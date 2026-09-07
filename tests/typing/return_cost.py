"""Static API checks; run with pyright, not as a runtime benchmark.

The expected-error lines must keep producing diagnostics: Pyright reports an
unnecessary ignore if an invalid call or incorrect unpacking becomes accepted.
"""
# pyright: reportUnnecessaryTypeIgnoreComment=true

from typing import List, Tuple, Union

import lap
import numpy as np
import numpy.typing as npt
from typing_extensions import assert_type


def check_lapjv(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjv(cost),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjv(cost, return_cost=True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjv(cost, return_cost=False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjv(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )
    assert_type(
        lap.lapjv(cost, False, np.inf, True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjv(cost, False, np.inf, False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjv(cost, False, np.inf, flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjv(cost, return_cost="yes")  # type: ignore
    lap.lapjv(cost, unknown_option=True)  # type: ignore
    lap.lapjv()  # type: ignore
    lap.lapjv(cost, False, np.inf, True, None)  # type: ignore
    _, _ = lap.lapjv(cost)  # type: ignore


def check_lapjvc(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvc(cost),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvc(cost, return_cost=True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvc(cost, return_cost=False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvc(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )
    assert_type(
        lap.lapjvc(cost, True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvc(cost, False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvc(cost, flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvc(cost, return_cost="yes")  # type: ignore
    lap.lapjvc(cost, unknown_option=True)  # type: ignore
    lap.lapjvc()  # type: ignore
    lap.lapjvc(cost, True, None)  # type: ignore
    _, _ = lap.lapjvc(cost)  # type: ignore


def check_lapjvx(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvx(cost),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvx(cost, return_cost=True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvx(cost, return_cost=False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvx(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )
    assert_type(
        lap.lapjvx(cost, False, np.inf, True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvx(cost, False, np.inf, False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvx(cost, False, np.inf, flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvx(cost, return_cost="yes")  # type: ignore
    lap.lapjvx(cost, unknown_option=True)  # type: ignore
    lap.lapjvx()  # type: ignore
    lap.lapjvx(cost, False, np.inf, True, None)  # type: ignore
    _, _ = lap.lapjvx(cost)  # type: ignore


def check_lapjvxa(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvxa(cost),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvxa(cost, return_cost=True),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvxa(cost, return_cost=False),
        np.ndarray,
    )
    assert_type(
        lap.lapjvxa(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray], np.ndarray],
    )
    assert_type(
        lap.lapjvxa(cost, False, np.inf, True),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvxa(cost, False, np.inf, False),
        np.ndarray,
    )
    assert_type(
        lap.lapjvxa(cost, False, np.inf, flag),
        Union[Tuple[float, np.ndarray], np.ndarray],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvxa(cost, return_cost="yes")  # type: ignore
    lap.lapjvxa(cost, unknown_option=True)  # type: ignore
    lap.lapjvxa()  # type: ignore
    lap.lapjvxa(cost, False, np.inf, True, None)  # type: ignore
    _, _, _ = lap.lapjvxa(cost)  # type: ignore


def check_lapjvs(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvs(cost),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvs(cost, return_cost=True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvs(cost, return_cost=False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvs(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )
    assert_type(
        lap.lapjvs(cost, None, True, False, False),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvs(cost, None, False, False, False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapjvs(cost, None, flag, False, False),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvs(cost, return_cost="yes")  # type: ignore
    lap.lapjvs(cost, unknown_option=True)  # type: ignore
    lap.lapjvs()  # type: ignore
    lap.lapjvs(cost, None, True, False, False, None)  # type: ignore
    _, _ = lap.lapjvs(cost)  # type: ignore


def check_lapjvsa(
    cost: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvsa(cost),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvsa(cost, return_cost=True),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvsa(cost, return_cost=False),
        np.ndarray,
    )
    assert_type(
        lap.lapjvsa(cost, return_cost=flag),
        Union[Tuple[float, np.ndarray], np.ndarray],
    )
    assert_type(
        lap.lapjvsa(cost, None, True, False),
        Tuple[float, np.ndarray],
    )
    assert_type(
        lap.lapjvsa(cost, None, False, False),
        np.ndarray,
    )
    assert_type(
        lap.lapjvsa(cost, None, flag, False),
        Union[Tuple[float, np.ndarray], np.ndarray],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvsa(cost, return_cost="yes")  # type: ignore
    lap.lapjvsa(cost, unknown_option=True)  # type: ignore
    lap.lapjvsa()  # type: ignore
    lap.lapjvsa(cost, None, True, False, None)  # type: ignore
    _, _, _ = lap.lapjvsa(cost)  # type: ignore


def check_lapjvx_batch(
    costs: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvx_batch(costs),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, return_cost=True),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, return_cost=False),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, return_cost=flag),
        Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]],
    )
    assert_type(
        lap.lapjvx_batch(costs, False, np.inf, True, None),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, False, np.inf, False, None),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, False, np.inf, flag, None),
        Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]],
    )
    assert_type(
        lap.lapjvx_batch(costs, return_cost=False, n_threads=None),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvx_batch(costs, return_cost=True, n_threads=None),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvx_batch(costs, return_cost="yes")  # type: ignore
    lap.lapjvx_batch(costs, unknown_option=True)  # type: ignore
    lap.lapjvx_batch()  # type: ignore
    lap.lapjvx_batch(costs, False, np.inf, True, None, None)  # type: ignore
    _, _ = lap.lapjvx_batch(costs)  # type: ignore


def check_lapjvxa_batch(
    costs: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvxa_batch(costs),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvxa_batch(costs, return_cost=True),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvxa_batch(costs, return_cost=False),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvxa_batch(costs, return_cost=flag),
        Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvxa_batch(costs, False, np.inf, True, None),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvxa_batch(costs, False, np.inf, False, None),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvxa_batch(costs, False, np.inf, flag, None),
        Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvxa_batch(costs, return_cost=False, n_threads=None),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvxa_batch(costs, return_cost=True, n_threads=None),
        Tuple[np.ndarray, List[np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvxa_batch(costs, return_cost="yes")  # type: ignore
    lap.lapjvxa_batch(costs, unknown_option=True)  # type: ignore
    lap.lapjvxa_batch()  # type: ignore
    lap.lapjvxa_batch(costs, False, np.inf, True, None, None)  # type: ignore
    _, _, _ = lap.lapjvxa_batch(costs)  # type: ignore


def check_lapjvs_batch(
    costs: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvs_batch(costs),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, return_cost=True),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, return_cost=False),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, return_cost=flag),
        Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]],
    )
    assert_type(
        lap.lapjvs_batch(costs, False, True, None, False),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, False, False, None, False),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, False, flag, None, False),
        Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]],
    )
    assert_type(
        lap.lapjvs_batch(costs, return_cost=False, n_threads=None),
        Tuple[List[np.ndarray], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvs_batch(costs, return_cost=True, n_threads=None),
        Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvs_batch(costs, return_cost="yes")  # type: ignore
    lap.lapjvs_batch(costs, unknown_option=True)  # type: ignore
    lap.lapjvs_batch()  # type: ignore
    lap.lapjvs_batch(costs, False, True, None, False, None)  # type: ignore
    _, _ = lap.lapjvs_batch(costs)  # type: ignore


def check_lapjvsa_batch(
    costs: np.ndarray, flag: bool,
) -> None:
    assert_type(
        lap.lapjvsa_batch(costs),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvsa_batch(costs, return_cost=True),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvsa_batch(costs, return_cost=False),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvsa_batch(costs, return_cost=flag),
        Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvsa_batch(costs, False, True, None, False),
        Tuple[np.ndarray, List[np.ndarray]],
    )
    assert_type(
        lap.lapjvsa_batch(costs, False, False, None, False),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvsa_batch(costs, False, flag, None, False),
        Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]],
    )
    assert_type(
        lap.lapjvsa_batch(costs, return_cost=False, n_threads=None),
        List[np.ndarray],
    )
    assert_type(
        lap.lapjvsa_batch(costs, return_cost=True, n_threads=None),
        Tuple[np.ndarray, List[np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapjvsa_batch(costs, return_cost="yes")  # type: ignore
    lap.lapjvsa_batch(costs, unknown_option=True)  # type: ignore
    lap.lapjvsa_batch()  # type: ignore
    lap.lapjvsa_batch(costs, False, True, None, False, None)  # type: ignore
    _, _, _ = lap.lapjvsa_batch(costs)  # type: ignore


def check_lapmod(
    cc: npt.NDArray[np.float64], ii: npt.NDArray[np.int32],
    kk: npt.NDArray[np.int32], flag: bool,
) -> None:
    assert_type(
        lap.lapmod(2, cc, ii, kk),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, return_cost=True),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, return_cost=False),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, return_cost=flag),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, True, True, lap.FP_DYNAMIC),
        Tuple[float, np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, True, False, lap.FP_DYNAMIC),
        Tuple[np.ndarray, np.ndarray],
    )
    assert_type(
        lap.lapmod(2, cc, ii, kk, True, flag, lap.FP_DYNAMIC),
        Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]],
    )

    # Invalid calls and tuple sizes must still be rejected.
    lap.lapmod(2, cc, ii, kk, return_cost="yes")  # type: ignore
    lap.lapmod(2.5, cc, ii, kk)  # type: ignore
    lap.lapmod(2, cc, ii, kk, unknown_option=True)  # type: ignore
    lap.lapmod()  # type: ignore
    lap.lapmod(2, cc, ii, kk, True, True, lap.FP_DYNAMIC, None)  # type: ignore
    _, _ = lap.lapmod(2, cc, ii, kk)  # type: ignore

    # NumPy integer sizes are supported by the wrapper's index conversion.
    for n in (np.int32(2), np.int64(2), np.uint32(2), np.uint64(2)):
        assert_type(
            lap.lapmod(n, cc, ii, kk),
            Tuple[float, np.ndarray, np.ndarray],
        )
        assert_type(
            lap.lapmod(n, cc, ii, kk, return_cost=False),
            Tuple[np.ndarray, np.ndarray],
        )
