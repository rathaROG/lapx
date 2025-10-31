# Tomas Kazmar, 2012-2017, BSD 2-clause license, see LICENSE.

# Updated by rathaROG
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
    """
    Solve the Linear Assignment Problem using the Jonker-Volgenant (JV) algorithm.

    Orientation is normalized internally for performance: the native kernel
    always sees rows <= cols by transposing when N_rows > N_cols, and results
    are mapped back to the original (row, col) orientation before returning.

    Parameters
    ----------
    cost : (N, M) ndarray
        Cost matrix. Entry cost[i, j] is the cost of assigning row i to column j.
        Any float dtype is accepted; a contiguous float64 working buffer is used only if needed.
    extend_cost : bool, optional (default: False)
        Whether to permit non-square inputs via zero-padding to a square matrix.
        See the unified augmentation policy below.
    cost_limit : float, optional (default: np.inf)
        If finite, augment to an (N+M) x (N+M) matrix with sentinel costs
        cost_limit/2 and a 0 block in the bottom-right. This models per-edge
        reject costs and allows rectangular inputs even when extend_cost=False.
    return_cost : bool, optional (default: True)
        Whether to return the total assignment cost as the first return value.

    Returns
    -------
    opt : float
        Total assignment cost (only if return_cost=True). The total is computed
        from the ORIGINAL input array shape (N, M), not the padded/augmented one.
    x : (N,) ndarray of int32
        x[i] = assigned column index for row i, or -1 if unassigned.
    y : (M,) ndarray of int32
        y[j] = assigned row index for column j, or -1 if unassigned.

    Unified augmentation policy
    ---------------------------
    - If cost_limit < inf: always augment to (N+M) to model per-edge rejects.
      Rectangular inputs are allowed regardless of extend_cost.
    - Else if (N != M) or extend_cost=True: zero-pad to a square of size max(N, M).
      Rectangular inputs are allowed when extend_cost=True.
    - Else (square, un-augmented): run on the given square matrix.

    Notes
    -----
    - Single contiguous working buffer: we reuse the input when it's already
      float64 C-contiguous and no transpose is needed; otherwise we materialize
      exactly one contiguous float64 working array (or its transpose).
    - For zero-sized dimensions, the solver returns 0.0 (if requested) and
      all -1 mappings with appropriate lengths.
    """
    if cost.ndim != 2:
        raise ValueError('2-dimensional array expected')

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
    cdef bint transposed = False
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] B
    if n_rows0 > n_cols0:
        B = np.ascontiguousarray(A.T, dtype=np.double)  # single working buffer (transposed)
        transposed = True
    else:
        if A.dtype == np.float64 and A.flags['C_CONTIGUOUS']:
            # reuse input buffer directly
            B = A
        else:
            B = np.ascontiguousarray(A, dtype=np.double)  # single working buffer

    cdef Py_ssize_t R = B.shape[0]  # working rows (<= cols)
    cdef Py_ssize_t C = B.shape[1]  # working cols

    # Permit rectangular when cost_limit < inf (augment) or extend_cost=True (zero-pad); otherwise require square
    if R != C and (not extend_cost) and cost_limit == np.inf:
        raise ValueError(
            'Square cost array expected. If cost is intentionally '
            'non-square, pass extend_cost=True or set a finite cost_limit.'
        )

    cdef uint_t N
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c = B
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c_extended

    if cost_limit < np.inf:
        # Augment to (R+C)x(R+C) with sentinel edges
        N = <uint_t>(R + C)
        cost_c_extended = np.empty((R + C, R + C), dtype=np.double)
        cost_c_extended[:] = cost_limit / 2.0
        cost_c_extended[R:, C:] = 0.0
        cost_c_extended[:R, :C] = cost_c
        cost_c = cost_c_extended
    elif R != C or extend_cost:
        # Zero-pad to square max(R, C); if already square and extend_cost=True, keep as-is
        N = <uint_t>max(R, C)
        if R != C:
            cost_c_extended = np.zeros((N, N), dtype=np.double)
            cost_c_extended[:R, :C] = cost_c
            cost_c = cost_c_extended
        else:
            N = <uint_t>R
    else:
        # Square, un-augmented
        N = <uint_t>R

    # Build row-pointer view for kernel
    cdef double **cost_ptr = <double **> malloc(N * sizeof(double *))
    if cost_ptr == NULL:
        raise MemoryError('Out of memory.')
    cdef int i
    for i in range(N):
        cost_ptr[i] = &cost_c[i, 0]

    # Outputs for kernel space (size N)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = np.empty((N,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = np.empty((N,), dtype=np.int32)

    cdef int ret
    with nogil:
        ret = lapjv_internal(N, cost_ptr, &x_c[0], &y_c[0])
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
    x_out = np.full((n_rows0,), -1, dtype=np.int32)
    y_out = np.full((n_cols0,), -1, dtype=np.int32)

    if not transposed:
        mask = (x_trim >= 0)
        if np.any(mask):
            rows = np.nonzero(mask)[0]
            cols = x_trim[mask]
            x_out[rows] = cols
            y_out[cols] = rows
    else:
        # B rows are A columns; B cols are A rows
        mask = (x_trim >= 0)
        if np.any(mask):
            rows_b = np.nonzero(mask)[0]        # indices in B rows -> A columns
            cols_b = x_trim[mask]               # indices in B cols -> A rows
            row_A = cols_b
            col_A = rows_b
            x_out[row_A] = col_A
            y_out[col_A] = row_A

    # Total from ORIGINAL A
    cdef double opt = 0.0
    if return_cost:
        mcost = (x_out >= 0)
        if np.any(mcost):
            rr = np.nonzero(mcost)[0]
            cc = x_out[mcost]
            opt = float(A[rr, cc].sum())
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
    """Internal function called from lapmod(..., fast=True)."""
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

    cdef int_t ret = lapmod_internal(n, &cc_c[0], &ii_c[0], &kk_c[0], 
                                     &x_c[0], &y_c[0], fp_version)
    if ret != 0:
        if ret == -1:
            raise MemoryError('Out of memory.')
        raise RuntimeError('Unknown error (lapmod_internal returned %d).' % ret)

    return x_c, y_c
