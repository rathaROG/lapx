# Copyright (c) 2026 Ratha SIV | MIT License
# cython: language_level=3, embedsignature=True

import os
import sys
import numpy as np
cimport numpy as cnp
from libc.stdint cimport int64_t
from libc.stddef cimport size_t
from libc.limits cimport INT_MAX
from libc.float cimport FLT_MAX
from libc.math cimport isfinite, isnan, INFINITY

cdef extern from "lapjvr.h" nogil:
    int lapjvr_run(const void*, int, const void*, int, size_t, size_t,
                  size_t, double, size_t, int, int, int, int, int64_t*, size_t*,
                  double*, size_t*)


cdef cnp.ndarray _checked_float32(cnp.ndarray original):
    """Cast aligned, contiguous float64 costs without full-size temporaries.

    Check the original value before conversion: otherwise finite overflow
    becomes positive infinity and silently turns a usable edge into a forbidden
    one. Genuine infinities retain the existing input contract.
    """
    cdef cnp.ndarray converted = np.empty_like(original, dtype=np.float32)
    cdef const double* source = <const double*>cnp.PyArray_DATA(original)
    cdef float* destination = <float*>cnp.PyArray_DATA(converted)
    cdef Py_ssize_t i, count = cnp.PyArray_SIZE(original)
    cdef double value
    cdef bint overflow = False
    with nogil:
        for i in range(count):
            value = source[i]
            # Most costs are in range. Only outliers need the infinity check.
            if (value > FLT_MAX or value < -FLT_MAX) and isfinite(value):
                overflow = True
                break
            destination[i] = <float>value
    if overflow:
        raise ValueError("Finite costs overflow float32; use precision='float64'")
    return converted


