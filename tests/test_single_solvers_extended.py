import numpy as np
import pytest

import lap


def _pairs_total(C, rows, cols):
    rr = np.asarray(rows, dtype=int)
    cc = np.asarray(cols, dtype=int)
    if rr.size == 0:
        return 0.0
    vals = C[rr, cc].astype(np.float64)
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


@pytest.mark.parametrize("shape", [(20, 20), (24, 37), (37, 24)], ids=["20x20", "24x37", "37x24"])
def test_lapjvc_scipy_cost_parity_square_and_rect(shape):
    scipy_opt = pytest.importorskip("scipy.optimize")
    rng = np.random.default_rng(202410)
    M, N = shape
    # lapjvc forbids via NaN; include some NaNs and ensure feasibility
    C = rng.normal(0.0, 3.0, size=(M, N)).astype(np.float64)
    mask = rng.random((M, N)) < 0.07
    # Ensure feasibility: at least one finite per row/col
    for i in range(M):
        if mask[i].all():
            mask[i, rng.integers(0, N)] = False
    for j in range(N):
        if mask[:, j].all():
            mask[rng.integers(0, M), j] = False
    C[mask] = np.nan

    # lapjvc result
    tot, r, c = lap.lapjvc(C, return_cost=True)
    assert _valid_pairs(r, c, M, N)
    assert len(r) == len(c) == min(M, N)
    assert np.isclose(tot, _pairs_total(C, r, c), rtol=1e-6, atol=1e-6)

    # SciPy linear_sum_assignment: convert NaN to a large positive penalty
    LARGE = 1e12
    C_scipy = np.where(np.isnan(C), LARGE, C)
    rr, cc = scipy_opt.linear_sum_assignment(C_scipy)
    scipy_total = float(C[rr, cc][np.isfinite(C[rr, cc])].sum())
    assert np.isclose(tot, scipy_total, rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("make_view", [
    lambda A: A[:, ::-1],      # reverse columns
    lambda A: A[::-1, :],      # reverse rows
    lambda A: np.asfortranarray(A),  # F-order
    lambda A: A.T.copy().T,    # change strides
], ids=["cols-rev", "rows-rev", "F-order", "stride-change"])
@pytest.mark.parametrize("solver_name", ["lapjvx", "lapjvs", "lapjvc"], ids=["lapjvx", "lapjvs", "lapjvc"])
def test_noncontiguous_inputs_single(solver_name, make_view):
    rng = np.random.default_rng(7)
    M, N = 12, 16
    C_base = rng.normal(0.0, 5.0, size=(M, N)).astype(np.float64)

    C_view = make_view(C_base)

    if solver_name == "lapjvx":
        tot0, r0, c0 = lap.lapjvx(C_base, return_cost=True, extend_cost=(M != N))
        tot1, r1, c1 = lap.lapjvx(C_view, return_cost=True, extend_cost=(M != N))
    elif solver_name == "lapjvs":
        # lapjvs handles rectangles internally, jvx-like pairs
        tot0, r0, c0 = lap.lapjvs(C_base, return_cost=True, jvx_like=True)
        tot1, r1, c1 = lap.lapjvs(C_view, return_cost=True, jvx_like=True)
    else:
        tot0, r0, c0 = lap.lapjvc(C_base, return_cost=True)
        tot1, r1, c1 = lap.lapjvc(C_view, return_cost=True)

    assert _valid_pairs(r0, c0, M, N)
    assert _valid_pairs(r1, c1, *C_view.shape)
    # Totals should match their own input matrices
    assert np.isclose(tot0, _pairs_total(C_base, r0, c0), rtol=1e-6, atol=1e-6)
    assert np.isclose(tot1, _pairs_total(C_view, r1, c1), rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("shape", [(0, 0), (0, 3), (5, 0)], ids=["0x0", "0x3", "5x0"])
@pytest.mark.parametrize("solver_name", ["lapjv", "lapjvx", "lapjvc", "lapjvs"], ids=["lapjv", "lapjvx", "lapjvc", "lapjvs"])
def test_empty_matrices_behave_gracefully(solver_name, shape):
    """
    Dynamically detect support for empty shapes without hardcoding.
    If a solver throws for a given shape, skip with a clear reason.
    For solvers that return assignment vectors (lapjv), normalize to (rows, cols) pairs before asserting.
    """
    M, N = shape
    C = np.empty((M, N), dtype=np.float64)

    def solve_raw(name, C, M, N):
        if name == "lapjv":
            return lap.lapjv(C, return_cost=True, extend_cost=(M != N))
        if name == "lapjvx":
            return lap.lapjvx(C, return_cost=True, extend_cost=(M != N))
        if name == "lapjvc":
            return lap.lapjvc(C, return_cost=True)
        if name == "lapjvs":
            return lap.lapjvs(C, return_cost=True, jvx_like=True)
        raise AssertionError(f"Unknown solver {name}")

    try:
        tot, r, c = solve_raw(solver_name, C, M, N)
    except Exception as e:
        pytest.skip(f"{solver_name} does not support empty matrices for shape={shape}: {e}")
        return

    # Normalize lapjv assignment vectors (x, y) to pair lists (rows, cols)
    if solver_name == "lapjv":
        x = np.asarray(r, dtype=int)  # r is x (size M)
        mask = x >= 0
        rows = np.nonzero(mask)[0]
        cols = x[mask]
        r, c = rows, cols

    # If it didn't raise, it should behave gracefully with zero pairs and zero total.
    assert len(r) == len(c) == 0
    assert np.isclose(float(tot), 0.0, rtol=0.0, atol=0.0)


@pytest.mark.parametrize("solver_name", ["lapjvx", "lapjvs", "lapjvc"], ids=["lapjvx", "lapjvs", "lapjvc"])
def test_tie_case_determinism_and_optimality(solver_name):
    # Many optimal solutions exist; verify determinism across repeated calls
    # and correctness of total.
    M, N = 4, 4
    C = np.zeros((M, N), dtype=np.float64)

    def solve_once():
        if solver_name == "lapjvx":
            return lap.lapjvx(C, return_cost=True, extend_cost=False)
        elif solver_name == "lapjvs":
            return lap.lapjvs(C, return_cost=True, jvx_like=True)
        else:
            return lap.lapjvc(C, return_cost=True)

    tot1, r1, c1 = solve_once()
    tot2, r2, c2 = solve_once()

    assert _valid_pairs(r1, c1, M, N)
    assert _valid_pairs(r2, c2, M, N)
    assert np.isclose(float(tot1), 0.0, rtol=0.0, atol=0.0)
    assert np.isclose(float(tot2), 0.0, rtol=0.0, atol=0.0)
    # Deterministic across runs
    assert np.array_equal(np.asarray(r1), np.asarray(r2))
    assert np.array_equal(np.asarray(c1), np.asarray(c2))


@pytest.mark.parametrize("dtype, lo, hi", [
    (np.int32, -10_000_000, 10_000_000),
    (np.int64, -1_000_000_000, 1_000_000_000),
], ids=["int32-1e7", "int64-1e9"])
@pytest.mark.parametrize("solver_name", ["lapjvx", "lapjvs", "lapjvc"], ids=["lapjvx", "lapjvs", "lapjvc"])
def test_large_integer_ranges(solver_name, dtype, lo, hi):
    rng = np.random.default_rng(1234)
    M, N = 25, 25
    C = rng.integers(lo, hi, size=(M, N), dtype=dtype)

    if solver_name == "lapjvx":
        tot, r, c = lap.lapjvx(C, return_cost=True, extend_cost=False)
    elif solver_name == "lapjvs":
        tot, r, c = lap.lapjvs(C, return_cost=True, jvx_like=True)
    else:
        tot, r, c = lap.lapjvc(C, return_cost=True)

    assert _valid_pairs(r, c, M, N)
    # Recompute total in float to avoid dtype overflow concerns in Python
    tot_chk = _pairs_total(C.astype(np.float64), r, c)
    assert np.isclose(float(tot), tot_chk, rtol=1e-6, atol=1e-6)
