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
    """
    Solve linear assignment problem using Jonker-Volgenant algorithm,
    returning (row_indices, col_indices) like scipy.optimize.linear_sum_assignment.

    Orientation is normalized internally (kernel sees rows <= cols) and results
    are mapped back to the original orientation.

    Unified augmentation policy
    ---------------------------
    - If cost_limit < inf: augment to (N+M) with cost_limit/2 sentinels (rectangular allowed).
    - Elif (N != M) or extend_cost: zero-pad to square max(N, M) (rectangular allowed when extend_cost=True).
    - Else (square, un-augmented): run on the given square.

    Returns
    -------
    opt : float
        Total cost (if return_cost=True), computed on the ORIGINAL input (not padded).
    row_indices : (K,) ndarray (np.where -> int64)
    col_indices : (K,) ndarray (sliced from x_c -> int32)
    """
    if cost.ndim != 2:
        raise ValueError('2-dimensional array expected')

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
    cdef bint transposed = False
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] B
    if n_rows0 > n_cols0:
        B = np.ascontiguousarray(A.T, dtype=np.double)  # single working buffer (transposed)
        transposed = True
    else:
        if A.dtype == np.float64 and A.flags['C_CONTIGUOUS']:
            B = A  # reuse input buffer
        else:
            B = np.ascontiguousarray(A, dtype=np.double)  # single working buffer

    cdef Py_ssize_t R = B.shape[0]
    cdef Py_ssize_t C = B.shape[1]

    # Gate: rectangular error only if extend_cost=False and cost_limit==inf
    if R != C and (not extend_cost) and cost_limit == np.inf:
        raise ValueError(
            'Square cost array expected. If cost is intentionally '
            'non-square, pass extend_cost=True.'
        )

    cdef uint_t N
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c = B
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c_extended

    if cost_limit < np.inf:
        N = <uint_t>(R + C)
        cost_c_extended = np.empty((R + C, R + C), dtype=np.double)
        cost_c_extended[:] = cost_limit / 2.0
        cost_c_extended[R:, C:] = 0.0
        cost_c_extended[:R, :C] = cost_c
        cost_c = cost_c_extended
    elif R != C or extend_cost:
        N = <uint_t>max(R, C)
        if R != C:
            cost_c_extended = np.zeros((N, N), dtype=np.double)
            cost_c_extended[:R, :C] = cost_c
            cost_c = cost_c_extended
        else:
            N = <uint_t>R
    else:
        N = <uint_t>R

    # Build row-pointer view
    cdef double **cost_ptr = <double **> malloc(N * sizeof(double *))
    if cost_ptr == NULL:
        raise MemoryError('Out of memory when allocating cost_ptr')
    cdef int i
    for i in range(N):
        cost_ptr[i] = &cost_c[i, 0]

    # Allocate x/y
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = np.empty((N,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = np.empty((N,), dtype=np.int32)

    cdef int ret
    with nogil:
        ret = lapjv_internal(<uint_t> N, cost_ptr, &x_c[0], &y_c[0])

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
    rows_b = np.nonzero(x_trim >= 0)[0].astype(np.int64, copy=False)
    cols_b = x_trim[x_trim >= 0]  # keep int32 dtype

    if transposed:
        row_indices = cols_b
        col_indices = rows_b
    else:
        row_indices = rows_b
        col_indices = cols_b

    cdef double opt = 0.0
    if return_cost:
        if row_indices.size:
            opt = float(A[row_indices, col_indices].sum())
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
    """
    Like lapjvx, but returns assignment pairs as a (K,2) ndarray of (row, col).
    Uses int32 pairs to match legacy behavior.
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
