import numpy as np
import pytest

from lap import lapjvx, lapjv


def total_from_pairs(C, rows, cols):
    rr = np.asarray(rows, dtype=int)
    cc = np.asarray(cols, dtype=int)
    vals = C[rr, cc].astype(np.float64)
    vals = vals[np.isfinite(vals)]
    return float(vals.sum()) if vals.size else 0.0


def is_valid_matching(rows, cols, M, N):
    # No duplicates, within bounds, and lengths match
    if len(rows) != len(cols):
        return False
    rr = np.asarray(rows, dtype=int)
    cc = np.asarray(cols, dtype=int)
    if np.any(rr < 0) or np.any(rr >= M) or np.any(cc < 0) or np.any(cc >= N):
        return False
    return len(set(rr.tolist())) == len(rr) and len(set(cc.tolist())) == len(cc)


def test_small_known_square_cases():
    # Classic exact 3x3
    C = np.array([[1000, 4, 1],
                  [1, 1000, 3],
                  [5, 1, 1000]], dtype=np.float64)
    tot, r, c = lapjvx(C, extend_cost=False, return_cost=True)
    assert is_valid_matching(r, c, *C.shape)
    assert np.isclose(tot, C[0, 2] + C[1, 0] + C[2, 1])  # 1 + 1 + 1 = 3
    assert set(zip(r.tolist(), c.tolist())) == {(0, 2), (1, 0), (2, 1)}

    # Another small 2x2 with ties
    C2 = np.array([[0, 0],
                   [0, 0]], dtype=np.float64)
    tot2, r2, c2 = lapjvx(C2, extend_cost=False, return_cost=True)
    assert is_valid_matching(r2, c2, *C2.shape)
    assert np.isclose(tot2, 0.0)
    assert len(r2) == 2  # perfect matching


@pytest.mark.parametrize("M,N", [(2, 4), (5, 3), (7, 11)])
def test_rectangular_extend_cost(M, N):
    rng = np.random.default_rng(0)
    C = rng.normal(size=(M, N)).astype(np.float64)
    tot, r, c = lapjvx(C, extend_cost=True, return_cost=True)
    assert is_valid_matching(r, c, M, N)
    assert len(r) == len(c) == min(M, N)
    assert np.isclose(tot, total_from_pairs(C, r, c), rtol=1e-6, atol=1e-6)

    # Ensure a non-extend rectangular raises or needs extend_cost
    if M != N:
        with pytest.raises(Exception):
            _ = lapjvx(C, extend_cost=False, return_cost=True)


def test_forbidden_inf_float():
    rng = np.random.default_rng(1)
    M, N = 10, 14
    C = rng.normal(size=(M, N)).astype(np.float64)

    # Forbid ~10% entries with +Inf but keep feasibility per row/col
    mask = rng.random((M, N)) < 0.1
    # Ensure at least one finite per row/col
    for i in range(M):
        if mask[i].all():
            mask[i, rng.integers(0, N)] = False
    for j in range(N):
        if mask[:, j].all():
            mask[rng.integers(0, M), j] = False
    C[mask] = np.inf

    tot, r, c = lapjvx(C, extend_cost=True, return_cost=True)
    assert is_valid_matching(r, c, M, N)
    # Matched entries must be finite
    assert np.all(np.isfinite(C[np.asarray(r), np.asarray(c)]))
    # Totals must match recomputed
    assert np.isclose(tot, total_from_pairs(C, r, c), rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("dtype", [np.int32, np.int64, np.float32, np.float64])
def test_integer_and_float_inputs(dtype):
    rng = np.random.default_rng(2)
    M, N = 16, 12
    # Keep magnitudes moderate for integers
    if np.issubdtype(dtype, np.integer):
        C = rng.integers(-50, 50, size=(M, N)).astype(dtype)
    else:
        C = rng.normal(0.0, 10.0, size=(M, N)).astype(dtype)

    tot, r, c = lapjvx(C, extend_cost=True, return_cost=True)
    assert is_valid_matching(r, c, M, N)
    assert np.isclose(tot, total_from_pairs(C, r, c), rtol=1e-5, atol=1e-5)


def test_invariance_constant_shift():
    rng = np.random.default_rng(3)
    M, N = 20, 35
    C = rng.normal(0.0, 5.0, size=(M, N)).astype(np.float64)

    tot0, r0, c0 = lapjvx(C, extend_cost=True, return_cost=True)
    K = 7.25
    tot1, r1, c1 = lapjvx(C + K, extend_cost=True, return_cost=True)

    # Adding a constant to all entries should shift the total by r*K, where r=min(M,N)
    r = min(M, N)
    assert np.isclose(tot1, tot0 + r * K, rtol=1e-6, atol=1e-6)
    # The assignment can change under ties; don't enforce equality of pairs.


def test_crosscheck_lapjv_total_matches_on_square():
    rng = np.random.default_rng(4)
    n = 32
    C = rng.normal(0.0, 10.0, size=(n, n)).astype(np.float64)

    tot_vx, rvx, cvx = lapjvx(C, extend_cost=False, return_cost=True)
    tot_jv, x, y = lapjv(C, return_cost=True)

    # Both should produce the same optimal total
    assert np.isclose(tot_vx, tot_jv, rtol=1e-8, atol=1e-8)

    # Consistency checks for lapjvx's returned pairs
    assert is_valid_matching(rvx, cvx, n, n)
    assert np.isclose(tot_vx, total_from_pairs(C, rvx, cvx), rtol=1e-8, atol=1e-8)


scipy_available = True
try:
    from scipy.optimize import linear_sum_assignment
except Exception:
    scipy_available = False


@pytest.mark.skipif(not scipy_available, reason="SciPy not available for cross-check")
@pytest.mark.parametrize("M,N", [(20, 20), (24, 37), (60, 30)])
def test_crosscheck_scipy_totals(M, N):
    rng = np.random.default_rng(5)
    C = rng.normal(0.0, 10.0, size=(M, N)).astype(np.float64)

    # Our solver
    tot_vx, rvx, cvx = lapjvx(C, extend_cost=True, return_cost=True)

    # SciPy baseline (convert NaN to +Inf if ever present)
    Cs = C.astype(np.float64)
    Cs[~np.isfinite(Cs)] = np.inf
    rr, cc = linear_sum_assignment(Cs)
    tot_sp = float(Cs[rr, cc].sum())

    assert np.isclose(tot_vx, tot_sp, rtol=1e-6, atol=1e-6)
    assert is_valid_matching(rvx, cvx, M, N)