cdef object _solve(object costs, bint batch, bint extend_cost, double limit,
                   bint return_cost, object n_threads, object precision,
                   object output, bint hybrid=False):
    # An ordinary ndarray already has the semantics of np.asarray. Avoid its
    # Python call for the common case; subclasses and other inputs still use it.
    cdef cnp.ndarray a = costs if cnp.PyArray_CheckExact(costs) else np.asarray(costs)
    cdef cnp.ndarray original, work, result, counts, totals
    cdef cnp.npy_intp result_shape[2]
    cdef Py_ssize_t b, n, m, k, i, count
    cdef size_t workers, failed = 0
    cdef size_t single_count = 0
    cdef double single_total = 0.0
    cdef size_t* count_ptr
    cdef double* total_ptr
    cdef int status, cost32, original32, pairs, input_type
    cdef int automatic = 0
    if a.ndim != (3 if batch else 2):
        raise ValueError("3-dimensional array expected [B, N, M]" if batch else "2-dimensional array expected")
    if isnan(limit) or limit == -INFINITY:
        raise ValueError("cost_limit must be finite or positive infinity")
    if precision not in ("native", "float32", "float64"):
        raise ValueError("precision must be 'native', 'float32', or 'float64'")
    if output not in ("indices", "pairs"):
        raise ValueError("output must be 'indices' or 'pairs'")
    input_type = cnp.PyArray_TYPE(a)
    if (input_type != cnp.NPY_FLOAT32 and input_type != cnp.NPY_FLOAT64
            and a.dtype.kind not in 'biuf'):
        raise TypeError("costs must contain real numeric values")
    b = a.shape[0] if batch else 1
    n = a.shape[1] if batch else a.shape[0]
    m = a.shape[2] if batch else a.shape[1]
    k = min(n, m)
    # Validate dimensions before any conversion of broadcast/strided input.
    if n > INT_MAX or m > INT_MAX:
        raise ValueError("Cost matrix is too large for int32 internal indices")
    if k and b > sys.maxsize // (2 * k * 8):
        raise ValueError("Batch output is too large")
    if n and m and b > sys.maxsize // n // m // 8:
        raise ValueError("Batch input is too large")
    if batch:
        # Match existing conversions, but retain automatic mode separately.
        automatic = n_threads is None or n_threads == 0
        if automatic:
            workers = min(max(1, int(os.cpu_count() or 1)), max(1, b))
        else:
            workers = min(max(1, int(n_threads)), max(1, b))
    else:
        workers = 1
    if b and k and n != m and not extend_cost and not isfinite(limit):
        raise ValueError("Square cost array expected; pass extend_cost=True for rectangular costs")
    pairs = output == "pairs"
    if k == 0 or b == 0:
        if batch:
            if pairs:
                arrays = [np.empty((0, 2), dtype=np.int64) for _ in range(b)]
                return (np.zeros(b), arrays) if return_cost else arrays
            rows = [np.empty(0, dtype=np.int64) for _ in range(b)]
            cols = [np.empty(0, dtype=np.int64) for _ in range(b)]
            return (np.zeros(b), rows, cols) if return_cost else (rows, cols)
        if pairs:
            empty = np.empty((0, 2), dtype=np.int64)
            return (0.0, empty) if return_cost else empty
        rows = np.empty(0, dtype=np.int64)
        cols = np.empty(0, dtype=np.int64)
        return (0.0, rows, cols) if return_cost else (rows, cols)

    # Hold both NumPy owners until the native call finishes. Callers must not
    # mutate or resize costs (including aliases) concurrently with a solve.
    if ((input_type == cnp.NPY_FLOAT32 or input_type == cnp.NPY_FLOAT64)
            and cnp.PyArray_ISCARRAY_RO(a) and cnp.PyArray_ISNOTSWAPPED(a)):
        original = a
    else:
        original = np.ascontiguousarray(a, dtype=np.float32 if input_type == cnp.NPY_FLOAT32 else np.float64)
        if not cnp.PyArray_ISALIGNED(original):
            original = original.copy()
    original32 = cnp.PyArray_TYPE(original) == cnp.NPY_FLOAT32
    cost32 = precision == "float32" or (precision == "native" and original32)
    if cost32 and isfinite(limit) and abs(limit) > 3.4028234663852886e38:
        raise ValueError("cost_limit overflows float32; use precision='float64'")
    if cost32 == original32:
        work = original
    elif cost32:
        work = _checked_float32(original)
    else:
        work = np.ascontiguousarray(original, dtype=np.float64)
    if batch:
        result_shape[0], result_shape[1] = b, 2 * k
        result = cnp.PyArray_SimpleNew(2, result_shape, cnp.NPY_INT64)
        counts = np.empty(b, dtype=np.uintp)
        totals = np.empty(b, dtype=np.float64)
        count_ptr = <size_t*>cnp.PyArray_DATA(counts)
        total_ptr = <double*>cnp.PyArray_DATA(totals)
    else:
        if pairs:
            result_shape[0], result_shape[1] = k, 2
            result = cnp.PyArray_SimpleNew(2, result_shape, cnp.NPY_INT64)
        else:
            result_shape[0] = 2 * k
            result = cnp.PyArray_SimpleNew(1, result_shape, cnp.NPY_INT64)
        count_ptr = &single_count
        total_ptr = &single_total
    with nogil:
        status = lapjvr_run(cnp.PyArray_DATA(work), cost32,
                            cnp.PyArray_DATA(original), original32,
                            b, n, m, limit, workers, automatic, pairs, return_cost, hybrid,
                            <int64_t*>cnp.PyArray_DATA(result),
                            count_ptr, total_ptr, &failed)
    if status:
        suffix = " at batch index %d" % failed if batch else ""
        if status == 1:
            raise ValueError("Cost matrix is infeasible or its reduced costs overflow" + suffix)
        if status == 2:
            raise MemoryError("Unable to allocate Rust solver workspace or workers" + suffix)
        if status == 4:
            raise ValueError("Cost matrix dimensions exceed native limits" + suffix)
        if status == 5:
            raise RuntimeError("LAPJVH requires a build with C++ completion support")
        raise RuntimeError("Rust solver failed internally" + suffix)
    if batch:
        # A successful required solve matches k pairs in every problem. With a
        # finite limit, check only where the reduction costs less than slicing.
        # Tiny batches slice faster than they build the intermediate views.
        if b >= 8 and (not isfinite(limit) or (b >= 32 and counts.min() == k)):
            # Row iteration builds the same views in C instead of slicing
            # each problem from Python.
            if pairs:
                arrays = list(result.reshape((b, k, 2)))
                return (totals, arrays) if return_cost else arrays
            rows = list(result[:, :k])
            cols = list(result[:, k:])
            return (totals, rows, cols) if return_cost else (rows, cols)
        # Convert the counts once; indexing a NumPy array per item boxes a scalar.
        sizes = counts.tolist()
        if pairs:
            arrays = [result[i].reshape((k, 2))[:sizes[i]] for i in range(b)]
            return (totals, arrays) if return_cost else arrays
        rows = [result[i, :sizes[i]] for i in range(b)]
        cols = [result[i, k:k + sizes[i]] for i in range(b)]
        return (totals, rows, cols) if return_cost else (rows, cols)
    count = single_count
    if pairs:
        array = result if count == k else result[:count]
        return (single_total, array) if return_cost else array
    rows = result[:count]
    cols = result[k:k + count]
    return (single_total, rows, cols) if return_cost else (rows, cols)


