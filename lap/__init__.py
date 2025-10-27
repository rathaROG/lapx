# Copyright (c) 2025 Ratha SIV | MIT License

"""
LAPX — Jonker-Volgenant (JV) linear assignment solvers.

Single-matrix solvers — common parameters
-----------------------------------------
cost : (N, M) ndarray
    Cost matrix. Entry cost[i, j] is the cost of assigning row i to column j.
extend_cost : bool, optional
    Whether or not to extend a non-square matrix. Default: False.
cost_limit : float, optional
    An upper limit for the cost of a single assignment. Default: np.inf.
return_cost : bool, optional
    Whether or not to return the assignment cost.

Batch solvers — common parameters
---------------------------------
costs : (B, N, M) ndarray
    A batch of cost matrices. costs[b] is the cost matrix for batch item b.
extend_cost : bool, optional
    Whether to extend non-square matrices in the batch. Default: False.
cost_limit : float, optional
    An upper limit for the cost of a single assignment. Default: np.inf.
return_cost : bool, optional
    Whether to return the assignment costs per batch item.
n_threads : int, optional
    Number of OpenMP threads to use. 0 selects a runtime default. Default: 0.
prefer_float32 : bool, optional
    Prefer the float32 kernel when possible to reduce memory bandwidth.
    Defaults to True for lapjvs-based batch solvers.

Provided solvers (single-matrix)
--------------------------------
- lapmod   : Sparse assignment solver (for sparse cost matrices) by Tomas Kazmar's lap.
- lapjv    : JV assignment solver by Tomas Kazmar's lap; returns JV-style mappings (x, y).
- lapjvx   : Enhanced lapjv by lapx; returns SciPy-like outputs (rows, cols).
- lapjvxa  : Convenience wrapper of lapjvx by lapx; returns (K, 2) assignment pairs.
- lapjvc   : Classic JV variant by Christoph Heindl's lapsolver; returns (rows, cols).
- lapjvs   : Enhanced Vadim Markovtsev's lapjv by lapx; returns either style.
- lapjvsa  : Convenience wrapper of lapjvs by lapx; returns (K, 2) assignment pairs.

Provided solvers (batch)
------------------------
- lapjvx_batch  : Batched lapjvx; returns (totals, rows_list, cols_list) or (rows_list, cols_list).
- lapjvxa_batch : Batched lapjvxa; returns (totals, pairs_list) or pairs_list with (K_b, 2).
- lapjvs_batch  : Batched lapjvs; returns (totals, rows_list, cols_list) or (rows_list, cols_list).
- lapjvsa_batch : Batched lapjvsa; returns (totals, pairs_list) or pairs_list with (K_b, 2).

Notes
-----
- All solvers in lapx handle both square and rectangular cost matrices.
- Batch solvers accept costs shaped (B, N, M) and return per-instance assignments.
- lapjvs and lapjvs_* wrappers may recompute the total cost from the original input
  for float32/float64 parity; this has negligible overhead.
- For details and benchmarks, see the official repo: https://github.com/rathaROG/lapx
"""

__version__ = '0.8.0'

# Single-matrix solvers
from .lapmod import lapmod
from ._lapjv import (
    lapjv,
    LARGE_ as LARGE,
    FP_1_ as FP_1,
    FP_2_ as FP_2,
    FP_DYNAMIC_ as FP_DYNAMIC
)
from ._lapjvx import lapjvx, lapjvxa
from ._lapjvc import lapjvc
from .lapjvs import lapjvs, lapjvsa

# Batch solvers
from .lapjvx_batch import lapjvx_batch, lapjvxa_batch
from .lapjvs_batch import lapjvs_batch, lapjvsa_batch

__all__ = [
    'lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa',
    'lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch',
    'lapmod', 'FP_1', 'FP_2', 'FP_DYNAMIC', 'LARGE'
]
