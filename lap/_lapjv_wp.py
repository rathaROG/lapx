# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, Tuple, Union

from ._lapjv import lapjv as _lapjv


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjv(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: Literal[True] = True,
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def lapjv(
        cost: np.ndarray,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjv(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        *,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjv(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: bool = True,
    ) -> Union[
        Tuple[float, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]: ...


def lapjv(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """Solve the linear assignment problem with the Jonker-Volgenant (JV) algorithm.

    This wrapper returns mapping arrays (x, y):
    - x[i] gives the assigned column for row i, or -1 if the row has no assignment.
    - y[j] gives the assigned row for column j, or -1 if the column has no assignment.

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        A 2D cost matrix. Entry cost[i, j] gives the cost to assign row i to column j.
        The solver accepts any floating data type. It uses one contiguous float64
        buffer when necessary.
    extend_cost : bool, default False
        Permit rectangular inputs through zero-padding to a square matrix.
        See the matrix extension rules below.
    cost_limit : float, default np.inf
        If finite, the solver extends the matrix to size (N+M).
        The added edges have cost_limit/2 costs, with a zero block at the bottom right.
        This models a reject cost for each edge. It permits rectangular inputs
        even if extend_cost=False. The value must be finite or positive infinity.
    return_cost : bool, default True
        If True, return the total assignment cost first.
        The solver calculates this total from the original input array, before
        any matrix extension or padding.

    Returns
    -------
    If return_cost is True:
        total_cost : float
            The solver sums the costs of matched pairs in float64 from the original input.
        x : np.ndarray[int32] with shape (N,)
            This array maps rows to columns. Rows without assignments have value -1.
        y : np.ndarray[int32] with shape (M,)
            This array maps columns to rows. Columns without assignments have value -1.
    Else:
        x : np.ndarray[int32] with shape (N,)
        y : np.ndarray[int32] with shape (M,)

    Matrix extension rules
    ----------------------
    - If cost_limit < inf, extend the matrix to size (N+M) to model reject costs for each edge.
      This permits rectangular inputs.
    - Otherwise, if N != M or extend_cost=True, add zeros to make a square of size max(N, M).
    - Otherwise, solve the original square matrix without extension.

    Notes
    -----
    - The solver adjusts the matrix orientation so the native kernel has rows <= cols.
      The outputs use the original orientation.
    - For a zero-sized dimension, the solver returns 0.0 if return_cost=True.
      All mapping entries have value -1.
    - This wrapper calls the Cython implementation directly. It does not change data types.
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver. Results with these
      values are undefined. Positive infinity can represent a forbidden assignment.
    """
    return _lapjv(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)