def lapjvr(cost, extend_cost=False, double cost_limit=np.inf,
           return_cost=True, *, precision="native", output="indices"):
    """Solve the linear assignment problem with the Jonker-Volgenant algorithm.

    The function returns aligned (rows, cols) index arrays. Use output='pairs'
    for assignment pairs with shape (K, 2). If return_cost is True, return the
    total assignment cost first.

    Parameters
    ----------
    cost : array_like, shape (N, M)
        A 2D cost matrix with real numeric values. The solver accepts array-like
        inputs and may copy them for layout or precision conversion.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        Permit rectangular inputs when cost_limit is infinite. Rectangular
        problems use a native path without padding to a square matrix. A finite
        cost_limit permits rectangular inputs regardless of this option.
    cost_limit : float, default np.inf
        The value must be finite or positive infinity. A finite limit permits
        unmatched rows and columns, each charged cost_limit / 2 during
        optimization. The returned total excludes these penalties. Negative finite
        limits are allowed. With np.inf, each problem requires min(N, M) matches.
    return_cost : bool, default True
        If True, return the total assignment cost first.
        The solver sums this total in float64 from the selected original input
        costs, before any float32 conversion. If False, return only indices or
        pairs and skip the total-cost sum.
    precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
        Select the working cost precision. 'native' preserves float32/float64
        inputs and uses float64 for other real numeric inputs. Explicit
        'float32' or 'float64' converts the working costs. Finite costs and
        limits must fit the selected float32 range when float32 is used.
    output : {'indices', 'pairs'}, keyword-only, default 'indices'
        'indices' returns aligned row and column index arrays. 'pairs' returns
        an array with shape (K, 2), where each row contains
        (row_index, column_index).

    Returns
    -------
    total_cost : float, optional
        Returned first only if return_cost is True. The total sums selected
        original input costs and excludes unmatched penalties.
    rows, cols : np.ndarray, shape (K,), dtype int64
        Returned if output='indices'. Each rows[i] is matched to cols[i].
        The row indices are sorted in increasing order, and both arrays refer to
        the original cost matrix.
    pairs : np.ndarray, shape (K, 2), dtype int64
        Returned instead of rows and cols if output='pairs'. Each row contains
        (row_index, column_index), with pairs sorted by row index.
        K is at most min(N, M); finite limits can choose fewer matches. An empty
        matrix dimension returns arrays with K=0 and total cost 0.0.

    Raises
    ------
    TypeError
        cost has a non-real numeric dtype, such as complex, object, or string.
    ValueError
        The input is not 2D, a nonempty rectangle is disallowed, an option or
        limit is invalid, float32 conversion overflows, dimensions exceed
        native limits, required matches are infeasible, or reduced costs
        overflow.
    MemoryError
        An input copy, output array, or native workspace cannot be allocated.
    RuntimeError
        An internal native solver error occurs.

    Notes
    -----
    LAPJVR uses Rust for required square completion. Rectangular and
    finite-limit problems use native Rust paths without square padding.

    All paths use float64 potentials, distances, and reduced-cost arithmetic,
    including with float32 cost storage. Finite-limit half-penalties and their
    sum retain rounding in the selected cost precision before promotion.
    Float64 working arithmetic reduces cancellation, but extreme cost ranges
    can still obscure small objective differences. It does not provide
    arbitrary-range exactness or restore costs rounded during conversion.
    A finite limit optimizes rejection jointly with matching; it is not
    equivalent to filtering a required solution after solving. Equal-cost
    optima can produce different assignments across solvers or precisions.

    Suitable contiguous arrays are borrowed, and the native solve releases
    the GIL. Other inputs may be copied for layout or precision conversion.
    Do not mutate or resize the input or any alias until the call returns.

    See Also
    --------
    lapjvh : The other completion strategy with the same input/output contract.
    lapjvr_batch : Solve a batch with reusable native workers.

    Examples
    --------
    >>> import lap
    >>> import numpy as np
    >>> cost = np.array([[3.0, 1.0], [1.0, 4.0]])
    >>> total, rows, cols = lap.lapjvr(cost)
    >>> total, rows.tolist(), cols.tolist()
    (2.0, [0, 1], [1, 0])
    >>> lap.lapjvr(cost, return_cost=False, output='pairs').tolist()
    [[0, 1], [1, 0]]
    """
    return _solve(cost, False, extend_cost, cost_limit, return_cost, 1, precision, output)


