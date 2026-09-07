# Copyright (c) 2026 Ratha SIV | MIT License

import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import numpy.typing as npt

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
        Each tuple describes a square sparse problem as accepted by `lapmod`.
        Sizes, numbers of stored entries, and array dtypes may differ between
        problems. Stored costs must be finite, non-negative, and less than
        `lap.LARGE`; row pointers and sorted column indices are validated by
        the single-instance wrapper. Input arrays are not modified and must
        not be mutated by the caller while solving.
    fast : bool, default True
        Use the native solver, which releases the GIL during each solve.
        False uses the Python fallback, where the GIL limits thread speedup.
    return_cost : bool, default True
        Include per-problem totals. False skips total-cost calculation.
    fp_version : int, default FP_DYNAMIC
        Native path-search version, forwarded to `lapmod`. Ignored when
        fast=False, as in the single-instance solver.
    n_threads : int or None, default 0
        Number of worker threads. 0 or None uses `os.cpu_count()`, capped to
        the batch size. Negative values use one worker. No pool is created for
        one worker or a batch containing at most one problem.

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), dtype float64
        x_list, y_list : lists of np.ndarray, dtype int32
    Else:
        x_list, y_list

    Each x_list[b] maps rows to columns and y_list[b] maps columns to rows,
    exactly as returned by `lapmod`, with length n for that problem. An empty
    batch returns empty lists and, when requested, an empty totals array.

    Notes
    -----
    Exceptions from individual problems propagate to the caller after the
    thread pool is shut down. Each solve remains single-threaded; the pool
    runs separate problems concurrently. Python-side validation and cost
    calculation can limit speedup, especially for small problems.
    """
    batch_size = len(problems)
    threads = max(1, int(n_threads or os.cpu_count() or 1))
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
