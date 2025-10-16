# Copyright (c) 2025 Ratha SIV | MIT License

"""LAPX

A linear assignment problem solver using the Jonker-Volgenant
algorithm, providing:

- Sparse (lapmod)
- Enhanced dense (lapjv, lapjvx, lapjvxa)
- Classic dense (lapjvc)

Common Parameters for lapjv, lapjvx, lapjvxa
--------------------------------------------

cost : (N,M) ndarray
    Cost matrix. Entry `cost[i, j]` is the cost of assigning row `i` to column `j`.
extend_cost : bool, optional
    Whether or not to extend a non-square matrix. Default: False.
cost_limit : float, optional
    An upper limit for the cost of a single assignment. Default: np.inf.
return_cost : bool, optional
    Whether or not to return the assignment cost.

Assignment API Overview
-----------------------

There are *multiple interfaces* for dense assignment problems:

lapmod
    Find optimal (minimum-cost) assignment for a sparse cost matrix.

lapjv
    Enhanced Jonker-Volgenant for dense cost matrices.
    **Returns:** (x, y) or (cost, x, y)
    - `x[i]`: assigned column for row i (or -1 if unassigned).
    - `y[j]`: assigned row for column j (or -1 if unassigned).
    - Not in parallel assignment format—**do not use** `list(zip(x, y))` directly!

lapjvx
    Enhanced Jonker-Volgenant with practical output.
    **Returns:** (cost, row_indices, col_indices) or (row_indices, col_indices)
    - Parallel arrays: row_indices[i] assigned to col_indices[i].
    - Matches the output style of ``scipy.optimize.linear_sum_assignment`` and ``lapjvc``.

lapjvxa
    Enhanced Jonker-Volgenant with assignment array output.
    **Returns:** (cost, assignments) or (assignments)
    - `assignments`: array of shape (K, 2), each row is (row_index, col_index).
    - Most convenient for direct iteration or indexing.

lapjvc
    Classic Jonker-Volgenant for dense cost matrices.
    **Returns:** (cost, row_indices, col_indices) or (row_indices, col_indices)
    - `row_indices` and `col_indices` are parallel arrays: row_indices[i] assigned to col_indices[i].
    - You can do: `assignments = np.array(list(zip(row_indices, col_indices)))`

"""

__version__ = '0.6.0'

from .lapmod import lapmod

from ._lapjv import (
    lapjv,
    LARGE_ as LARGE,
    FP_1_ as FP_1,
    FP_2_ as FP_2,
    FP_DYNAMIC_ as FP_DYNAMIC
)

from ._lapjvx import (
    lapjvx,
    lapjvxa
)

from ._lapjvc import lapjvc

__all__ = ['lapmod', 'lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'FP_1', 'FP_2', 'FP_DYNAMIC', 'LARGE']