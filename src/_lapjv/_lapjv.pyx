# Tomas Kazmar, 2012-2017, BSD 2-clause license, see LICENSE.

# Updated by rathaROG
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
    int lapmod_internal(const uint_t n,
                        double *cc,
                        uint_t *ii,
                        uint_t *kk,
                        int_t *x,
                        int_t *y,
                        fp_t fp_version)

LARGE_ = LARGE
FP_1_ = FP_1
FP_2_ = FP_2
FP_DYNAMIC_ = FP_DYNAMIC


# Improved efficiency by raphaelreme
# https://github.com/rathaROG/lapx/pull/7

@cython.boundscheck(False)
@cython.wraparound(False)
def lapjv(cnp.ndarray cost not None, char extend_cost=False,
          double cost_limit=np.inf, char return_cost=True):
    """Solve the linear assignment problem with the Jonker-Volgenant (JV) algorithm.

    For performance, the solver transposes inputs when N_rows > N_cols.
    The native kernel always has rows <= cols.
    The returned results use the original (row, col) orientation.

    Parameters
    ----------
    cost : (N, M) ndarray
        The cost matrix. Entry cost[i, j] gives the cost to assign row i to column j.
        The solver accepts any floating data type.
        It uses a contiguous float64 working buffer only when necessary.
    extend_cost : bool, optional (default: False)
        Permit rectangular inputs through zero-padding to a square matrix.
        See the matrix extension rules below.
    cost_limit : float, optional (default: np.inf)
        If finite, the solver extends the matrix to shape (N+M, N+M).
        The added edges have cost_limit/2 costs, with a zero block at the bottom right.
        This models a reject cost for each edge.
        It permits rectangular inputs even when extend_cost=False.
    return_cost : bool, optional (default: True)
        This option controls whether the function returns the total assignment cost first.

    Returns
    -------
    opt : float
        The total assignment cost, only if return_cost=True.
        The solver calculates it from the original input array with shape (N, M),
        before any padding or matrix extension.
    x : (N,) ndarray of int32
        x[i] gives the assigned column for row i, or -1 if the row has no assignment.
    y : (M,) ndarray of int32
        y[j] gives the assigned row for column j, or -1 if the column has no assignment.

    Matrix extension rules
    ----------------------
    - If cost_limit < inf, extend the matrix to size (N+M) to model reject costs for each edge.
      This permits rectangular inputs regardless of extend_cost.
    - Otherwise, if N != M or extend_cost=True, add zeros to make a square of size max(N, M).
      This permits rectangular inputs when extend_cost=True.
    - Otherwise, solve the original square matrix without extension.

    Notes
    -----
    - The solver reuses the input if it is float64, is C-contiguous, and needs no transpose.
      Otherwise, it creates exactly one contiguous float64 working array or its transpose.
    - For a zero-sized dimension, the solver returns 0.0 if return_cost=True.
      All mapping entries have value -1, with the appropriate array lengths.
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver.
      Results with these values are undefined.
      Positive infinity can represent a forbidden assignment.
    """
    if cost.ndim != 2:
        raise ValueError('2-dimensional array expected')
    if isnan(cost_limit) or cost_limit == -INFINITY:
        raise ValueError('cost_limit must be finite or positive infinity')

    # Original input for final total computation (no copy unless necessary for transpose below)
    A = np.asarray(cost)
    cdef Py_ssize_t n_rows0 = A.shape[0]
    cdef Py_ssize_t n_cols0 = A.shape[1]

    # Fast exits for empty dimensions
    if n_rows0 == 0 or n_cols0 == 0:
        if return_cost:
            return 0.0, np.full((n_rows0,), -1, dtype=np.int32), np.full((n_cols0,), -1, dtype=np.int32)
        else:
            return np.full((n_rows0,), -1, dtype=np.int32), np.full((n_cols0,), -1, dtype=np.int32)

    # Normalize orientation: kernel sees rows <= cols
    cdef bint transposed = n_rows0 > n_cols0
    # Keep a view until the final buffer's shape is known, then copy/cast once.
    B = A.T if transposed else A

    cdef Py_ssize_t R = B.shape[0]  # working rows (<= cols)
    cdef Py_ssize_t C = B.shape[1]  # working cols

    # Permit rectangular when cost_limit < inf (augment) or extend_cost=True (zero-pad); otherwise require square
    if R != C and (not extend_cost) and cost_limit == np.inf:
        raise ValueError(
            'Square cost array expected. If cost is intentionally '
            'non-square, pass extend_cost=True or set a finite cost_limit.'
        )

    cdef Py_ssize_t size = R + C if cost_limit < INFINITY else C
    if size > INT_MAX:
        raise ValueError('Cost matrix is too large for int32 indices')
    cdef uint_t N = <uint_t>size
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c

    if cost_limit < np.inf:
        # Augment to (R+C)x(R+C) with sentinel edges
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

    # Allocate Python-owned outputs before allocating the row pointers.
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = np.empty((N,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = np.empty((N,), dtype=np.int32)

    # Build row-pointer view for kernel
    cdef double **cost_ptr = <double **> malloc(N * sizeof(double *))
    if cost_ptr == NULL:
        raise MemoryError('Out of memory.')
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

    # Trim to working rectangle (B space) and clean artificial matches
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

    # Map to ORIGINAL orientation (A space) as vectors x_out (N_rows0), y_out (N_cols0)
    # Both inverse mappings already exist; transpose only swaps their roles.
    # Copy trimmed arrays so a large augmented output is not retained.
    x_out = y_trim.copy() if transposed else x_trim.copy()
    y_out = x_trim.copy() if transposed else y_trim.copy()

    # Total from ORIGINAL A
    cdef double opt = 0.0
    if return_cost:
        mcost = (x_out >= 0)
        if np.any(mcost):
            rr = np.nonzero(mcost)[0]
            cc = x_out[mcost]
            opt = float(A[rr, cc].sum(dtype=np.float64))
        else:
            opt = 0.0

    if return_cost:
        return opt, x_out, y_out
    else:
        return x_out, y_out


@cython.boundscheck(False)
@cython.wraparound(False)
def _lapmod(const uint_t n,
            cnp.ndarray cc not None,
            cnp.ndarray ii not None,
            cnp.ndarray kk not None,
            fp_t fp_version=FP_DYNAMIC):
    """lapmod(..., fast=True) calls this internal function."""
    cdef cnp.ndarray[cnp.double_t, ndim=1, mode='c'] cc_c = \
        np.ascontiguousarray(cc, dtype=np.double)
    cdef cnp.ndarray[uint_t, ndim=1, mode='c'] ii_c = \
        np.ascontiguousarray(ii, dtype=np.uint32)
    cdef cnp.ndarray[uint_t, ndim=1, mode='c'] kk_c = \
        np.ascontiguousarray(kk, dtype=np.uint32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = \
        np.empty((n,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = \
        np.empty((n,), dtype=np.int32)

    cdef int_t ret
    with nogil:
        ret = lapmod_internal(n, &cc_c[0], &ii_c[0], &kk_c[0],
                              &x_c[0], &y_c[0], fp_version)
    if ret != 0:
        if ret == -1:
            raise MemoryError('Out of memory.')
        if ret == -2:
            raise ValueError('Unknown fp_version')
        raise RuntimeError('Unknown error (lapmod_internal returned %d).' % ret)

    return x_c, y_c