def lapjvr_batch(costs, extend_cost=False, double cost_limit=np.inf,
                 return_cost=True, n_threads=0, *, precision="native",
                 output="indices"):
    """Solve a batch of cost matrices with lapjvr.

    It runs lapjvr on each (N, M) slice of the (B, N, M) batch.
    It keeps the input order and supports execution with multiple threads.
    Use output='pairs' for a list of arrays of assignment pairs.

    Parameters
    ----------
    costs : array_like, shape (B, N, M)
        A batch of cost matrices with real numeric values.
        Each costs[b] contains one assignment problem. The solver accepts
        array-like inputs and may copy them for layout or precision conversion.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        Permit rectangular inputs when cost_limit is infinite. Rectangular
        problems use a native path without padding to a square matrix. A finite
        cost_limit permits rectangular inputs regardless of this option.
    cost_limit : float, default np.inf
        The value must be finite or positive infinity. A finite limit permits
        unmatched rows and columns, each charged cost_limit / 2 during
        optimization. The returned totals exclude these penalties. Negative finite
        limits are allowed. With np.inf, each problem requires min(N, M) matches.
    return_cost : bool, default True
        If True, return the array of total costs first.
        The solver sums each total in float64 from the selected original input
        costs, before any float32 conversion. If False, return only index lists
        or pair lists and skip the total-cost sums.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        One worker or at most one problem runs serially. Automatic mode may also
        run small workloads serially. Otherwise, the solver reuses native worker
        pools. Explicit positive values are not capped by the CPU count.
    precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
        Select the working cost precision. 'native' preserves float32/float64
        inputs and uses float64 for other real numeric inputs. Explicit
        'float32' or 'float64' converts the working costs. Finite costs and
        limits must fit the selected float32 range when float32 is used.
    output : {'indices', 'pairs'}, keyword-only, default 'indices'
        'indices' returns two lists of aligned row and column index arrays.
        'pairs' returns one list of arrays with shape (K_b, 2), where each row
        contains (row_index, column_index).

    Returns
    -------
    totals : np.ndarray, shape (B,), dtype float64, optional
        Returned first only if return_cost is True. Each entry gives the total
        cost for one original cost matrix, excluding unmatched penalties.
    rows_list, cols_list : list of np.ndarray
        Returned if output='indices'. Each list has length B. Entry b has
        shape (K_b,) and dtype int64, with row indices sorted in increasing order.
        rows_list[b][i] is matched to cols_list[b][i] in the original cost matrix.
    pairs_list : list of np.ndarray
        Returned instead of the two index lists if output='pairs'. The list has
        length B. Entry b has shape (K_b, 2) and dtype int64. Each row contains
        (row_index, column_index), with pairs sorted by row index.
        K_b is at most min(N, M); finite limits can choose fewer matches.
        An empty batch returns empty lists and, when requested, an empty totals
        array. An empty matrix dimension returns empty assignments and zero
        totals for each problem.

    Raises
    ------
    TypeError
        costs has a non-real numeric dtype, or n_threads cannot be interpreted
        as an integer.
    ValueError
        The input is not 3D, nonempty rectangles are disallowed, options or
        thread counts are invalid, float32 conversion overflows, dimensions
        exceed native limits, required matches are infeasible, or reduced
        costs overflow. Native solver failures identify the lowest failing
        batch index; no partial batch result is returned.
    MemoryError
        Input copies, outputs, native workspaces, or workers cannot be allocated.
    RuntimeError
        An internal native solver error occurs.

    Notes
    -----
    LAPJVR uses Rust for required square completion. Rectangular and
    finite-limit problems use native Rust paths without square padding.

    All paths use float64 potentials, distances, and reduced-cost arithmetic,
    including with float32 cost storage. Finite-limit half-penalties and their
    sum retain rounding in the selected cost precision before promotion.
    Float64 working arithmetic reduces cancellation, but extreme cost ranges
    can still obscure small objective differences. It does not provide
    arbitrary-range exactness or restore costs rounded during conversion.
    Finite limits optimize rejection jointly with matching; they are not
    equivalent to filtering required solutions after solving. Equal-cost
    optima can produce different assignments across solvers or precisions.

    Suitable contiguous arrays are borrowed, and the native solve releases
    the GIL. Other inputs may be copied for layout or precision conversion.
    Do not mutate or resize the input or any alias until the call returns.

    Both families share reusable native worker pools and workspaces. Calls may
    run concurrently, and each call keeps its own completion strategy. Avoid
    oversubscribing CPU cores with concurrent large batches. Use process
    spawning instead of forking after native worker pools have initialized.

    See Also
    --------
    lapjvr : Solve one matrix with the same precision and output options.
    lapjvh_batch : The other completion strategy with the same batch contract.

    Examples
    --------
    >>> import lap
    >>> import numpy as np
    >>> costs = np.array([[[3.0, 1.0], [1.0, 4.0]],
    ...                   [[4.0, 2.0], [3.0, 6.0]]])
    >>> totals, rows, cols = lap.lapjvr_batch(costs, n_threads=2)
    >>> totals.tolist()
    [2.0, 5.0]
    >>> [r.tolist() for r in rows]
    [[0, 1], [0, 1]]
    >>> pairs = lap.lapjvr_batch(costs, return_cost=False,
    ...                              output='pairs', n_threads=2)
    >>> [p.tolist() for p in pairs]
    [[[0, 1], [1, 0]], [[0, 1], [1, 0]]]
    """
    return _solve(costs, True, extend_cost, cost_limit, return_cost, n_threads, precision, output)


