# Copyright (c) 2026 Ratha SIV | MIT License

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import numpy.typing as npt

from ._batch_utils import _normalize_threads
from ._lapmod_wp import FP_DYNAMIC, lapmod as _lapmod_single


_SparseProblem = Tuple[
    Union[int, np.integer],
    npt.NDArray[np.floating],
    npt.NDArray[np.integer],
    npt.NDArray[np.integer],
]


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapmod_batch(
        problems: Sequence[_SparseProblem],
        fast: bool = True,
        return_cost: Literal[True] = True,
        fp_version: int = FP_DYNAMIC,
        n_threads: Optional[int] = 0,
    ) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapmod_batch(
        problems: Sequence[_SparseProblem],
        fast: bool,
        return_cost: Literal[False],
        fp_version: int = FP_DYNAMIC,
        n_threads: Optional[int] = 0,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapmod_batch(
        problems: Sequence[_SparseProblem],
        fast: bool = True,
        *,
        return_cost: Literal[False],
        fp_version: int = FP_DYNAMIC,
        n_threads: Optional[int] = 0,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapmod_batch(
        problems: Sequence[_SparseProblem],
        fast: bool = True,
        return_cost: bool = True,
        fp_version: int = FP_DYNAMIC,
        n_threads: Optional[int] = 0,
    ) -> Union[
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
        Tuple[List[np.ndarray], List[np.ndarray]],
    ]: ...


def lapmod_batch(
    problems: Sequence[_SparseProblem],
    fast: bool = True,
    return_cost: bool = True,
    fp_version: int = FP_DYNAMIC,
    n_threads: Optional[int] = 0,
) -> Union[
    Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    Tuple[List[np.ndarray], List[np.ndarray]],
]:
    """Solve a batch of sparse assignment problems in input order.

    Parameters
    ----------
    problems : sequence of (n, cc, ii, kk) tuples
        Each tuple describes a square sparse problem that lapmod accepts.
        Problem sizes, numbers of stored entries, and array data types may differ.
        Stored costs must be finite, non-negative, and less than lap.LARGE.
        The single solver wrapper checks row pointers and sorted column indices.
        The solver does not change input arrays. Do not change these arrays while the solver runs.
    fast : bool, default True
        Use the native solver, which releases the global interpreter lock (GIL)
        during each solve. False selects the Python solver, where the GIL limits
        speedup from threads.
    return_cost : bool, default True
        Include the total cost for each problem. If False, do not calculate total costs.
    fp_version : int, default FP_DYNAMIC
        This option selects the native path-search version.
        The wrapper passes it to lapmod. When fast=False, lapmod ignores this option.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        The function creates no thread pool for one worker or at most one problem.

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), dtype float64
        x_list, y_list : lists of np.ndarray, dtype int32
    Else:
        x_list, y_list

    For problem b, x_list[b] maps rows to columns and y_list[b] maps columns to rows.
    These arrays match the lapmod outputs and have length n for that problem.
    An empty batch returns empty lists. If return_cost=True, it also returns an
    empty totals array.

    Notes
    -----
    If a problem raises an exception, the caller receives it after the thread pool
    stops. Each solve uses one thread. The pool runs separate problems concurrently.
    Python code that checks inputs and calculates costs can limit speedup,
    especially for small problems.
    """
    batch_size = len(problems)
    threads = _normalize_threads(n_threads)
    totals = np.empty(batch_size, dtype=np.float64) if return_cost else None
    x_list: List[np.ndarray] = []
    y_list: List[np.ndarray] = []

    def work(problem: _SparseProblem) -> Tuple[float, np.ndarray, np.ndarray]:
        n, cc, ii, kk = problem
        if return_cost:
            return _lapmod_single(
                n, cc, ii, kk, fast=fast, return_cost=True, fp_version=fp_version)
        x, y = _lapmod_single(
            n, cc, ii, kk, fast=fast, return_cost=False, fp_version=fp_version)
        return 0.0, x, y

    def collect(results: Iterable[Tuple[float, np.ndarray, np.ndarray]]) -> None:
        for i, (total, x, y) in enumerate(results):
            if totals is not None:
                totals[i] = total
            x_list.append(x)
            y_list.append(y)

    if threads == 1 or batch_size <= 1:
        collect(map(work, problems))
    else:
        with ThreadPoolExecutor(max_workers=min(threads, batch_size)) as pool:
            collect(pool.map(work, problems))

    if totals is not None:
        return totals, x_list, y_list
    return x_list, y_list
