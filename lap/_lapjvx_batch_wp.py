# Copyright (c) 2025 Ratha SIV | MIT License

import os
import numpy as np
from typing import List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ._lapjvx import lapjvx as _lapjvx_single  # type: ignore
from ._lapjvx import lapjvxa as _lapjvxa_single  # type: ignore


def _normalize_threads(n_threads: int) -> int:
    if not n_threads:
        return max(1, int(os.cpu_count() or 1))
    return max(1, int(n_threads))


def lapjvx_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
    n_threads: int = 0,
) -> Union[
    Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    Tuple[List[np.ndarray], List[np.ndarray]]
]:
    """
    Batched lapjvx solver with a thread pool.

    This function applies a JVX-style solver (`lapjvx`) across a batch of cost
    matrices and aggregates the results. It preserves batch order and supports
    multi-threaded execution.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        Batch of cost matrices (float32/float64).
    extend_cost : bool, default False
        If True, rectangular matrices are handled via internal zero-padding.
        If False, instances must be square.
    cost_limit : float, default np.inf
        A per-instance threshold to prune/limit assignments, forwarded to the
        underlying `lapjvx` implementation.
    return_cost : bool, default True
        If True, returns per-instance totals first.
    n_threads : int, default 0
        Number of worker threads. 0 or None uses `os.cpu_count()`.

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), float64
        rows_list : List[np.ndarray[int64]] of length B
        cols_list : List[np.ndarray[int64]] of length B
    Else:
        rows_list, cols_list

    Raises
    ------
    ValueError
        - If `costs` is not a 3D array.
        - If any instance is rectangular while `extend_cost=False`.

    Notes
    -----
    - See the single-instance `lapjvx` for detailed behavior around `extend_cost`
      and `cost_limit`.
    """
    A = np.asarray(costs)
    if A.ndim != 3:
        raise ValueError("3-dimensional array expected [B, N, M]")
    B = A.shape[0]
    threads = _normalize_threads(n_threads)

    totals = np.empty((B,), dtype=np.float64) if return_cost else None
    rows_list: List[np.ndarray] = [None] * B  # type: ignore
    cols_list: List[np.ndarray] = [None] * B  # type: ignore

    def work(bi: int):
        a2d = A[bi]
        if return_cost:
            total, rows, cols = _lapjvx_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=True
            )
            return bi, total, rows, cols
        else:
            rows, cols = _lapjvx_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=False
            )
            return bi, None, rows, cols

    if threads == 1 or B == 1:
        for bi in range(B):
            i, t, r, c = work(bi)
            if return_cost:
                totals[i] = float(t)  # type: ignore
            rows_list[i] = np.asarray(r, dtype=np.int64)
            cols_list[i] = np.asarray(c, dtype=np.int64)
    else:
        # Cap workers to the batch size
        with ThreadPoolExecutor(max_workers=min(threads, B)) as ex:
            futures = [ex.submit(work, bi) for bi in range(B)]
            for fut in as_completed(futures):
                i, t, r, c = fut.result()
                if return_cost:
                    totals[i] = float(t)  # type: ignore
                rows_list[i] = np.asarray(r, dtype=np.int64)
                cols_list[i] = np.asarray(c, dtype=np.int64)

    if return_cost:
        return np.asarray(totals, dtype=np.float64), rows_list, cols_list  # type: ignore
    return rows_list, cols_list


def lapjvxa_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
    n_threads: int = 0,
) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]:
    """
    Batched lapjvxa solver, returning (K_b, 2) arrays per instance.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        Batch of cost matrices.
    extend_cost : bool, default False
        If True, rectangular matrices are solved by internal zero-padding.
    cost_limit : float, default np.inf
        Forwarded to `lapjvxa` to limit/prune assignments.
    return_cost : bool, default True
        If True, includes per-instance totals as the first returned array.
    n_threads : int, default 0
        Number of worker threads. 0 or None uses `os.cpu_count()`.

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), float64
        pairs_list : List[np.ndarray[int64] with shape (K_b, 2)]
    Else:
        pairs_list

    Raises
    ------
    ValueError
        If `costs` is not a 3D array, or if any instance is rectangular while
        `extend_cost=False`.

    Notes
    -----
    - See `lapjvxa` for single-instance behavior and semantics of `cost_limit`.
    - Results are returned in the original batch order.
    """
    A = np.asarray(costs)
    if A.ndim != 3:
        raise ValueError("3-dimensional array expected [B, N, M]")
    B = A.shape[0]
    threads = _normalize_threads(n_threads)

    totals = np.empty((B,), dtype=np.float64) if return_cost else None
    pairs_list: List[np.ndarray] = [None] * B  # type: ignore

    def work(bi: int):
        a2d = A[bi]
        if return_cost:
            total, pairs = _lapjvxa_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=True
            )
            return bi, total, pairs
        else:
            pairs = _lapjvxa_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=False
            )
            return bi, None, pairs

    if threads == 1 or B == 1:
        for bi in range(B):
            i, t, P = work(bi)
            if return_cost:
                totals[i] = float(t)  # type: ignore
            pairs_list[i] = np.asarray(P, dtype=np.int64)
    else:
        # Cap workers to the batch size
        with ThreadPoolExecutor(max_workers=min(threads, B)) as ex:
            futures = [ex.submit(work, bi) for bi in range(B)]
            for fut in as_completed(futures):
                i, t, P = fut.result()
                if return_cost:
                    totals[i] = float(t)  # type: ignore
                pairs_list[i] = np.asarray(P, dtype=np.int64)

    if return_cost:
        return np.asarray(totals, dtype=np.float64), pairs_list  # type: ignore
    return pairs_list
