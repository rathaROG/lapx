import numpy as np
import pytest

from lap import lapjvxa, lapjvsa


def _pairs_total(C, rows, cols):
    vals = C[np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)].astype(np.float64)
    vals = vals[np.isfinite(vals)]
    return float(vals.sum()) if vals.size else 0.0


def _valid_pairs(rows, cols, M, N):
    if len(rows) != len(cols):
        return False
    rr = np.asarray(rows, dtype=int)
    cc = np.asarray(cols, dtype=int)
    if np.any(rr < 0) or np.any(rr >= M) or np.any(cc < 0) or np.any(cc >= N):
        return False
    return len(set(rr.tolist())) == len(rr) and len(set(cc.tolist())) == len(cc)


@pytest.mark.parametrize("fn_name", ["lapjvxa", "lapjvsa"])
def test_assignments_return_shape_and_total(fn_name):
    rng = np.random.default_rng(10)
    M, N = 15, 22
    C = rng.normal(0.0, 5.0, size=(M, N)).astype(np.float64)

    fn = lapjvxa if fn_name == "lapjvxa" else lapjvsa
    tot, assignments = fn(C, extend_cost=True, return_cost=True)

    # assignments is (K, 2)
    assert isinstance(assignments, np.ndarray) and assignments.ndim == 2 and assignments.shape[1] == 2
    rows = assignments[:, 0].astype(int)
    cols = assignments[:, 1].astype(int)
    assert _valid_pairs(rows, cols, M, N)
    assert len(rows) == len(cols) == min(M, N)
    assert np.isfinite(C[rows, cols]).all()
    assert np.isclose(tot, _pairs_total(C, rows, cols), rtol=1e-6, atol=1e-6)