def lapjvh(cost, extend_cost=False, double cost_limit=np.inf,
           return_cost=True, *, precision="native", output="indices"):
    """Solve the linear assignment problem with the Jonker-Volgenant algorithm.

    The function returns aligned (rows, cols) index arrays. Use output='pairs'
    for assignment pairs with shape (K, 2). If return_cost is True, return the
    total assignment cost first.

    Parameters
    ----------
    cost : array_like, shape (N, M)
        A 2D cost matrix with real numeric values. The solver accepts array-like
        inputs and may copy them for layout or precision conversion.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        Permit rectangular inputs when cost_limit is infinite. Rectangular
        problems use a native path without padding to a square matrix. A finite
        cost_limit permits rectangular inputs regardless of this option.
    cost_limit : float, default np.inf
        The value must be finite or positive infinity. A finite limit permits
        unmatched rows and columns, each charged cost_limit / 2 during
        optimization. The returned total excludes these penalties. Negative finite
        limits are allowed. With np.inf, each problem requires min(N, M) matches.
    return_cost : bool, default True
        If True, return the total assignment cost first.
        The solver sums this total in float64 from the selected original input
        costs, before any float32 conversion. If False, return only indices or
        pairs and skip the total-cost sum.
    precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
        Select the working cost precision. 'native' preserves float32/float64
        inputs and uses float64 for other real numeric inputs. Explicit
        'float32' or 'float64' converts the working costs. Finite costs and
        limits must fit the selected float32 range when float32 is used.
    output : {'indices', 'pairs'}, keyword-only, default 'indices'
        'indices' returns aligned row and column index arrays. 'pairs' returns
        an array with shape (K, 2), where each row contains
        (row_index, column_index).

    Returns
    -------
    total_cost : float, optional
        Returned first only if return_cost is True. The total sums selected
        original input costs and excludes unmatched penalties.
    rows, cols : np.ndarray, shape (K,), dtype int64
        Returned if output='indices'. Each rows[i] is matched to cols[i].
        The row indices are sorted in increasing order, and both arrays refer to
        the original cost matrix.
    pairs : np.ndarray, shape (K, 2), dtype int64
        Returned instead of rows and cols if output='pairs'. Each row contains
        (row_index, column_index), with pairs sorted by row index.
        K is at most min(N, M); finite limits can choose fewer matches. An empty
        matrix dimension returns arrays with K=0 and total cost 0.0.

    Raises
    ------
    TypeError
        cost has a non-real numeric dtype, such as complex, object, or string.
    ValueError
        The input is not 2D, a nonempty rectangle is disallowed, an option or
        limit is invalid, float32 conversion overflows, dimensions exceed
        native limits, required matches are infeasible, or reduced costs
        overflow.
    MemoryError
        An input copy, output array, or native workspace cannot be allocated.
    RuntimeError
        C++ completion is unavailable, or an internal native error occurs.

    Notes
    -----
    LAPJVH uses Rust initialization/reduction and C++ completion for
    required square problems. Rectangular and finite-limit problems use
    the same native Rust paths as LAPJVR, without square padding.

    All paths use float64 potentials, distances, and reduced-cost arithmetic,
    including with float32 cost storage. Finite-limit half-penalties and their
    sum retain rounding in the selected cost precision before promotion.
    Float64 working arithmetic reduces cancellation, but extreme cost ranges
    can still obscure small objective differences. It does not provide
    arbitrary-range exactness or restore costs rounded during conversion.
    A finite limit optimizes rejection jointly with matching; it is not
    equivalent to filtering a required solution after solving. Equal-cost
    optima can produce different assignments across solvers or precisions.

    Suitable contiguous arrays are borrowed, and the native solve releases
    the GIL. Other inputs may be copied for layout or precision conversion.
    Do not mutate or resize the input or any alias until the call returns.

    See Also
    --------
    lapjvr : The other completion strategy with the same input/output contract.
    lapjvh_batch : Solve a batch with reusable native workers.

    Examples
    --------
    >>> import lap
    >>> import numpy as np
    >>> cost = np.array([[3.0, 1.0], [1.0, 4.0]])
    >>> total, rows, cols = lap.lapjvh(cost)
    >>> total, rows.tolist(), cols.tolist()
    (2.0, [0, 1], [1, 0])
    >>> lap.lapjvh(cost, return_cost=False, output='pairs').tolist()
    [[0, 1], [1, 0]]
    """
    return _solve(cost, False, extend_cost, cost_limit, return_cost, 1, precision, output, True)


