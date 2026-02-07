"""
Regression tests for upstream gatagat/lap issues affecting extend_cost padding:

- Issue #20: Non-square matrix with infinite costs in lapjv
  https://github.com/gatagat/lap/issues/20

- Issue #21: Extension of non-square matrix with all negative values in lapjv
  https://github.com/gatagat/lap/issues/21

These tests are applied to lapx single-matrix solvers (lapjv/lapjvx/lapjvxa/lapjvs/lapjvsa)
to prevent regressions in rectangular padding/extension behavior.
"""

import numpy as np
import pytest
import lap


def _pairs_from_lapjv_x(x):
    """Convert lapjv row->col mapping x into (K,2) pairs."""
    x = np.asarray(x)
    rows = np.where(x >= 0)[0]
    cols = x[rows]
    return np.column_stack((rows, cols)).astype(np.int64, copy=False)


def _pairs_from_rows_cols(rows, cols):
    return np.column_stack((np.asarray(rows), np.asarray(cols))).astype(np.int64, copy=False)


def _normalize_pairs(pairs):
    """Sort pairs for stable comparison."""
    p = np.asarray(pairs, dtype=np.int64)
    if p.size == 0:
        return p.reshape(0, 2)
    # sort by row then col
    order = np.lexsort((p[:, 1], p[:, 0]))
    return p[order]


# ---------- Test cases (ground truth) ----------

def _case_negative():
    # [[2,4,6,8],[1,2,4,8]] - 30
    cost = (np.array([[2, 4, 6, 8], [1, 2, 4, 8]], dtype=np.float64) - 30.0)
    expected_total = -56.0
    expected_pairs = np.array([[0, 0], [1, 1]], dtype=np.int64)
    return cost, expected_total, expected_pairs


def _case_inf():
    cost = np.asarray([[np.inf, 11.0, 8.0], [8.0, np.inf, 7.0]], dtype=np.float64)
    expected_total = 16.0
    expected_pairs = np.array([[0, 2], [1, 0]], dtype=np.int64)
    return cost, expected_total, expected_pairs


# ---------- Solver adapters ----------

def _solve_pairs(solver_name, cost):
    if solver_name == "lapjv":
        total, x, y = lap.lapjv(cost, extend_cost=True, return_cost=True)
        pairs = _pairs_from_lapjv_x(x)
        return float(total), pairs

    if solver_name == "lapjvx":
        total, rows, cols = lap.lapjvx(cost, extend_cost=True, return_cost=True)
        pairs = _pairs_from_rows_cols(rows, cols)
        return float(total), pairs

    if solver_name == "lapjvxa":
        total, pairs = lap.lapjvxa(cost, extend_cost=True, return_cost=True)
        return float(total), np.asarray(pairs, dtype=np.int64)

    if solver_name == "lapjvs":
        # keep it consistent with lapjvx style
        total, rows, cols = lap.lapjvs(cost, extend_cost=True, return_cost=True, jvx_like=True)
        pairs = _pairs_from_rows_cols(rows, cols)
        return float(total), pairs

    if solver_name == "lapjvsa":
        total, pairs = lap.lapjvsa(cost, extend_cost=True, return_cost=True)
        return float(total), np.asarray(pairs, dtype=np.int64)

    raise ValueError(f"Unknown solver: {solver_name}")


SOLVERS = ["lapjv", "lapjvx", "lapjvxa", "lapjvs", "lapjvsa"]


# ---------- Negative regression (gatagat/lap #21-like) ----------

@pytest.mark.parametrize("solver", SOLVERS)
def test_extend_cost_all_negative_costs(solver):
    cost, expected_total, expected_pairs = _case_negative()
    total, pairs = _solve_pairs(solver, cost)

    np.testing.assert_allclose(total, expected_total)
    np.testing.assert_array_equal(_normalize_pairs(pairs), _normalize_pairs(expected_pairs))


# ---------- Inf regression (gatagat/lap #20-like) ----------
# If you find some solvers reject inf, you can convert this test to xfail/raises for those.

@pytest.mark.parametrize("solver", SOLVERS)
def test_extend_cost_with_inf_costs(solver):
    cost, expected_total, expected_pairs = _case_inf()
    total, pairs = _solve_pairs(solver, cost)

    np.testing.assert_allclose(total, expected_total)
    np.testing.assert_array_equal(_normalize_pairs(pairs), _normalize_pairs(expected_pairs))