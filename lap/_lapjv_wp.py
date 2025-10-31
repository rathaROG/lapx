# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Tuple, Union

from ._lapjv import lapjv as _lapjv


def lapjv(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """
    Solve the Linear Assignment Problem using the Jonker-Volgenant (JV) algorithm.

    This wrapper returns lapjv-style mapping vectors (x, y), where:
      - x[i] is the assigned column index for row i, or -1 if unassigned.
      - y[j] is the assigned row index for column j, or -1 if unassigned.

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        2D cost matrix. Entry cost[i, j] is the cost of assigning row i to column j.
        Any float dtype is accepted; internally a single contiguous float64 buffer is used when needed.
    extend_cost : bool, default False
        Permit rectangular inputs by zero-padding to a square matrix.
        See the unified augmentation policy below.
    cost_limit : float, default np.inf
        When finite, the solver augments to size (N+M) with sentinel edges of cost_limit/2
        and a bottom-right zero block. This models a per-edge "reject" cost and allows
        rectangular inputs even if extend_cost=False.
    return_cost : bool, default True
        If True, include the total assignment cost as the first return value.
        The total is computed from the ORIGINAL (un-augmented/unpadded) input array.

    Returns
    -------
    If return_cost is True:
        total_cost : float
            Sum of costs over matched pairs, computed on the ORIGINAL input.
        x : np.ndarray[int32] with shape (N,)
            Mapping from rows to columns; -1 for unassigned rows.
        y : np.ndarray[int32] with shape (M,)
            Mapping from columns to rows; -1 for unassigned columns.
    Else:
        x : np.ndarray[int32] with shape (N,)
        y : np.ndarray[int32] with shape (M,)

    Unified augmentation policy
    ---------------------------
    - If cost_limit < inf: always augment to (N+M) to model per-edge rejects (rectangular allowed).
    - Else if (N != M) or extend_cost=True: zero-pad to a square of size max(N, M).
    - Else (square, un-augmented): run on the given square matrix.

    Notes
    -----
    - Orientation is normalized internally (kernel works with rows <= cols); outputs are mapped
      back to the ORIGINAL orientation before returning.
    - For zero-sized dimensions, the solver returns 0.0 (if requested) and all -1 mappings.
    - This wrapper forwards directly to the Cython implementation without altering dtypes.
    """
    return _lapjv(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)
