# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, Optional, Tuple, Union

from ._lapjvs import lapjvs_native as _lapjvs_native  # type: ignore
from ._lapjvs import lapjvs_float32 as _lapjvs_float32  # type: ignore
from ._lapjvs import lapjvsa_native as _lapjvsa_native  # type: ignore
from ._lapjvs import lapjvsa_float32 as _lapjvsa_float32  # type: ignore


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjvs(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        return_cost: Literal[True] = True,
        jvx_like: bool = True,
        prefer_float32: bool = True,
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def lapjvs(
        cost: np.ndarray,
        extend_cost: Optional[bool],
        return_cost: Literal[False],
        jvx_like: bool = True,
        prefer_float32: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjvs(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        *,
        return_cost: Literal[False],
        jvx_like: bool = True,
        prefer_float32: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjvs(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        return_cost: bool = True,
        jvx_like: bool = True,
        prefer_float32: bool = True,
    ) -> Union[
        Tuple[float, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]: ...


def lapjvs(
    cost: np.ndarray,
    extend_cost: Optional[bool] = None,
    return_cost: bool = True,
    jvx_like: bool = True,
    prefer_float32: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray]
]:
    """Solve a linear assignment problem with a Jonker-Volgenant solver.

    The function returns mapping arrays (x, y), as in lapjv, or aligned index arrays
    (rows, cols), as in lapjvx and SciPy. When requested, it adds zeros to make
    rectangular inputs square.

    Parameters
    ----------
    cost : np.ndarray, shape (n, m)
        The cost matrix must be 2D with a real floating data type.
        The solver treats the values as costs to minimize.
        It pads rectangular inputs with zeros when extend_cost=True or
        when extend_cost=None and n != m.
    extend_cost : Optional[bool], default None
        This option controls padding for rectangular inputs:
        - True: Add zeros to make the matrix square, if necessary.
        - False: Require a square matrix. Otherwise, raise ValueError.
        - None: Add zeros if and only if the input is rectangular.
    return_cost : bool, default True
        If True, return the total assignment cost first.
        The solver always recalculates this total from the original cost array
        with float64 sums. This preserves the previous numerical behavior.
    jvx_like : bool, default True
        This option selects the output format:
        - True: Return aligned index arrays, as in lapjvx and SciPy:
            return_cost=True  -> (total_cost: float, rows: (k,), cols: (k,))
            return_cost=False -> (rows: (k,), cols: (k,))
          The solver assigns rows[i] to cols[i].
        - False: Return mapping arrays, as in lapjv:
            return_cost=True  -> (total_cost: float, x: (n0,), y: (m0,))
            return_cost=False -> (x: (n0,), y: (m0,))
          x[i] gives the assigned column for row i, or -1 if the row has no assignment.
          y[j] gives the assigned row for column j, or -1 if the column has no assignment.
    prefer_float32 : bool, default True
        If True, the kernel uses float32 to reduce memory bandwidth and improve speed.
        If False and the input is float64, the kernel uses float64.
        The solver recalculates the total from the original cost array,
        regardless of the kernel data type.

    Returns
    -------
    See jvx_like and return_cost above for the exact return formats.
    All index arrays use int64. Their indices refer to the original orientation
    of cost, before any internal transpose.

    Raises
    ------
    ValueError
        The function raises this exception in these cases:
        - cost is not a 2D array.
        - extend_cost=False and the input matrix is rectangular.
        - No feasible assignment exists.

    Notes
    -----
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver. Results with these
      values are undefined. Positive infinity can represent a forbidden assignment.
    - The solver adjusts the matrix orientation so the working matrix has rows <= cols.
      It pads the right, bottom, or both with zeros to make rectangular problems square.
      It returns only assignments within the original (n, m) region.
      It uses only these assignments for the total cost.
    - The kernel may use float32 or float64.
      The solver always sums total costs in float64 from the original cost array.
    """
    # Keep the original array to compute the final cost from it (preserves previous behavior)
    A = np.asarray(cost)
    if A.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n0, m0 = A.shape
    if extend_cost is not None and not extend_cost and n0 != m0:
        raise ValueError("extend_cost=False requires a square cost matrix")
    if n0 == 0 or m0 == 0:
        if jvx_like:
            x_out = np.empty((0,), dtype=np.int64)
            y_out = np.empty((0,), dtype=np.int64)
        else:
            x_out = np.full(n0, -1, dtype=np.int64)
            y_out = np.full(m0, -1, dtype=np.int64)
        return (0.0, x_out, y_out) if return_cost else (x_out, y_out)

    # Normalize orientation for performance: let the kernel see rows <= cols.
    # Keep a view until the final working buffer's dtype and shape are known.
    transposed = n0 > m0
    B = A.T if transposed else A
    n, m = B.shape

    # Choose backend and working dtype for the solver only
    use_float32_kernel = not ((prefer_float32 is False) and (B.dtype == np.float64))
    if use_float32_kernel:
        _kernel = _lapjvs_float32
        wdtype = np.float32
    else:
        _kernel = _lapjvs_native
        wdtype = np.float64

    def _rows_cols_from_x(x_vec: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if x_vec.size == 0:
            return np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)
        mask = x_vec >= 0
        rows_b = np.nonzero(mask)[0].astype(np.int64, copy=False)
        cols_b = x_vec[mask].astype(np.int64, copy=False)
        if not transposed:
            return rows_b, cols_b
        # Map back to original orientation (A): swap row/col
        return cols_b, rows_b

    if n == m:
        # Square: call solver directly on chosen dtype, compute total from ORIGINAL A
        work_base = np.ascontiguousarray(B, dtype=wdtype)
        x_raw_obj, y_raw_obj = _kernel(work_base)

        x_raw_b = np.asarray(x_raw_obj, dtype=np.int64)

        if jvx_like:
            rows_a, cols_a = _rows_cols_from_x(x_raw_b)
            if return_cost:
                total = float(A[rows_a, cols_a].sum(dtype=np.float64)) if rows_a.size else 0.0
                return total, rows_a, cols_a
            else:
                return rows_a, cols_a
        else:
            # Return vectors (x, y) in original orientation
            y_raw_b = np.asarray(y_raw_obj, dtype=np.int64)

            if not transposed:
                if return_cost:
                    total = float(A[np.arange(n), x_raw_b].sum(dtype=np.float64)) if n > 0 else 0.0
                    return total, x_raw_b, y_raw_b
                else:
                    return x_raw_b, y_raw_b

            # transposed square should not happen (n0==m0 implies no transpose), but keep safe mapping
            # Build pairs from B then map to A vectors
            rows_a, cols_a = _rows_cols_from_x(x_raw_b)
            x_out = np.full(n0, -1, dtype=np.int64)
            if rows_a.size:
                x_out[rows_a] = cols_a
            y_out = np.full(m0, -1, dtype=np.int64)
            if rows_a.size:
                y_out[cols_a] = rows_a
            if return_cost:
                total = float(A[rows_a, cols_a].sum(dtype=np.float64)) if rows_a.size else 0.0
                return total, x_out, y_out
            else:
                return x_out, y_out

    # Rectangular: zero-pad to square (in B space), solve, map back; compute total from ORIGINAL A
    size = max(n, m)
    padded = np.empty((size, size), dtype=wdtype)
    # Copy and cast directly into the final buffer, including for strided inputs.
    padded[:n, :m] = B
    if m < size:
        padded[:n, m:] = 0
    if n < size:
        padded[n:, :] = 0

    x_pad_obj, y_pad_obj = _kernel(padded)
    x_pad_b = np.asarray(x_pad_obj, dtype=np.int64)

    # Trim to original rectangle (B space), then map to A space if needed
    cols_pad_n = x_pad_b[:n]
    mask_r_b = (cols_pad_n >= 0) & (cols_pad_n < m)

    # Prepare pairs in A-space for convenience
    if mask_r_b.any():
        rows_b = np.nonzero(mask_r_b)[0].astype(np.int64, copy=False)
        cols_b = cols_pad_n[mask_r_b].astype(np.int64, copy=False)
        if transposed:
            rows_a = cols_b
            cols_a = rows_b
        else:
            rows_a = rows_b
            cols_a = cols_b
    else:
        rows_a = np.empty((0,), dtype=np.int64)
        cols_a = np.empty((0,), dtype=np.int64)

    if jvx_like:
        total = float(A[rows_a, cols_a].sum(dtype=np.float64)) if (return_cost and rows_a.size) else 0.0
        return (total, rows_a, cols_a) if return_cost else (rows_a, cols_a)

    # lapjv-like outputs (vectorized) in ORIGINAL orientation
    x_out = np.full(n0, -1, dtype=np.int64)
    y_out = np.full(m0, -1, dtype=np.int64)
    if rows_a.size:
        x_out[rows_a] = cols_a
        y_out[cols_a] = rows_a

    if return_cost and rows_a.size:
        total = float(A[rows_a, cols_a].sum(dtype=np.float64))
    else:
        total = 0.0

    return (total, x_out, y_out) if return_cost else (x_out, y_out)


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    @overload
    def lapjvsa(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        return_cost: Literal[True] = True,
        prefer_float32: bool = True,
    ) -> Tuple[float, np.ndarray]: ...

    @overload
    def lapjvsa(
        cost: np.ndarray,
        extend_cost: Optional[bool],
        return_cost: Literal[False],
        prefer_float32: bool = True,
    ) -> np.ndarray: ...

    @overload
    def lapjvsa(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        *,
        return_cost: Literal[False],
        prefer_float32: bool = True,
    ) -> np.ndarray: ...

    @overload
    def lapjvsa(
        cost: np.ndarray,
        extend_cost: Optional[bool] = None,
        return_cost: bool = True,
        prefer_float32: bool = True,
    ) -> Union[Tuple[float, np.ndarray], np.ndarray]: ...


def lapjvsa(
    cost: np.ndarray,
    extend_cost: Optional[bool] = None,
    return_cost: bool = True,
    prefer_float32: bool = True,
) -> Union[
    Tuple[float, np.ndarray],
    np.ndarray
]:
    """Return assignment pairs with shape (K, 2).

    Each row contains (row_index, col_index) in the original orientation of the
    input matrix. When requested, the solver pads rectangular inputs with zeros.

    Parameters
    ----------
    cost : np.ndarray, shape (n, m)
        The cost matrix must be 2D with data type float32 or float64.
    extend_cost : Optional[bool], default None
        This option controls padding for rectangular inputs:
        - True: Add zeros to make the matrix square, if necessary.
        - False: Require a square matrix. Otherwise, raise ValueError.
        - None: Add zeros if and only if the input is rectangular.
    return_cost : bool, default True
        If True, return the total cost first.
        The solver calculates this total from the original input matrix.
    prefer_float32 : bool, default True
        Request a float32 kernel for performance.
        If False and the input is float64, the kernel uses float64.

    Returns
    -------
    If return_cost is True:
        (total_cost: float, pairs: np.ndarray[int64] with shape (K, 2))
    Else:
        pairs: np.ndarray[int64] with shape (K, 2)

    Raises
    ------
    ValueError
        The function raises this exception in these cases:
        - cost is not a 2D array.
        - extend_cost=False and cost is rectangular.
        - No feasible assignment exists.

    Notes
    -----
    - The solver adjusts the matrix orientation so the kernel has rows <= cols.
      The returned pairs always use the original orientation.
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver. Results with these
      values are undefined. Positive infinity can represent a forbidden assignment.
    - For rectangular inputs, pairs contain only assignments within the original (n, m) region.
    - The solver sums total costs in float64 from the original cost array.
    """
    A = np.asarray(cost)
    if A.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n0, m0 = A.shape
    if extend_cost is not None and not extend_cost and n0 != m0:
        raise ValueError("extend_cost=False requires a square cost matrix")
    if n0 == 0 or m0 == 0:
        pairs = np.empty((0, 2), dtype=np.int64)
        return (0.0, pairs) if return_cost else pairs

    # Normalize orientation for performance
    transposed = n0 > m0
    B = A.T if transposed else A
    n, m = B.shape

    # Select dtype/backend
    use_f32 = not ((prefer_float32 is False) and (B.dtype == np.float64))
    wdtype = np.float32 if use_f32 else (B.dtype if B.dtype in (np.float32, np.float64) else np.float64)

    if n == m:
        work = np.ascontiguousarray(B, dtype=wdtype)
        pairs_b_obj = (_lapjvsa_float32(work) if use_f32 else _lapjvsa_native(work))
        pairs_b = np.asarray(pairs_b_obj, dtype=np.int64)

        # Map pairs back to original orientation
        if transposed and pairs_b.size:
            pairs_a = pairs_b[:, ::-1].astype(np.int64, copy=False)
        else:
            pairs_a = pairs_b

        if return_cost:
            if pairs_a.size:
                r = pairs_a[:, 0]; c = pairs_a[:, 1]
                total = float(A[r, c].sum(dtype=np.float64))
            else:
                total = 0.0
            return total, pairs_a
        return pairs_a

    # Rectangular: zero-pad in B space, solve, trim, map back to A
    size = max(n, m)
    padded = np.empty((size, size), dtype=wdtype)
    padded[:n, :m] = B
    if m < size:
        padded[:n, m:] = 0
    if n < size:
        padded[n:, :] = 0

    pairs_pad_b_obj = (_lapjvsa_float32(padded) if use_f32 else _lapjvsa_native(padded))
    pairs_pad_b = np.asarray(pairs_pad_b_obj, dtype=np.int64)

    if pairs_pad_b.size == 0 or n == 0 or m == 0:
        pairs_a = np.empty((0, 2), dtype=np.int64)
        total = 0.0
    else:
        r_b = pairs_pad_b[:, 0]
        c_b = pairs_pad_b[:, 1]
        mask_b = (r_b >= 0) & (r_b < n) & (c_b >= 0) & (c_b < m)
        if mask_b.any():
            pairs_b = np.stack([r_b[mask_b], c_b[mask_b]], axis=1).astype(np.int64, copy=False)
            # Map back to A orientation if needed
            pairs_a = pairs_b[:, ::-1] if transposed else pairs_b
            if return_cost and pairs_a.size:
                total = float(A[pairs_a[:, 0], pairs_a[:, 1]].sum(dtype=np.float64))
            else:
                total = 0.0
        else:
            pairs_a = np.empty((0, 2), dtype=np.int64)
            total = 0.0

    return (total, pairs_a) if return_cost else pairs_a
