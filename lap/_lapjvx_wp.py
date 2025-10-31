# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Tuple, Union

from ._lapjvx import lapjvx as _lapjvx  # type: ignore
from ._lapjvx import lapjvxa as _lapjvxa  # type: ignore


def lapjvx(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """
    Solve the Linear Assignment Problem using the Jonker-Volgenant algorithm,
    returning (row_indices, col_indices) like scipy.optimize.linear_sum_assignment.

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        2D cost matrix. Any float dtype is accepted; internally a single contiguous
        float64 working buffer is used when required.
    extend_cost : bool, default False
        Permit rectangular inputs by zero-padding to a square matrix.
    cost_limit : float, default np.inf
        If finite, augment to size (N+M) with sentinel edges of cost_limit/2 and a
        bottom-right zero block, modeling a per-edge reject cost (allows rectangular inputs).
    return_cost : bool, default True
        If True, include total assignment cost first (computed on the ORIGINAL input).

    Returns
    -------
    If return_cost is True:
        total_cost : float
        row_indices : np.ndarray with shape (K,), dtype int64
            Row indices of selected assignments (in original orientation).
        col_indices : np.ndarray with shape (K,), typically dtype int32
            Column indices corresponding to row_indices.
    Else:
        row_indices, col_indices

    Notes
    -----
    - Orientation is normalized internally so the native kernel sees rows <= cols;
      indices are mapped back to the ORIGINAL orientation on return.
    - Dtypes of the returned indices follow the Cython implementation:
      row_indices as int64, col_indices often int32 (subject to NumPy/platform).
    - Unified augmentation policy:
        * cost_limit < inf: augment to (N+M) (rectangular allowed).
        * elif (N != M) or extend_cost: zero-pad to square max(N, M).
        * else: run on the given square matrix.
    """
    return _lapjvx(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)


def lapjvxa(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray],
    np.ndarray,
]:
    """
    Like lapjvx, but returns assignment pairs as a compact (K, 2) ndarray of (row, col).

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        2D cost matrix.
    extend_cost : bool, default False
        Permit rectangular inputs by zero-padding to a square matrix.
    cost_limit : float, default np.inf
        When finite, augment to (N+M) to model per-edge reject cost (see lapjvx).
    return_cost : bool, default True
        If True, include the total cost as the first element.

    Returns
    -------
    If return_cost is True:
        total_cost : float
        assignments : np.ndarray with shape (K, 2), dtype int32
            Each row is (row_index, col_index) in the ORIGINAL orientation.
    Else:
        assignments : np.ndarray with shape (K, 2), dtype int32

    Notes
    -----
    - This is a convenience wrapper over lapjvx that packs (rows, cols) into a (K, 2) array.
    - Total cost is computed on the ORIGINAL input (not augmented or padded).
    """
    return _lapjvxa(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)
