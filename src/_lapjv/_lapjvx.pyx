# _lapjvx.pyx | Wrote on 2025/10/16 by rathaROG

# lapjvx returns assignments as two arrays: (row_indices, col_indices)
# Combine them with:
#   assignments = np.column_stack((row_indices, col_indices))  # fast!
# Or:
#   assignments = np.array(list(zip(row_indices, col_indices)))  # works too
# Same as scipy.optimize.linear_sum_assignment.

# cython: language_level=3
# cython: embedsignature=True

import numpy as np
cimport numpy as cnp
cimport cython

from libc.stdlib cimport malloc, free
from libc.limits cimport INT_MAX
from libc.math cimport isnan, INFINITY

cdef extern from "lapjv.h" nogil:
    ctypedef signed int int_t
    ctypedef unsigned int uint_t
    cdef int LARGE
    cdef enum fp_t:
        FP_1
        FP_2
        FP_DYNAMIC
    int lapjv_internal(const uint_t n,
                       double *cost[],
                       int_t *x,
                       int_t *y)

@cython.boundscheck(False)
@cython.wraparound(False)
def lapjvx(cnp.ndarray cost not None, char extend_cost=False,
           double cost_limit=np.inf, char return_cost=True):
    """Solve the linear assignment problem with the Jonker-Volgenant algorithm.

    The function returns (row_indices, col_indices), as in
    scipy.optimize.linear_sum_assignment.
    The solver adjusts the matrix orientation so the kernel has rows <= cols.
    The returned results use the original orientation.

    Matrix extension rules
    ----------------------
    - If cost_limit < inf, extend the matrix to size (N+M) with cost_limit/2 costs on added edges.
      This permits rectangular inputs.
    - Otherwise, if N != M or extend_cost=True, add zeros to make a square of size max(N, M).
      This permits rectangular inputs when extend_cost=True.
    - Otherwise, solve the original square matrix without extension.

    The solver does not check for NaN (not a number) or negative infinity.
    Check or remove these values before you call the solver.
    Results with these values are undefined.
    Positive infinity can represent a forbidden assignment.

    Returns
    -------
    opt : float
        The total cost, if return_cost=True.
        The solver calculates it from the original input, before padding.
    row_indices : (K,) ndarray (np.where -> int64)
    col_indices : (K,) ndarray (sliced from x_c -> int32)
    """
    if cost.ndim != 2:
        raise ValueError('2-dimensional array expected')
    if isnan(cost_limit) or cost_limit == -INFINITY:
        raise ValueError('cost_limit must be finite or positive infinity')

    # Original input for final total (no copy unless needed for transpose)
    A = np.asarray(cost)
    cdef Py_ssize_t n_rows0 = A.shape[0]
    cdef Py_ssize_t n_cols0 = A.shape[1]

    # Fast exits for empty dims
    if n_rows0 == 0 or n_cols0 == 0:
        if return_cost:
            return 0.0, np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)
        else:
            return np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)

    # Normalize orientation: kernel sees rows <= cols
    cdef bint transposed = n_rows0 > n_cols0
    # Copy/cast directly into the final padded or augmented buffer.
    B = A.T if transposed else A

    cdef Py_ssize_t R = B.shape[0]
    cdef Py_ssize_t C = B.shape[1]

    # Gate: rectangular error only if extend_cost=False and cost_limit==inf
    if R != C and (not extend_cost) and cost_limit == np.inf:
        raise ValueError(
            'Square cost array expected. If cost is intentionally '
            'non-square, pass extend_cost=True.'
        )

    cdef Py_ssize_t size = R + C if cost_limit < INFINITY else C
    if size > INT_MAX:
        raise ValueError('Cost matrix is too large for int32 indices')
    cdef uint_t N = <uint_t>size
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c

    if cost_limit < np.inf:
        cost_c = np.empty((N, N), dtype=np.double)
        cost_c[:R, C:] = cost_limit / 2.0
        cost_c[R:, :C] = cost_limit / 2.0
        cost_c[R:, C:] = 0.0
        cost_c[:R, :C] = B
    elif R != C:
        cost_c = np.empty((N, N), dtype=np.double)
        cost_c[:R, :C] = B
        cost_c[R:, :] = 0.0
    else:
        cost_c = np.ascontiguousarray(B, dtype=np.double)

    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = np.empty((N,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = np.empty((N,), dtype=np.int32)

    # Build row-pointer view
    cdef double **cost_ptr = <double **> malloc(N * sizeof(double *))
    if cost_ptr == NULL:
        raise MemoryError('Out of memory when allocating cost_ptr')
    cdef int i
    cdef int ret
    try:
        with nogil:
            for i in range(N):
                cost_ptr[i] = &cost_c[i, 0]
            ret = lapjv_internal(N, cost_ptr, &x_c[0], &y_c[0])
    finally:
        free(cost_ptr)
    if ret != 0:
        if ret == -1:
            raise MemoryError('Out of memory.')
        raise RuntimeError('Unknown error (lapjv_internal returned %d).' % ret)

    # Trim to working rectangle (B-space) and clean artificial matches
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_trim
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_trim

    if cost_limit < np.inf or (R != C or extend_cost):
        x_c[x_c >= C] = -1
        y_c[y_c >= R] = -1
        x_trim = x_c[:R]
        y_trim = y_c[:C]
    else:
        x_trim = x_c[:R]
        y_trim = y_c[:C]

    # Build rows/cols in ORIGINAL orientation (A-space)
    mask = x_trim >= 0
    rows_b = np.nonzero(mask)[0].astype(np.int64, copy=False)
    cols_b = x_trim[mask]  # keep int32 dtype

    if transposed:
        row_indices = cols_b
        col_indices = rows_b
    else:
        row_indices = rows_b
        col_indices = cols_b

    cdef double opt = 0.0
    if return_cost:
        if row_indices.size:
            opt = float(A[row_indices, col_indices].sum(dtype=np.float64))
        else:
            opt = 0.0

    if return_cost:
        return opt, row_indices, col_indices
    else:
        return row_indices, col_indices


# The function lapjvxa is a wrapper of lapjvx which returns 
# assignment pairs as a (K,2) np.ndarray of (row, col).

@cython.boundscheck(False)
@cython.wraparound(False)
def lapjvxa(cnp.ndarray cost not None, char extend_cost=False,
            double cost_limit=np.inf, char return_cost=True):
    """Solve with lapjvx and return (row, col) pairs in an array with shape (K, 2).

    The pairs use int32 to preserve the previous behavior.
    """
    if return_cost:
        opt, row_indices, col_indices = lapjvx(cost, extend_cost=extend_cost,
                                               cost_limit=cost_limit, return_cost=True)
        assignments = np.empty((row_indices.shape[0], 2), dtype=np.int32)
        assignments[:, 0] = row_indices
        assignments[:, 1] = col_indices
        return opt, assignments
    else:
        row_indices, col_indices = lapjvx(cost, extend_cost=extend_cost,
                                          cost_limit=cost_limit, return_cost=False)
        assignments = np.empty((row_indices.shape[0], 2), dtype=np.int32)
        assignments[:, 0] = row_indices
        assignments[:, 1] = col_indices
        return assignments
