# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Optional, Tuple, Union

from ._lapjvs import lapjvs_native as _lapjvs_native  # type: ignore
from ._lapjvs import lapjvs_float32 as _lapjvs_float32  # type: ignore
from ._lapjvs import lapjvsa_native as _lapjvsa_native  # type: ignore
from ._lapjvs import lapjvsa_float32 as _lapjvsa_float32  # type: ignore


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
    """
    This function wraps a high-performance JV solver and provides flexible
    I/O to match either lapjv-style vector outputs (x, y) or lapjvx/SciPy-style
    pair lists (rows, cols). It handles rectangular inputs by zero-padding to a
    square matrix internally when requested.

    Parameters
    ----------
    cost : np.ndarray, shape (n, m)
        The cost matrix. Must be 2D and a real floating dtype. Values are treated
        as minimization costs. Rectangular matrices are supported via internal
        zero-padding when `extend_cost=True` or `extend_cost=None and n != m`.
    extend_cost : Optional[bool], default None
        Controls how rectangular inputs are handled:
        - True: Always zero-pad to a square internally (if needed).
        - False: Require a square matrix, otherwise raise ValueError.
        - None: Auto mode; pad iff the input is rectangular.
    return_cost : bool, default True
        If True, include the total assignment cost as the first return value.
        The total is always recomputed from the ORIGINAL input array `cost`
        (float64 accumulation) to match previous numeric behavior.
    jvx_like : bool, default True
        Selects the output format.
        - True: Return lapjvx/SciPy-style indexing arrays:
            return_cost=True  -> (total_cost: float, rows: (k,), cols: (k,))
            return_cost=False -> (rows: (k,), cols: (k,))
          Here, `rows[i]` is assigned to `cols[i]`.
        - False: Return lapjv-style mapping vectors:
            return_cost=True  -> (total_cost: float, x: (n0,), y: (m0,))
            return_cost=False -> (x: (n0,), y: (m0,))
          `x[i]` gives the assigned column for row i or -1 if unassigned.
          `y[j]` gives the assigned row for column j or -1 if unassigned.
    prefer_float32 : bool, default True
        When True, the solver kernel runs in float32 to reduce memory bandwidth
        and improve speed. When False and the input is float64, the kernel runs
        in float64. Regardless of kernel dtype, the returned total cost is
        recomputed against the ORIGINAL `cost` array.

    Returns
    -------
    See `jvx_like` and `return_cost` above for exact signatures. In all cases,
    index arrays are int64 and refer to indices in the ORIGINAL orientation of
    `cost` (not the internally transposed one).

    Raises
    ------
    ValueError
        - If `cost` is not a 2D array.
        - If `extend_cost=False` and the input matrix is rectangular.

    Notes
    -----
    - Rectangular handling:
      Internally, the solver normalizes orientation so that the working matrix
      has rows <= cols. Rectangular problems are modeled by zero-padding on
      the right and/or bottom to become square. Only assignments within the
      original (n, m) region are returned and used for the total.
    - Dtype:
      The kernel may operate in float32 or float64, but accumulation for the
      returned total cost is performed in float64 on the ORIGINAL `cost`.
    """
    # Keep the original array to compute the final cost from it (preserves previous behavior)
    A = np.asarray(cost)
    if A.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n0, m0 = A.shape
    transposed = False

    # Normalize orientation for performance: let the kernel see rows <= cols.
    if n0 > m0:
        B = np.ascontiguousarray(A.T)
        transposed = True
    else:
        B = np.ascontiguousarray(A)

    n, m = B.shape
    extend = (n != m) if (extend_cost is None) else bool(extend_cost)

    # Choose backend and working dtype for the solver only
    use_float32_kernel = not ((prefer_float32 is False) and (B.dtype == np.float64))
    if use_float32_kernel:
        _kernel = _lapjvs_float32
        work_base = np.ascontiguousarray(B, dtype=np.float32)
    else:
        _kernel = _lapjvs_native
        work_base = np.ascontiguousarray(B, dtype=np.float64)

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

    if not extend:
        # Square: call solver directly on chosen dtype, compute total from ORIGINAL A
        if n != m:
            # Guard (per docstring): if extend_cost=False, require square input
            raise ValueError("extend_cost=False requires a square cost matrix")
        x_raw_obj, y_raw_obj = _kernel(work_base)

        x_raw_b = np.asarray(x_raw_obj, dtype=np.int64)

        if jvx_like:
            rows_a, cols_a = _rows_cols_from_x(x_raw_b)
            if return_cost:
                total = float(A[rows_a, cols_a].sum()) if rows_a.size else 0.0
                return total, rows_a, cols_a
            else:
                return rows_a, cols_a
        else:
            # Return vectors (x, y) in original orientation
            y_raw_b = np.asarray(y_raw_obj, dtype=np.int64)

            if not transposed:
                if return_cost:
                    total = float(A[np.arange(n), x_raw_b].sum()) if n > 0 else 0.0
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
                total = float(A[rows_a, cols_a].sum()) if rows_a.size else 0.0
                return total, x_out, y_out
            else:
                return x_out, y_out

    # Rectangular: zero-pad to square (in B space), solve, map back; compute total from ORIGINAL A
    size = max(n, m)
    padded = np.empty((size, size), dtype=work_base.dtype)
    # copy original submatrix
    padded[:n, :m] = work_base
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
        total = float(A[rows_a, cols_a].sum()) if (return_cost and rows_a.size) else 0.0
        return (total, rows_a, cols_a) if return_cost else (rows_a, cols_a)

    # lapjv-like outputs (vectorized) in ORIGINAL orientation
    x_out = np.full(n0, -1, dtype=np.int64)
    y_out = np.full(m0, -1, dtype=np.int64)
    if rows_a.size:
        x_out[rows_a] = cols_a
        y_out[cols_a] = rows_a

    if return_cost and rows_a.size:
        total = float(A[rows_a, cols_a].sum())
    else:
        total = 0.0

    return (total, x_out, y_out) if return_cost else (x_out, y_out)


