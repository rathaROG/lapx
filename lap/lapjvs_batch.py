# Copyright (c) 2025 Ratha SIV | MIT License

import os
import numpy as np
from typing import List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

# We build batch on top of the stable single-instance API (releases GIL inside)
from .lapjvs import lapjvs as _lapjvs_single
from .lapjvs import lapjvsa as _lapjvsa_single


def _normalize_threads(n_threads: int) -> int:
    if n_threads is None or n_threads == 0:
        cpu = os.cpu_count() or 1
        return max(1, int(cpu))
    return max(1, int(n_threads))


def _solve_one_jvs(
    a2d: np.ndarray,
    extend_cost: bool,
    prefer_float32: bool,
    jvx_like: bool,
    return_cost: bool,
):
    # Calls the proven single-instance wrapper; it releases the GIL internally.
    return _lapjvs_single(
        a2d, extend_cost=extend_cost, return_cost=return_cost,
        jvx_like=jvx_like, prefer_float32=prefer_float32
    )


def _solve_one_jvsa(
    a2d: np.ndarray,
    extend_cost: bool,
    prefer_float32: bool,
    return_cost: bool,
):
    return _lapjvsa_single(
        a2d, extend_cost=extend_cost, return_cost=return_cost,
        prefer_float32=prefer_float32
    )


def lapjvs_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    return_cost: bool = True,
    n_threads: int = 0,
    prefer_float32: bool = True,
) -> Union[
    Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    Tuple[List[np.ndarray], List[np.ndarray]]
]:
    """
    Stable batched JVS built on the single-instance solver with a thread pool.
    - costs: (B, N, M) array-like (float32/float64)
    - extend_cost: pad rectangular inputs to square
    - return_cost: if True, returns totals (B,) first
    - n_threads: 0 -> os.cpu_count(), else exact number of threads
    - prefer_float32: forward to single-instance kernel

    Returns:
      if return_cost:
        (totals: (B,), rows_list: List[(K_b,)], cols_list: List[(K_b,)])
      else:
        (rows_list, cols_list)
    """
    A = np.asarray(costs)
    if A.ndim != 3:
        raise ValueError("3-dimensional array expected [B, N, M]")

    B, N, M = A.shape
    threads = _normalize_threads(n_threads)

    # Preallocate outputs
    totals = np.empty((B,), dtype=np.float64) if return_cost else None
    rows_list: List[np.ndarray] = [None] * B  # type: ignore
    cols_list: List[np.ndarray] = [None] * B  # type: ignore

    # Worker
    def work(bi: int):
        a2d = A[bi]
        if return_cost:
            total, rows, cols = _solve_one_jvs(
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32,
                jvx_like=True, return_cost=True
            )
            return bi, total, rows, cols
        else:
            rows, cols = _solve_one_jvs(
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32,
                jvx_like=True, return_cost=False
            )
            return bi, None, rows, cols

    if threads == 1 or B == 1:
        # Serial path (still GIL-free inside the solver)
        for bi in range(B):
            idx, t, r, c = work(bi)
            if return_cost:
                totals[idx] = float(t)  # type: ignore
            rows_list[idx] = np.asarray(r, dtype=np.int64)
            cols_list[idx] = np.asarray(c, dtype=np.int64)
    else:
        # Parallel path (ThreadPool is OK because solver releases GIL)
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(work, bi) for bi in range(B)]
            for fut in as_completed(futures):
                idx, t, r, c = fut.result()
                if return_cost:
                    totals[idx] = float(t)  # type: ignore
                rows_list[idx] = np.asarray(r, dtype=np.int64)
                cols_list[idx] = np.asarray(c, dtype=np.int64)

    if return_cost:
        return np.asarray(totals, dtype=np.float64), rows_list, cols_list  # type: ignore
    else:
        return rows_list, cols_list


def lapjvsa_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    return_cost: bool = True,
    n_threads: int = 0,
    prefer_float32: bool = True,
) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]:
    """
    Stable batched JVS (pairs API) built on the single-instance wrapper with a thread pool.

    Returns:
      if return_cost:
        (totals: (B,), pairs_list: List[(K_b, 2)])
      else:
        (pairs_list,)
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
            total, pairs = _solve_one_jvsa(
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32, return_cost=True
            )
            return bi, total, pairs
        else:
            pairs = _solve_one_jvsa(
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32, return_cost=False
            )
            return bi, None, pairs

    if threads == 1 or B == 1:
        for bi in range(B):
            idx, t, P = work(bi)
            if return_cost:
                totals[idx] = float(t)  # type: ignore
            pairs_list[idx] = np.asarray(P, dtype=np.int64)
    else:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(work, bi) for bi in range(B)]
            for fut in as_completed(futures):
                idx, t, P = fut.result()
                if return_cost:
                    totals[idx] = float(t)  # type: ignore
                pairs_list[idx] = np.asarray(P, dtype=np.int64)

    if return_cost:
        return np.asarray(totals, dtype=np.float64), pairs_list  # type: ignore
    else:
        return pairs_list
