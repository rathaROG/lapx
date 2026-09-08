# Copyright (c) 2026 Ratha SIV | MIT License

import numpy as np
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from ._batch_utils import _normalize_threads
from ._lapjvx import lapjvx as _lapjvx_single  # type: ignore
from ._lapjvx import lapjvxa as _lapjvxa_single  # type: ignore


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    from typing import overload
    from typing_extensions import Literal

    @overload
    def lapjvx_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
    ) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvx_batch(
        costs: np.ndarray,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvx_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def lapjvx_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
    ) -> Union[
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
        Tuple[List[np.ndarray], List[np.ndarray]],
    ]: ...


def lapjvx_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
    n_threads: Optional[int] = 0,
) -> Union[
    Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    Tuple[List[np.ndarray], List[np.ndarray]]
]:
    """Solve a batch of cost matrices with lapjvx.

    It runs lapjvx on each (N, M) slice of the (B, N, M) batch.
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
        The wrapper passes this option to lapjvx.
    cost_limit : float, default np.inf
        This threshold limits assignments for each problem.
        The wrapper passes it to lapjvx.
        The value must be finite or positive infinity.
    return_cost : bool, default True
        If True, return the array of total costs first.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        The function creates no thread pool for one worker or at most one problem.

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
    See lapjvx for the single solver behavior and cost_limit rules.

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
            total, rows, cols = _lapjvx_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=True
            )
            return bi, total, rows, cols
        else:
            rows, cols = _lapjvx_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=False
            )
            return bi, None, rows, cols

    if threads == 1 or B <= 1:
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


# Describe return_cost for type checkers without registering overloads at runtime.
if TYPE_CHECKING:
    @overload
    def lapjvxa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
    ) -> Tuple[np.ndarray, List[np.ndarray]]: ...

    @overload
    def lapjvxa_batch(
        costs: np.ndarray,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
    ) -> List[np.ndarray]: ...

    @overload
    def lapjvxa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
    ) -> List[np.ndarray]: ...

    @overload
    def lapjvxa_batch(
        costs: np.ndarray,
        extend_cost: bool = False,
        cost_limit: float = np.inf,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
    ) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]: ...


def lapjvxa_batch(
    costs: np.ndarray,
    extend_cost: bool = False,
    cost_limit: float = np.inf,
    return_cost: bool = True,
    n_threads: Optional[int] = 0,
) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]:
    """Solve a batch of cost matrices with lapjvxa.

    The function returns an array of assignment pairs with shape (K_b, 2) for each problem.

    It runs lapjvxa on each (N, M) slice of the (B, N, M) batch.
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
        The wrapper passes this option to lapjvxa.
    cost_limit : float, default np.inf
        This threshold limits assignments for each problem.
        The wrapper passes it to lapjvxa.
        The value must be finite or positive infinity.
    return_cost : bool, default True
        If True, return the array of total costs first.
    n_threads : int or None, default 0
        This option sets the number of worker threads:

        - 0 or None: Use os.cpu_count(). If the CPU count is unavailable, use 1.
        - Negative values: Use one worker.
        - Positive values: Use at most this many workers, limited to the batch size.

        The function creates no thread pool for one worker or at most one problem.

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
    See lapjvxa for the single solver behavior and cost_limit rules.

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
            total, pairs = _lapjvxa_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=True
            )
            return bi, total, pairs
        else:
            pairs = _lapjvxa_single(
                a2d, extend_cost=extend_cost, cost_limit=cost_limit, return_cost=False
            )
            return bi, None, pairs

    if threads == 1 or B <= 1:
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
