# Copyright (c) 2025 Ratha SIV | MIT License

"""
LAPX — Jonker-Volgenant (JV) linear assignment solvers.

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
- lapjvs* family wrappers may recompute the total cost from the original input for 
  consistency; this has negligible overhead.
- For tests and benchmarks, see the official repo: https://github.com/rathaROG/lapx
"""

from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
    # Single-matrix solvers
    from ._lapmod_wp import lapmod
    from ._lapjv_wp import lapjv
    from ._lapjvx_wp import lapjvx, lapjvxa
    from ._lapjvc_wp import lapjvc
    from ._lapjvs_wp import lapjvs, lapjvsa
    # Batch solvers
    from ._lapjvx_batch_wp import lapjvx_batch, lapjvxa_batch
    from ._lapjvs_batch_wp import lapjvs_batch, lapjvsa_batch
    # Constants
    from ._lapjv import (  # type: ignore
        LARGE_ as LARGE,
        FP_1_ as FP_1,
        FP_2_ as FP_2,
        FP_DYNAMIC_ as FP_DYNAMIC,
    )

_exports = {
    # Single-matrix solvers
    'lapmod': ("lap._lapmod_wp", "lapmod"),
    'lapjv': ("lap._lapjv_wp", "lapjv"),
    'lapjvx': ("lap._lapjvx_wp", "lapjvx"),
    'lapjvxa': ("lap._lapjvx_wp", "lapjvxa"),
    'lapjvc': ("lap._lapjvc_wp", "lapjvc"),
    'lapjvs': ("lap._lapjvs_wp", "lapjvs"),
    'lapjvsa': ("lap._lapjvs_wp", "lapjvsa"),
    # Batch solvers
    'lapjvx_batch': ("lap._lapjvx_batch_wp", "lapjvx_batch"),
    'lapjvxa_batch': ("lap._lapjvx_batch_wp", "lapjvxa_batch"),
    'lapjvs_batch': ("lap._lapjvs_batch_wp", "lapjvs_batch"),
    'lapjvsa_batch': ("lap._lapjvs_batch_wp", "lapjvsa_batch"),
    # Constants
    'LARGE': ("lap._lapjv", "LARGE_"),
    'FP_1': ("lap._lapjv", "FP_1_"),
    'FP_2': ("lap._lapjv", "FP_2_"),
    'FP_DYNAMIC': ("lap._lapjv", "FP_DYNAMIC_"),
}

def __getattr__(name):
    if name in _exports:
        mod_path, attr = _exports[name]
        mod = importlib.import_module(mod_path)
        obj = getattr(mod, attr)
        globals()[name] = obj
        return obj
    raise AttributeError(f"LAPX could not find attribute '{name}'.")

__version__ = '0.9.4'
__author__ = 'Ratha SIV'
__description__ = 'Linear assignment problem solvers, including single and batch solvers.'
__homepage__ = 'https://github.com/rathaROG/lapx'
__all__ = [
    # Single-matrix solvers
    'lapmod', 'lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa',
    # Batch solvers
    'lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch',
    # Constants
    'FP_1', 'FP_2', 'FP_DYNAMIC', 'LARGE',
]
