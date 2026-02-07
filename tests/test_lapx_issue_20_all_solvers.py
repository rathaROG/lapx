"""
Regression test for Issue #20:
Solvers with extend_cost=True may produce incorrect assignments on non-square matrices
with large blocking costs (float32).

https://github.com/rathaROG/lapx/issues/20
"""

import numpy as np
import pytest
import lap


DTYPES = (np.float32, np.float64)


def _make_cost(dtype):
    # 11 detections x 12 tracks (rectangular)
    cost = np.full((11, 12), 1e6, dtype=dtype)

    # small diagonal costs
    for i in range(11):
        cost[i, i] = dtype(0.01 * (i + 1))

    # uniquely forced match (0,0)
    cost[0, 0] = dtype(0.0057)
    cost[0, 1:] = dtype(1e6)  # row 0 can only match col 0
    cost[1:, 0] = dtype(1e6)  # col 0 can only match row 0
    return cost


def _assert_total_cost_not_blocked(total_cost):
    # For the intended solution, total cost is ~0.6657 (well under 10)
    assert np.isfinite(total_cost), f"Expected finite total_cost, got {total_cost}"
    assert total_cost < 10.0, f"Total cost too large, likely used blocked edges: {total_cost}"


def _assert_row0_assigned_to_col0(col_for_row0, cost):
    assert int(col_for_row0) == 0, f"Expected row 0 -> col 0, got row 0 -> col {int(col_for_row0)}"
    assert float(cost[0, int(col_for_row0)]) < 1e5, (
        f"Row 0 matched to a blocked edge: cost[0, {int(col_for_row0)}] = {float(cost[0, int(col_for_row0)])}"
    )


def _assert_row0_col0_from_pairs(assignments, cost):
    a = np.asarray(assignments)
    assert a.ndim == 2 and a.shape[1] == 2, f"Expected (K,2) assignments, got shape {a.shape}"
    rows0 = a[a[:, 0] == 0]
    assert len(rows0) == 1, f"Expected exactly one assignment for row 0, got {rows0}"
    _assert_row0_assigned_to_col0(rows0[0, 1], cost)


def _assert_row0_col0_from_x(x, cost):
    x = np.asarray(x)
    assert x.ndim == 1, f"Expected 1D x, got shape {x.shape}"
    _assert_row0_assigned_to_col0(x[0], cost)


@pytest.mark.parametrize("dtype", DTYPES)
def test_lapjv_extend_cost_true(dtype):
    cost = _make_cost(dtype)
    total_cost, x, y = lap.lapjv(cost, extend_cost=True, return_cost=True)
    _assert_row0_col0_from_x(x, cost)
    _assert_total_cost_not_blocked(total_cost)


@pytest.mark.parametrize("dtype", DTYPES)
def test_lapjvx_extend_cost_true(dtype):
    cost = _make_cost(dtype)
    total_cost, rows, cols = lap.lapjvx(cost, extend_cost=True, return_cost=True)

    rows = np.asarray(rows)
    cols = np.asarray(cols)
    idx = np.where(rows == 0)[0]
    assert len(idx) == 1, f"Expected row 0 to appear exactly once in rows, got indices {idx}"
    _assert_row0_assigned_to_col0(cols[idx[0]], cost)

    _assert_total_cost_not_blocked(total_cost)


@pytest.mark.parametrize("dtype", DTYPES)
def test_lapjvxa_extend_cost_true(dtype):
    cost = _make_cost(dtype)
    total_cost, assignments = lap.lapjvxa(cost, extend_cost=True, return_cost=True)
    _assert_row0_col0_from_pairs(assignments, cost)
    _assert_total_cost_not_blocked(total_cost)


@pytest.mark.parametrize("dtype", DTYPES)
def test_lapjvs_extend_cost_true_jvx_like(dtype):
    cost = _make_cost(dtype)
    total_cost, rows, cols = lap.lapjvs(cost, extend_cost=True, return_cost=True, jvx_like=True)

    rows = np.asarray(rows)
    cols = np.asarray(cols)
    idx = np.where(rows == 0)[0]
    assert len(idx) == 1, f"Expected row 0 to appear exactly once in rows, got indices {idx}"
    _assert_row0_assigned_to_col0(cols[idx[0]], cost)

    _assert_total_cost_not_blocked(total_cost)


@pytest.mark.parametrize("dtype", DTYPES)
def test_lapjvsa_extend_cost_true(dtype):
    cost = _make_cost(dtype)
    total_cost, assignments = lap.lapjvsa(cost, extend_cost=True, return_cost=True)
    _assert_row0_col0_from_pairs(assignments, cost)
    _assert_total_cost_not_blocked(total_cost)
