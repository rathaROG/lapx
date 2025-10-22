# Copyright (c) 2025 Ratha SIV | MIT License

"""
LAPX — Jonker-Volgenant (JV) linear assignment solvers.

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

Provided solvers
----------------
- lapmod   : Sparse assignment solver (for sparse cost matrices) by Tomas Kazmar's lap.
- lapjv    : JV assignment solver by Tomas Kazmar's lap; returns JV-style mappings (x, y).
- lapjvx   : Enhanced lapjv by lapx; returns with SciPy-like outputs (rows, cols).
- lapjvxa  : Convenience wrapper of lapjvx by lapx; returns (K, 2) assignment pairs.
- lapjvc   : Classic JV variant by Christoph Heindl's lapsolver; returns (rows, cols).
- lapjvs   : Enhanced Vadim Markovtsev's lapjv by lapx; returns either style.

Notes
-----
- All solvers in lapx handle both square and rectangular cost matrices.
- Output formats may differ by solvers and input parameters.
- For details and benchmarks, see the official repo https://github.com/rathaROG/lapx .
"""

__version__ = '0.7.1'

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
from .lapjvs import lapjvs

__all__ = ['lapmod', 'lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'FP_1', 'FP_2', 'FP_DYNAMIC', 'LARGE']
