# Copyright (c) 2026 Ratha SIV | MIT License

"""LAPX provides Jonker-Volgenant (JV) solvers for linear assignment problems.

Single-matrix solvers
---------------------
- lapmod is the sparse solver from Tomas Kazmar's lap.
- lapjv is the JV solver from Tomas Kazmar's lap. It returns mapping arrays (x, y).
- lapjvx extends lapjv. It returns aligned index arrays (rows, cols), as in SciPy.
- lapjvxa wraps lapjvx. It returns assignment pairs with shape (K, 2).
- lapjvc uses Christoph Heindl's classic JV variant. It returns (rows, cols).
- lapjvs extends Vadim Markovtsev's lapjv. It supports mapping arrays and aligned index arrays.
- lapjvsa wraps lapjvs. It returns assignment pairs with shape (K, 2).

Batch solvers
-------------
- lapjvx_batch runs lapjvx. It returns (totals, rows_list, cols_list) or (rows_list, cols_list).
- lapjvxa_batch runs lapjvxa. It returns (totals, pairs_list) or pairs_list, with pair arrays of shape (K_b, 2).
- lapjvs_batch runs lapjvs. It returns (totals, rows_list, cols_list) or (rows_list, cols_list).
- lapjvsa_batch runs lapjvsa. It returns (totals, pairs_list) or pairs_list, with pair arrays of shape (K_b, 2).
- lapmod_batch runs lapmod. It returns (totals, x_list, y_list) or (x_list, y_list).

Notes
-----
- Dense solvers accept square and rectangular matrices. lapmod requires square problems.
- Dense batch solvers accept costs with shape (B, N, M).
- lapmod_batch accepts a sequence of sparse (n, cc, ii, kk) problems. The problem sizes can differ.
- The lapjvs family may recalculate total costs from the original input for consistency. This adds negligible overhead.
- For tests and benchmarks, see https://github.com/rathaROG/lapx.
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
    from ._lapmod_batch_wp import lapmod_batch
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
    'lapmod_batch': ("lap._lapmod_batch_wp", "lapmod_batch"),
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

__version__ = '0.10.0'
__author__ = 'Ratha SIV'
__description__ = 'Linear assignment problem solvers, including single and batch solvers.'
__homepage__ = 'https://github.com/rathaROG/lapx'
__all__ = [
    # Single-matrix solvers
    'lapmod', 'lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa',
    # Batch solvers
    'lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch', 'lapmod_batch',
    # Constants
    'FP_1', 'FP_2', 'FP_DYNAMIC', 'LARGE',
]
