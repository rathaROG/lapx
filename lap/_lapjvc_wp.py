# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, Tuple, Union

from ._lapjvc import lapjvc as _lapjvc  # type: ignore


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjvc(
        cost: np.ndarray,
        return_cost: Literal[True] = True,
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def lapjvc(
        cost: np.ndarray,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjvc(
        cost: np.ndarray,
        return_cost: bool = True,
    ) -> Union[
        Tuple[float, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]: ...


def lapjvc(
    cost: np.ndarray,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """Solve the linear assignment problem with the classic dense Jonker-Volgenant algorithm.

    This wrapper calls the C++ binding to calculate an optimal assignment for a 2D
    cost matrix. It returns aligned row and column index arrays, as in lapjvx.
    The order matches SciPy's linear_sum_assignment.

    Parameters
    ----------
    cost : np.ndarray, shape (M, N)
        A 2D cost matrix with data type int32, int64, float32, or float64.
        The dense solver pads rectangular inputs when necessary.
        It treats NaN and positive or negative infinity as forbidden assignments.
    return_cost : bool, default True
        If True, return (total_cost, row_indices, col_indices).
        If False, return (row_indices, col_indices).

    Returns
    -------
    If return_cost is True:
        total_cost : float
            The solver sums the costs at the assigned (row, col) pairs in float64.
        row_indices : np.ndarray with shape (K,), dtype int64 (platform-dependent via NumPy)
            This array contains the assigned row indices.
        col_indices : np.ndarray with shape (K,), dtype int64 (platform-dependent via NumPy)
            This array contains the assigned column indices.
    Else:
        row_indices, col_indices

    Notes
    -----
    - This function uses the classic dense JV algorithm.
      For very large, sparse, or otherwise structured problems, consider lapjv or lapjvx variants optimized for those cases.
    - Use np.nan or np.inf to represent forbidden assignments in floating inputs.
    """
    return _lapjvc(cost, return_cost=return_cost)
