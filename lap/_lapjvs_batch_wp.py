# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ._batch_utils import _normalize_threads
from ._lapjvs_wp import lapjvs as _lapjvs_single
from ._lapjvs_wp import lapjvsa as _lapjvsa_single


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


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjvs_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvs_batch(
        costs: np.ndarray,
        extend_cost: bool,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvs_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvs_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Union[
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
        Tuple[List[np.ndarray], List[np.ndarray]],
    ]: ...


def lapjvs_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    return_cost: bool = True,
    n_threads: Optional[int] = 0,
    prefer_float32: bool = True,
) -> Union[
    Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    Tuple[List[np.ndarray], List[np.ndarray]]
]:
    """Solve a batch of cost matrices with lapjvs.

    It runs lapjvs on each (N, M) slice of the (B, N, M) batch.
    It keeps the input order and supports execution with multiple threads.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        A batch of cost matrices with data type float32 or float64.
        Each costs[b] contains one assignment problem.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        If True, the solver pads rectangular problems with zeros.
        If False, each problem must be square.
        The wrapper passes this option to lapjvs.
    return_cost : bool, default True
        If True, return the array of total costs first.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        The function creates no thread pool for one worker or at most one problem.
    prefer_float32 : bool, default True
        Request a float32 kernel for each problem.
        The wrapper passes this option to lapjvs. See lapjvs for details.

    Returns
    -------
    If return_cost is True:
        totals : np.ndarray, shape (B,), float64
            Each entry gives the total cost for one original cost matrix.
        rows_list : List[np.ndarray[int64]] of length B
            Each array contains the assigned row indices for one problem, with length K_b.
        cols_list : List[np.ndarray[int64]] of length B
            Each array contains the assigned column indices for one problem, with length K_b.
    Else:
        rows_list, cols_list

    Raises
    ------
    ValueError
        The function raises this exception if costs is not a 3D array.
        It also raises this exception for rectangular problems when extend_cost=False.

    Notes
    -----
    See lapjvs for data types, total-cost sums, and other single solver behavior.

    The native kernel releases the global interpreter lock (GIL).
    Multiple threads can make large batches faster on systems with multiple CPU cores.

    Each problem may use float32 or float64. Kernel selection and data conversion
    follow the single solver rules. Totals use float64.

    Results keep the input order regardless of the thread count.
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

    if threads == 1 or B <= 1:
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


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    @overload
    def lapjvsa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Tuple[np.ndarray, List[np.ndarray]]: ...

    @overload
    def lapjvsa_batch(
        costs: np.ndarray,
        extend_cost: bool,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> List[np.ndarray]: ...

    @overload
    def lapjvsa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> List[np.ndarray]: ...

    @overload
    def lapjvsa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
        prefer_float32: bool = True,
    ) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]: ...


def lapjvsa_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    return_cost: bool = True,
    n_threads: Optional[int] = 0,
    prefer_float32: bool = True,
) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]:
    """Solve a batch of cost matrices with lapjvsa.

    The function returns an array of assignment pairs with shape (K_b, 2) for each problem.

    It runs lapjvsa on each (N, M) slice of the (B, N, M) batch.
    It keeps the input order and supports execution with multiple threads.

    Parameters
    ----------
    costs : np.ndarray, shape (B, N, M)
        A batch of cost matrices with data type float32 or float64.
        Each costs[b] contains one assignment problem.
        The solver does not check for NaN (not a number) or negative infinity.
        Check or remove these values before you call the solver. Results with these
        values are undefined. Positive infinity can represent a forbidden assignment.
    extend_cost : bool, default False
        If True, the solver pads rectangular problems with zeros.
        If False, each problem must be square.
        The wrapper passes this option to lapjvsa.
    return_cost : bool, default True
        If True, return the array of total costs first.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        The function creates no thread pool for one worker or at most one problem.
    prefer_float32 : bool, default True
        Request a float32 kernel for each problem.
        The wrapper passes this option to lapjvsa. See lapjvsa for details.

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
        The function raises this exception if costs is not a 3D array.
        It also raises this exception for rectangular problems when extend_cost=False.

    Notes
    -----
    See lapjvsa for data types, total-cost sums, and other single solver behavior.

    Results keep the input order regardless of the thread count.
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

    if threads == 1 or B <= 1:
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