def lapjvsa(
    cost: np.ndarray,
    extend_cost: Optional[bool] = None,
    return_cost: bool = True,
    prefer_float32: bool = True,
) -> Union[
    Tuple[float, np.ndarray],
    np.ndarray
]:
    """
    This variant returns a compact pairs array of shape (K, 2), where each row
    is a (row_index, col_index) assignment in the ORIGINAL orientation of the
    input matrix. Rectangular inputs are handled by internal zero-padding if
    requested.

    Parameters
    ----------
    cost : np.ndarray, shape (n, m)
        Cost matrix (float32/float64). Must be 2D.
    extend_cost : Optional[bool], default None
        Rectangular handling:
        - True: Zero-pad to square internally (if needed).
        - False: Require square, else raise ValueError.
        - None: Auto; pad iff rectangular.
    return_cost : bool, default True
        If True, include the total cost as the first return value. The total is
        computed from the ORIGINAL input matrix.
    prefer_float32 : bool, default True
        Hint to run the solver kernel in float32 for performance. When False and
        the input is float64, the kernel uses float64.

    Returns
    -------
    If return_cost is True:
        (total_cost: float, pairs: np.ndarray[int64] with shape (K, 2))
    Else:
        pairs: np.ndarray[int64] with shape (K, 2)

    Raises
    ------
    ValueError
        If `cost` is not 2D, or if `extend_cost=False` and `cost` is rectangular.

    Notes
    -----
    - Orientation is normalized internally so the kernel sees rows <= cols.
      Returned pairs are always mapped back to the ORIGINAL orientation.
    - Pairs only include assignments within the original (n, m) region for
      rectangular inputs.
    - Total is accumulated in float64 from the ORIGINAL `cost`.
    """
    A = np.asarray(cost)
    if A.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n0, m0 = A.shape
    transposed = False

    # Normalize orientation for performance
    if n0 > m0:
        B = np.ascontiguousarray(A.T)
        transposed = True
    else:
        B = np.ascontiguousarray(A)

    n, m = B.shape
    extend = (n != m) if (extend_cost is None) else bool(extend_cost)

    # Select dtype/backend
    use_f32 = not ((prefer_float32 is False) and (B.dtype == np.float64))
    wdtype = np.float32 if use_f32 else (B.dtype if B.dtype in (np.float32, np.float64) else np.float64)

    if not extend:
        if n != m:
            raise ValueError("extend_cost=False requires a square cost matrix")
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
                total = float(A[r, c].sum())
            else:
                total = 0.0
            return total, pairs_a
        return pairs_a

    # Rectangular: zero-pad in B space, solve, trim, map back to A
    size = max(n, m)
    padded = np.empty((size, size), dtype=wdtype)
    padded[:n, :m] = B.astype(wdtype, copy=False)
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
                total = float(A[pairs_a[:, 0], pairs_a[:, 1]].sum())
            else:
                total = 0.0
        else:
            pairs_a = np.empty((0, 2), dtype=np.int64)
            total = 0.0

    return (total, pairs_a) if return_cost else pairs_a
