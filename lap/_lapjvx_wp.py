# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, Tuple, Union

from ._lapjvx import lapjvx as _lapjvx  # type: ignore
from ._lapjvx import lapjvxa as _lapjvxa  # type: ignore


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjvx(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: Literal[True] = True,
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def lapjvx(
        cost: np.ndarray,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjvx(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        *,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def lapjvx(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: bool = True,
    ) -> Union[
        Tuple[float, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]: ...


def lapjvx(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray, np.ndarray],
    Tuple[np.ndarray, np.ndarray],
]:
    """Solve the linear assignment problem with the Jonker-Volgenant algorithm.

    The function returns (row_indices, col_indices), as in
    scipy.optimize.linear_sum_assignment.

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        A 2D cost matrix. The solver accepts any floating data type.
        It uses one contiguous float64 buffer when necessary.
    extend_cost : bool, default False
        Permit rectangular inputs through zero-padding to a square matrix.
    cost_limit : float, default np.inf
        If finite, the solver extends the matrix to size (N+M).
        The added edges have cost_limit/2 costs, with a zero block at the bottom right.
        This models a reject cost for each edge and permits rectangular inputs.
        The value must be finite or positive infinity.
    return_cost : bool, default True
        If True, return the total assignment cost first.
        The solver sums this total in float64 from the original input.

    Returns
    -------
    If return_cost is True:
        total_cost : float
        row_indices : np.ndarray with shape (K,), dtype int64
            This array contains the assigned row indices in the original orientation.
        col_indices : np.ndarray with shape (K,), typically dtype int32
            These column indices correspond to row_indices.
    Else:
        row_indices, col_indices

    Notes
    -----
    - The solver adjusts the matrix orientation so the native kernel has rows <= cols.
      The returned indices use the original orientation.
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver. Results with these
      values are undefined. Positive infinity can represent a forbidden assignment.
    - The Cython implementation determines the index data types.
      row_indices uses int64. col_indices often uses int32, depending on NumPy and the platform.
    - Matrix extension follows these rules:
      * If cost_limit < inf, extend the matrix to size (N+M). This permits rectangular inputs.
      * Otherwise, if N != M or extend_cost=True, add zeros to make a square of size max(N, M).
      * Otherwise, solve the original square matrix.
    """
    return _lapjvx(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    @overload
    def lapjvxa(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: Literal[True] = True,
    ) -> Tuple[float, np.ndarray]: ...

    @overload
    def lapjvxa(
        cost: np.ndarray,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
    ) -> np.ndarray: ...

    @overload
    def lapjvxa(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        *,
        return_cost: Literal[False],
    ) -> np.ndarray: ...

    @overload
    def lapjvxa(
        cost: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: bool = True,
    ) -> Union[Tuple[float, np.ndarray], np.ndarray]: ...


def lapjvxa(
    cost: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
) -> Union[
    Tuple[float, np.ndarray],
    np.ndarray,
]:
    """Solve with lapjvx and return assignment pairs with shape (K, 2).

    Each pair contains a row index and a column index.

    Parameters
    ----------
    cost : np.ndarray, shape (N, M)
        A 2D cost matrix.
    extend_cost : bool, default False
        Permit rectangular inputs through zero-padding to a square matrix.
    cost_limit : float, default np.inf
        If finite, the solver extends the matrix to size (N+M) to model reject costs for each edge.
        See lapjvx for details. The value must be finite or positive infinity.
    return_cost : bool, default True
        If True, return the total cost first.

    Returns
    -------
    If return_cost is True:
        total_cost : float
        assignments : np.ndarray with shape (K, 2), dtype int32
            Each row contains (row_index, col_index) in the original orientation.
    Else:
        assignments : np.ndarray with shape (K, 2), dtype int32

    Notes
    -----
    - This wrapper combines the rows and columns from lapjvx in a (K, 2) array.
    - The solver sums total costs in float64 from the original input, before any matrix extension or padding.
    - The solver does not check for NaN (not a number) or negative infinity.
      Check or remove these values before you call the solver. Results with these
      values are undefined. Positive infinity can represent a forbidden assignment.
    """
    return _lapjvxa(cost, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=return_cost)
