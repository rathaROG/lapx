# Copyright (c) 2025 Ratha SIV | MIT License

import numpy as np
from typing import Tuple, Union

from ._lapjvc import lapjvc as _lapjvc  # type: ignore


def lapjvc(
    cost: np.ndarray,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """
    Solve the Linear Assignment Problem using the classic dense Jonker-Volgenant algorithm.

    This is a thin wrapper around the C++ binding that computes an optimal assignment for a 2D
    cost matrix. It returns row/column index arrays (JVX-like) matching SciPy's
    linear_sum_assignment ordering.

    Parameters
    ----------
    cost : np.ndarray, shape (M, N)
        2D cost matrix. Supported dtypes: int32, int64, float32, float64.
        - Rectangular inputs are handled internally (the dense solver pads as needed).
        - NaN entries (for float types) are treated as forbidden assignments.
    return_cost : bool, default True
        If True, return (total_cost, row_indices, col_indices).
        If False, return only (row_indices, col_indices).

    Returns
    -------
    If return_cost is True:
        total_cost : float
            Sum of cost at the selected (row, col) pairs.
        row_indices : np.ndarray with shape (K,), dtype int64 (platform-dependent via NumPy)
            Row indices of the assignment.
        col_indices : np.ndarray with shape (K,), dtype int64 (platform-dependent via NumPy)
            Column indices of the assignment.
    Else:
        row_indices, col_indices

    Notes
    -----
    - This is the classic dense JV routine; for very large, sparse, or otherwise
      structured problems, consider using lapjv/lapjvx variants optimized for those cases.
    - Forbidden assignments can be encoded with np.nan (float inputs).
    """
    return _lapjvc(cost, return_cost=return_cost)
