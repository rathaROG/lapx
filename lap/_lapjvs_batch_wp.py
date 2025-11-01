# Copyright (c) 2025 Ratha SIV | MIT License

import os
import numpy as np
from typing import List, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ._lapjvs_wp import lapjvs as _lapjvs_single
from ._lapjvs_wp import lapjvsa as _lapjvsa_single


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
    Batched lapjvs solver with a thread pool.

    For each 2D cost matrix in a 3D batch, this function runs `lapjvs` and
    aggregates the per-instance results. It preserves the order of the batch
    in the outputs.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        Batch of cost matrices (float32/float64). Each slice `costs[b]` is
        a single LAP instance.
    extend_cost : bool, default False
        If True, rectangular instances are solved via internal zero-padding.
        If False, each instance must be square or a ValueError is raised.
        This is forwarded to the single-instance solver.
    return_cost : bool, default True
        If True, return per-instance totals as the first output.
    n_threads : int, default 0
        Number of worker threads. When 0 or None, uses `os.cpu_count()`.
        Actual workers are capped to the batch size.
    prefer_float32 : bool, default True
        Hint to run each kernel in float32 (forwarded to the single solver; 
        see the `lapjvs` for the details).

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), float64
            Total assignment cost for each instance, computed from the ORIGINAL
            per-instance cost matrix.
        rows_list : List[np.ndarray[int64]]
            For each b, a 1D array of assigned row indices (length K_b).
        cols_list : List[np.ndarray[int64]]
            For each b, a 1D array of assigned col indices (length K_b).
    Else:
        rows_list, cols_list

    Raises
    ------
    ValueError
        - If `costs` is not a 3D array.
        - If any instance is rectangular while `extend_cost=False`.

    Notes
    -----
    - Threading:
      The underlying native kernel releases the GIL, so using multiple threads
      can accelerate large batches on multi-core systems.
    - Dtypes:
      Each instance may be float32 or float64; the kernel selection and casting
      follow the single-instance rules. Totals are float64.
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
            total, rows, cols = _solve_one_jvs(  # type: ignore
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32,
                jvx_like=True, return_cost=True
            )
            return bi, total, rows, cols
        else:
            rows, cols = _solve_one_jvs(  # type: ignore
                a2d, extend_cost=extend_cost, prefer_float32=prefer_float32,
                jvx_like=True, return_cost=False
            )
            return bi, None, rows, cols

    if threads == 1 or B == 1:
        for bi in range(B):
            idx, t, r, c = work(bi)
            if return_cost:
                totals[idx] = float(t)  # type: ignore
            rows_list[idx] = np.asarray(r, dtype=np.int64)
            cols_list[idx] = np.asarray(c, dtype=np.int64)
    else:
        # Cap workers to the batch size
        with ThreadPoolExecutor(max_workers=min(threads, B)) as ex:
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
    Batched lapjvsa solver, returning (K_b, 2) arrays per instance.

    Runs `lapjvsa` on each (N, M) slice of a (B, N, M) batch and aggregates
    the results while preserving order.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        Batch of cost matrices.
    extend_cost : bool, default False
        If True, rectangular instances are solved via internal zero-padding.
    return_cost : bool, default True
        If True, include per-instance totals as the first returned array.
    n_threads : int, default 0
        Number of worker threads. 0 or None uses `os.cpu_count()`.
    prefer_float32 : bool, default True
        Hint to run each kernel in float32 (forwarded to the single solver; 
        see the `lapjvsa` for the details).

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
    - See `lapjvsa` for details on dtype handling and total-cost accumulation.
    - Results are reassembled in batch order irrespective of threading.
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
        # Cap workers to the batch size
        with ThreadPoolExecutor(max_workers=min(threads, B)) as ex:
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

