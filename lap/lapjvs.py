# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Optional, Tuple

from ._lapjvs import lapjvs as _lapjvs_raw


def lapjvs(
    cost: np.ndarray,
    extend_cost: Optional[bool] = None,
    return_cost: bool = True,
    jvx_like: bool = True,
    prefer_float32: bool = False,
):
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

    Returns
    -------
    One of:
      - (cost, x, y)                   if return_cost and not jvx_like
      - (x, y)                         if not return_cost and not jvx_like
      - (cost, row_indices, col_indices) if return_cost and jvx_like
      - (row_indices, col_indices)     if not return_cost and jvx_like

      Where:
        - x: np.ndarray shape (n,), dtype=int. x[r] is assigned column for row r, or -1.
        - y: np.ndarray shape (m,), dtype=int. y[c] is assigned row for column c, or -1.
        - row_indices, col_indices: 1D int arrays of equal length K, listing matched (row, col) pairs.

    Notes
    -----
    - For square inputs without extension, this wraps the raw C function directly and adapts outputs.
    - For rectangular inputs, zero-padding exactly models the rectangular LAP.
    """
    a = np.asarray(cost)
    if a.ndim != 2:
        raise ValueError("cost must be a 2D array")

    if prefer_float32 and a.dtype != np.float32:
        a = a.astype(np.float32, copy=False)

    n, m = a.shape
    extend = (n != m) if (extend_cost is None) else bool(extend_cost)

    def _rows_cols_from_x(x_vec: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if x_vec.size == 0:
            return np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)
        mask = x_vec >= 0
        rows = np.nonzero(mask)[0]
        cols = x_vec[mask]
        return rows.astype(np.int64, copy=False), cols.astype(np.int64, copy=False)

    if not extend:
        total_raw, x_raw, y_raw = _lapjvs_raw(a)
        x_raw = np.asarray(x_raw, dtype=np.int64)
        y_raw = np.asarray(y_raw, dtype=np.int64)

        if jvx_like:
            rows, cols = _rows_cols_from_x(x_raw)
            if return_cost:
                total = float(a[np.arange(n), x_raw].sum()) if n > 0 else 0.0
                return total, rows, cols
            else:
                return rows, cols
        else:
            if return_cost:
                total = float(a[np.arange(n), x_raw].sum()) if n > 0 else 0.0
                return total, x_raw, y_raw
            else:
                return x_raw, y_raw

    # Rectangular: zero-pad to square, solve, then trim back
    size = max(n, m)
    padded = np.empty((size, size), dtype=a.dtype)
    padded[:n, :m] = a
    if m < size:
        padded[:n, m:] = 0
    if n < size:
        padded[n:, :] = 0

    total_pad, x_pad, y_pad = _lapjvs_raw(padded)
    x_pad = np.asarray(x_pad, dtype=np.int64)
    y_pad = np.asarray(y_pad, dtype=np.int64)

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

    # lapjv-like outputs
    tiny_threshold = 32
    if max(n, m) <= tiny_threshold:
        x_out = np.full(n, -1, dtype=np.int64)
        for r in range(n):
            c = int(cols_pad_n[r])
            if 0 <= c < m:
                x_out[r] = c

        y_out = np.full(m, -1, dtype=np.int64)
        rows_pad_m = y_pad[:m]
        for c in range(m):
            r = int(rows_pad_m[c])
            if 0 <= r < n:
                y_out[c] = r
    else:
        x_out = np.full(n, -1, dtype=np.int64)
        mask_r = (cols_pad_n >= 0) & (cols_pad_n < m)
        if mask_r.any():
            r_idx = np.nonzero(mask_r)[0]
            x_out[r_idx] = cols_pad_n[mask_r]

        y_out = np.full(m, -1, dtype=np.int64)
        rows_pad_m = y_pad[:m]
        mask_c = (rows_pad_m >= 0) & (rows_pad_m < n)
        if mask_c.any():
            c_idx = np.nonzero(mask_c)[0]
            y_out[c_idx] = rows_pad_m[mask_c]

    if return_cost and n > 0 and m > 0:
        mask = (x_out >= 0)
        total = float(a[np.nonzero(mask)[0], x_out[mask]].sum()) if mask.any() else 0.0
    else:
        total = 0.0

    return (total, x_out, y_out) if return_cost else (x_out, y_out)
