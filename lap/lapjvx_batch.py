# Copyright (c) 2025 Ratha SIV | MIT License

import os
import numpy as np
from typing import List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ._lapjvx import lapjvx as _lapjvx_single
from ._lapjvx import lapjvxa as _lapjvxa_single


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
) -> Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
           Tuple[List[np.ndarray], List[np.ndarray]]]:
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
        with ThreadPoolExecutor(max_workers=threads) as ex:
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
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(work, bi) for bi in range(B)]
            for fut in as_completed(futures):
                i, t, P = fut.result()
                if return_cost:
                    totals[i] = float(t)  # type: ignore
                pairs_list[i] = np.asarray(P, dtype=np.int64)

    if return_cost:
        return np.asarray(totals, dtype=np.float64), pairs_list  # type: ignore
    return pairs_list

