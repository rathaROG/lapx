# Copyright (c) 2026 Ratha SIV | MIT License

"""Static signatures and documentation for the native solver entry points."""

from typing import Tuple, Union, overload
from typing_extensions import Literal, Protocol
import numpy as np

class _LapjvcSolver(Protocol):
    @overload
    def __call__(
        self,
        cost: np.ndarray,
        return_cost: Literal[True] = True,
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def __call__(
        self,
        cost: np.ndarray,
        return_cost: Literal[False],
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def __call__(
        self,
        cost: np.ndarray,
        return_cost: bool = True,
    ) -> Union[
        Tuple[float, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]: ...

lapjvc: _LapjvcSolver
"""Solve the linear assignment problem with the classic dense Jonker-Volgenant algorithm.

This function calculates an optimal assignment for a 2D
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
    row_indices : np.ndarray with shape (K,), dtype int32
        This array contains the assigned row indices.
    col_indices : np.ndarray with shape (K,), dtype int32
        This array contains the assigned column indices.
Else:
    row_indices, col_indices

Notes
-----
- This function uses the classic dense JV algorithm.
  For very large, sparse, or otherwise structured problems, consider lapjv or lapjvx variants optimized for those cases.
- Use np.nan or np.inf to represent forbidden assignments in floating inputs.

Examples
--------
>>> import numpy as np
>>> import lap
>>> cost = np.array([[6, 9, 1], [10, 3, 2], [8, 7, 4.]], dtype=np.float32)
>>> total, rows, cols = lap.lapjvc(cost)
>>> list(zip(rows.tolist(), cols.tolist()))
[(0, 2), (1, 1), (2, 0)]

References
----------
Jonker, R., and Volgenant, A. (1987). A shortest augmenting path algorithm
for dense and sparse linear assignment problems. Computing 38, 325-340.
This implementation adapts Christoph Heindl's py-lapsolver (MIT License),
which is based on Jaehyun Park's MinCostMatching.cc.

"""