def lapjvh_batch(costs, extend_cost=False, double cost_limit=np.inf,
                 return_cost=True, n_threads=0, *, precision="native",
                 output="indices"):
    """Solve a batch of cost matrices with lapjvh.

    It runs lapjvh on each (N, M) slice of the (B, N, M) batch.
    It keeps the input order and supports execution with multiple threads.
    Use output='pairs' for a list of arrays of assignment pairs.

    Parameters
    ----------
    costs : array_like, shape (B, N, M)
        A batch of cost matrices with real numeric values.
        Each costs[b] contains one assignment problem. The solver accepts
        array-like inputs and may copy them for layout or precision conversion.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        Permit rectangular inputs when cost_limit is infinite. Rectangular
        problems use a native path without padding to a square matrix. A finite
        cost_limit permits rectangular inputs regardless of this option.
    cost_limit : float, default np.inf
        The value must be finite or positive infinity. A finite limit permits
        unmatched rows and columns, each charged cost_limit / 2 during
        optimization. The returned totals exclude these penalties. Negative finite
        limits are allowed. With np.inf, each problem requires min(N, M) matches.
    return_cost : bool, default True
        If True, return the array of total costs first.
        The solver sums each total in float64 from the selected original input
        costs, before any float32 conversion. If False, return only index lists
        or pair lists and skip the total-cost sums.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        One worker or at most one problem runs serially. Automatic mode may also
        run small workloads serially. Otherwise, the solver reuses native worker
        pools. Explicit positive values are not capped by the CPU count.
    precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
        Select the working cost precision. 'native' preserves float32/float64
        inputs and uses float64 for other real numeric inputs. Explicit
        'float32' or 'float64' converts the working costs. Finite costs and
        limits must fit the selected float32 range when float32 is used.
    output : {'indices', 'pairs'}, keyword-only, default 'indices'
        'indices' returns two lists of aligned row and column index arrays.
        'pairs' returns one list of arrays with shape (K_b, 2), where each row
        contains (row_index, column_index).

    Returns
    -------
    totals : np.ndarray, shape (B,), dtype float64, optional
        Returned first only if return_cost is True. Each entry gives the total
        cost for one original cost matrix, excluding unmatched penalties.
    rows_list, cols_list : list of np.ndarray
        Returned if output='indices'. Each list has length B. Entry b has
        shape (K_b,) and dtype int64, with row indices sorted in increasing order.
        rows_list[b][i] is matched to cols_list[b][i] in the original cost matrix.
    pairs_list : list of np.ndarray
        Returned instead of the two index lists if output='pairs'. The list has
        length B. Entry b has shape (K_b, 2) and dtype int64. Each row contains
        (row_index, column_index), with pairs sorted by row index.
        K_b is at most min(N, M); finite limits can choose fewer matches.
        An empty batch returns empty lists and, when requested, an empty totals
        array. An empty matrix dimension returns empty assignments and zero
        totals for each problem.

    Raises
    ------
    TypeError
        costs has a non-real numeric dtype, or n_threads cannot be interpreted
        as an integer.
    ValueError
        The input is not 3D, nonempty rectangles are disallowed, options or
        thread counts are invalid, float32 conversion overflows, dimensions
        exceed native limits, required matches are infeasible, or reduced
        costs overflow. Native solver failures identify the lowest failing
        batch index; no partial batch result is returned.
    MemoryError
        Input copies, outputs, native workspaces, or workers cannot be allocated.
    RuntimeError
        C++ completion is unavailable, or an internal native error occurs.

    Notes
    -----
    LAPJVH uses Rust initialization/reduction and C++ completion for
    required square problems. Rectangular and finite-limit problems use
    the same native Rust paths as LAPJVR, without square padding.

    All paths use float64 potentials, distances, and reduced-cost arithmetic,
    including with float32 cost storage. Finite-limit half-penalties and their
    sum retain rounding in the selected cost precision before promotion.
    Float64 working arithmetic reduces cancellation, but extreme cost ranges
    can still obscure small objective differences. It does not provide
    arbitrary-range exactness or restore costs rounded during conversion.
    Finite limits optimize rejection jointly with matching; they are not
    equivalent to filtering required solutions after solving. Equal-cost
    optima can produce different assignments across solvers or precisions.

    Suitable contiguous arrays are borrowed, and the native solve releases
    the GIL. Other inputs may be copied for layout or precision conversion.
    Do not mutate or resize the input or any alias until the call returns.

    Both families share reusable native worker pools and workspaces. Calls may
    run concurrently, and each call keeps its own completion strategy. Avoid
    oversubscribing CPU cores with concurrent large batches. Use process
    spawning instead of forking after native worker pools have initialized.

    See Also
    --------
    lapjvh : Solve one matrix with the same precision and output options.
    lapjvr_batch : The other completion strategy with the same batch contract.

    Examples
    --------
    >>> import lap
    >>> import numpy as np
    >>> costs = np.array([[[3.0, 1.0], [1.0, 4.0]],
    ...                   [[4.0, 2.0], [3.0, 6.0]]])
    >>> totals, rows, cols = lap.lapjvh_batch(costs, n_threads=2)
    >>> totals.tolist()
    [2.0, 5.0]
    >>> [r.tolist() for r in rows]
    [[0, 1], [0, 1]]
    >>> pairs = lap.lapjvh_batch(costs, return_cost=False,
    ...                              output='pairs', n_threads=2)
    >>> [p.tolist() for p in pairs]
    [[[0, 1], [1, 0]], [[0, 1], [1, 0]]]
    """
    return _solve(costs, True, extend_cost, cost_limit, return_cost, n_threads, precision, output, True)
