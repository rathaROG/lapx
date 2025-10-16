# _lapjvx.pyx | Wrote on 2025/10/16 by rathaROG

# The function lapjvx returns assignments as two parallel arrays 
# (row_indices, col_indices), so you can do: 
# np.array(list(zip(row_indices, col_indices))) 
# just like with scipy.optimize.linear_sum_assignment or lapjvc.

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

    Parameters
    ----------
    cost: (N, M) ndarray
        Cost matrix. Entry cost[i, j] is the cost of assigning row i to column j.
    extend_cost: bool, optional
        Whether or not to extend a non-square matrix. Default: False.
    cost_limit: double, optional
        An upper limit for a cost of a single assignment. Default: np.inf.
    return_cost: bool, optional
        Whether or not to return the assignment cost.

    Returns
    -------
    opt: double
        Assignment cost. Not returned if return_cost is False.
    row_indices: (K,) ndarray
        Indices of assigned rows.
    col_indices: (K,) ndarray
        Indices of assigned columns.

    Note
    ----
    The arrays row_indices and col_indices are parallel:
    row_indices[i] is assigned to col_indices[i].
    You can do: r = np.array(list(zip(row_indices, col_indices)))
    just like with scipy.optimize.linear_sum_assignment or lapjvc.
    """
    if cost.ndim != 2:
        raise ValueError('2-dimensional array expected')
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c = \
        np.ascontiguousarray(cost, dtype=np.double)
    cdef cnp.ndarray[cnp.double_t, ndim=2, mode='c'] cost_c_extended
    cdef uint_t n_rows = cost_c.shape[0]
    cdef uint_t n_cols = cost_c.shape[1]
    cdef uint_t n = 0
    if n_rows == n_cols:
        n = n_rows
    else:
        if not extend_cost:
            raise ValueError(
                'Square cost array expected. If cost is intentionally '
                'non-square, pass extend_cost=True.')
    if cost_limit < np.inf:
        n = n_rows + n_cols
        cost_c_extended = np.empty((n, n), dtype=np.double)
        cost_c_extended[:] = cost_limit / 2.
        cost_c_extended[n_rows:, n_cols:] = 0
        cost_c_extended[:n_rows, :n_cols] = cost_c
        cost_c = cost_c_extended
    elif extend_cost:
        n = max(n_rows, n_cols)
        cost_c_extended = np.zeros((n, n), dtype=np.double)
        cost_c_extended[:n_rows, :n_cols] = cost_c
        cost_c = cost_c_extended

    cdef double **cost_ptr
    cost_ptr = <double **> malloc(n * sizeof(double *))
    cdef int i
    for i in range(n):
        cost_ptr[i] = &cost_c[i, 0]

    cdef cnp.ndarray[int_t, ndim=1, mode='c'] x_c = \
        np.empty((n,), dtype=np.int32)
    cdef cnp.ndarray[int_t, ndim=1, mode='c'] y_c = \
        np.empty((n,), dtype=np.int32)

    cdef int ret = lapjv_internal(n, cost_ptr, &x_c[0], &y_c[0])
    free(cost_ptr)
    if ret != 0:
        if ret == -1:
            raise MemoryError('Out of memory.')
        raise RuntimeError('Unknown error (lapjv_internal returned %d).' % ret)

    cdef double opt = np.nan
    if cost_limit < np.inf or extend_cost:
        x_c[x_c >= n_cols] = -1
        y_c[y_c >= n_rows] = -1
        x_c = x_c[:n_rows]
        y_c = y_c[:n_cols]
        if return_cost:
            opt = cost_c[np.nonzero(x_c != -1)[0], x_c[x_c != -1]].sum()
    elif return_cost:
        opt = cost_c[np.arange(n_rows), x_c].sum()

    # Construct row_indices, col_indices - only for assigned rows
    assigned_mask = x_c >= 0
    row_indices = np.where(assigned_mask)[0]
    col_indices = x_c[assigned_mask]

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
    Like lapjvx, but returns assignment pairs as a (K,2) np.ndarray of (row, col).

    Returns
    -------
    opt : double
        Assignment cost. Not returned if return_cost is False.
    assignments : (K, 2) ndarray
        Each row is (row_index, col_index).
    """
    # We call lapjvx to get the indices
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
