# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Optional, Tuple, Union

from ._lapjvs import lapjvs_native as _lapjvs_native
from ._lapjvs import lapjvs_float32 as _lapjvs_float32
from ._lapjvs import lapjvsa_native as _lapjvsa_native
from ._lapjvs import lapjvsa_float32 as _lapjvsa_float32


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
    Solve the Linear Assignment Problem using the 'lapjvs' algorithm.

    - Accepts rectangular cost matrices (pad to square internally).
    - Returns lapjv-like (x,y) or jvx-like (rows, cols).
    - Optional prefer_float32 to reduce memory bandwidth.

    Parameters
    ----------
    cost : np.ndarray
        Cost matrix of shape (n, m). dtype should be a floating type.
    extend_cost : Optional[bool]
        If True, treat rectangular inputs by extending (zero-padding) to square.
        If False, require square input.
        If None (default), auto-detect: extend if n != m.
    return_cost : bool
        If True (default), return total cost as the first element of the return tuple.
    jvx_like : bool
        If False (default), return lapjv-style mapping vectors:
          - return_cost=True  -> (total_cost, x, y)
          - return_cost=False -> (x, y)
        If True, return lapjvx/SciPy-style arrays:
          - return_cost=True  -> (total_cost, row_indices, col_indices)
          - return_cost=False -> (row_indices, col_indices)

    Notes
    -----
    - The solver kernel may run in float32 (when prefer_float32=True) or native float64,
      but the returned total cost is always recomputed from the ORIGINAL input array
      to preserve previous numeric behavior and parity with lapjv/lapjvx.
    - For rectangular inputs, zero-padding exactly models the rectangular LAP.
    """
    # Keep the original array to compute the final cost from it (preserves previous behavior)
    a = np.asarray(cost)
    if a.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n, m = a.shape
    extend = (n != m) if (extend_cost is None) else bool(extend_cost)

    # Choose backend and working dtype for the solver only (ensure contiguity to avoid hidden copies)
    use_float32_kernel = not ((prefer_float32 is False) and (a.dtype == np.float64))
    if use_float32_kernel:
        # Run float32 kernel (casting as needed)
        _kernel = _lapjvs_float32
        work = np.ascontiguousarray(a, dtype=np.float32)
    else:
        # Run native kernel on float64 inputs
        _kernel = _lapjvs_native
        work = np.ascontiguousarray(a, dtype=np.float64)

    def _rows_cols_from_x(x_vec: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if x_vec.size == 0:
            return np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)
        mask = x_vec >= 0
        rows = np.nonzero(mask)[0]
        cols = x_vec[mask]
        return rows.astype(np.int64, copy=False), cols.astype(np.int64, copy=False)

    if not extend:
        # Square: call solver directly on chosen dtype, but compute total from ORIGINAL array
        x_raw_obj, y_raw_obj = _kernel(work)

        # Convert only what's needed; y conversion deferred if not used
        x_raw = np.asarray(x_raw_obj, dtype=np.int64)

        if jvx_like:
            rows, cols = _rows_cols_from_x(x_raw)
            if return_cost:
                total = float(a[np.arange(n), x_raw].sum()) if n > 0 else 0.0
                return total, rows, cols
            else:
                return rows, cols
        else:
            y_raw = np.asarray(y_raw_obj, dtype=np.int64)
            if return_cost:
                total = float(a[np.arange(n), x_raw].sum()) if n > 0 else 0.0
                return total, x_raw, y_raw
            else:
                return x_raw, y_raw

    # Rectangular: zero-pad to square, solve, then trim back; compute total from ORIGINAL array
    size = max(n, m)
    padded = np.empty((size, size), dtype=work.dtype)
    padded[:n, :m] = work
    if m < size:
        padded[:n, m:] = 0
    if n < size:
        padded[n:, :] = 0

    x_pad_obj, y_pad_obj = _kernel(padded)
    x_pad = np.asarray(x_pad_obj, dtype=np.int64)
    cols_pad_n = x_pad[:n]

    if jvx_like:
        if n == 0 or m == 0:
            rows = np.empty((0,), dtype=np.int64)
            cols = np.empty((0,), dtype=np.int64)
            total = 0.0
        else:
            mask_r = (cols_pad_n >= 0) & (cols_pad_n < m)
            rows = np.nonzero(mask_r)[0].astype(np.int64, copy=False)
            cols = cols_pad_n[mask_r].astype(np.int64, copy=False)
            total = float(a[rows, cols].sum()) if (return_cost and rows.size) else 0.0

        return (total, rows, cols) if return_cost else (rows, cols)

    # lapjv-like outputs (vectorized)
    x_out = np.full(n, -1, dtype=np.int64)
    mask_r = (cols_pad_n >= 0) & (cols_pad_n < m)
    if mask_r.any():
        x_out[mask_r] = cols_pad_n[mask_r]

    y_pad = np.asarray(y_pad_obj, dtype=np.int64)
    rows_pad_m = y_pad[:m]
    y_out = np.full(m, -1, dtype=np.int64)
    mask_c = (rows_pad_m >= 0) & (rows_pad_m < n)
    if mask_c.any():
        y_out[mask_c] = rows_pad_m[mask_c]

    if return_cost and n > 0 and m > 0:
        mask = (x_out >= 0)
        total = float(a[np.nonzero(mask)[0], x_out[mask]].sum()) if mask.any() else 0.0
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
    Solve LAP using the 'lapjvs' algorithm (pairs API).

    - Accepts rectangular cost matrices (pads to square internally when needed).
    - Returns pairs array (K, 2) int64 with optional total cost (computed from ORIGINAL input).
    """
    a = np.asarray(cost)
    if a.ndim != 2:
        raise ValueError("cost must be a 2D array")

    n, m = a.shape
    extend = (n != m) if (extend_cost is None) else bool(extend_cost)

    if not extend:
        # Square: call native pairs entry point on chosen dtype
        use_f32 = not ((prefer_float32 is False) and (a.dtype == np.float64))
        if use_f32:
            pairs_obj = _lapjvsa_float32(np.ascontiguousarray(a, dtype=np.float32))
        else:
            # Follow native dtype; if a is float32 or float64, both ok
            # Ensure contiguous to avoid hidden copies
            work = np.ascontiguousarray(a, dtype=a.dtype if a.dtype in (np.float32, np.float64) else np.float64)
            pairs_obj = _lapjvsa_native(work)
        pairs = np.asarray(pairs_obj, dtype=np.int64)

        if return_cost:
            if pairs.size:
                r = pairs[:, 0]; c = pairs[:, 1]
                total = float(a[r, c].sum())
            else:
                total = 0.0
            return total, pairs
        return pairs

    # Rectangular: zero-pad to square, solve pairs on padded, map back, compute total from ORIGINAL
    size = max(n, m)
    use_f32 = not ((prefer_float32 is False) and (a.dtype == np.float64))
    wdtype = np.float32 if use_f32 else (a.dtype if a.dtype in (np.float32, np.float64) else np.float64)
    padded = np.empty((size, size), dtype=wdtype)
    # copy original submatrix
    padded[:n, :m] = a.astype(wdtype, copy=False)
    if m < size:
        padded[:n, m:] = 0
    if n < size:
        padded[n:, :] = 0

    # Solve pairs on the padded square matrix
    if use_f32:
        pairs_pad_obj = _lapjvsa_float32(padded)
    else:
        pairs_pad_obj = _lapjvsa_native(padded)
    pairs_pad = np.asarray(pairs_pad_obj, dtype=np.int64)

    # Trim pairs to original rectangle
    if pairs_pad.size == 0 or n == 0 or m == 0:
        pairs = np.empty((0, 2), dtype=np.int64)
        total = 0.0
    else:
        r = pairs_pad[:, 0]
        c = pairs_pad[:, 1]
        mask = (r >= 0) & (r < n) & (c >= 0) & (c < m)
        if mask.any():
            pairs = np.stack([r[mask], c[mask]], axis=1).astype(np.int64, copy=False)
            total = float(a[pairs[:, 0], pairs[:, 1]].sum()) if return_cost else 0.0
        else:
            pairs = np.empty((0, 2), dtype=np.int64)
            total = 0.0

    return (total, pairs) if return_cost else pairs
