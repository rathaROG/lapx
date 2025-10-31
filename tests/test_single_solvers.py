import numpy as np
import pytest

from lap import lapjv, lapjvx, lapjvc, lapjvs


def _pairs_total(C, rows, cols):
    rr = np.asarray(rows, dtype=int)
    cc = np.asarray(cols, dtype=int)
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


class SolverAdapter:
    def __init__(self, name, solver_fn, forbid_kind, needs_extend=False, uses_jvx_like=False):
        """
        forbid_kind: "inf" or "nan"
        needs_extend: if True, pass extend_cost=True for rectangular cases
        uses_jvx_like: if True, return style already (rows, cols)
        """
        self.name = name
        self.solver_fn = solver_fn
        self.forbid_kind = forbid_kind
        self.needs_extend = needs_extend
        self.uses_jvx_like = uses_jvx_like

    def solve(self, C):
        """Return total, rows, cols normalized."""
        M, N = C.shape
        if self.name == "lapjv":
            tot, x, y = lapjv(C, return_cost=True, extend_cost=(M != N))
            # x: size M, x[i] == assigned column or -1
            rows = [i for i in range(M) if x[i] >= 0]
            cols = [x[i] for i in range(M) if x[i] >= 0]
            return float(tot), np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)

        if self.name == "lapjvx":
            tot, rows, cols = lapjvx(C, return_cost=True, extend_cost=(M != N))
            return float(tot), np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)

        if self.name == "lapjvc":
            # lapjvc does not take extend_cost; handles rectangular internally
            tot, rows, cols = lapjvc(C, return_cost=True)
            return float(tot), np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)

        if self.name == "lapjvs":
            # jvx-like pairs
            tot, rows, cols = lapjvs(C, return_cost=True, jvx_like=True)
            return float(tot), np.asarray(rows, dtype=int), np.asarray(cols, dtype=int)

        raise ValueError(f"Unknown solver {self.name}")


SOLVERS = [
    SolverAdapter("lapjv", lapjv, forbid_kind="inf", needs_extend=True),
    SolverAdapter("lapjvx", lapjvx, forbid_kind="inf", needs_extend=True, uses_jvx_like=True),
    SolverAdapter("lapjvc", lapjvc, forbid_kind="nan", needs_extend=False, uses_jvx_like=True),
    SolverAdapter("lapjvs", lapjvs, forbid_kind="inf", needs_extend=False, uses_jvx_like=True),
]


@pytest.mark.parametrize("adapter", SOLVERS, ids=[s.name for s in SOLVERS])
def test_small_known_square(adapter: SolverAdapter):
    C = np.array([[1000, 4, 1],
                  [1, 1000, 3],
                  [5, 1, 1000]], dtype=np.float64)
    tot, r, c = adapter.solve(C)
    assert _valid_pairs(r, c, *C.shape)
    # The optimal known total is 3 (pairs: (0,2),(1,0),(2,1))
    assert np.isclose(tot, C[0, 2] + C[1, 0] + C[2, 1], rtol=1e-8, atol=1e-8)
    assert len(r) == len(c) == 3


@pytest.mark.parametrize("adapter", SOLVERS, ids=[s.name for s in SOLVERS])
@pytest.mark.parametrize("M,N", [(2, 4), (5, 3), (7, 11)])
def test_rectangular_random(adapter: SolverAdapter, M, N):
    rng = np.random.default_rng(0)
    C = rng.normal(size=(M, N)).astype(np.float64)
    tot, r, c = adapter.solve(C)
    assert _valid_pairs(r, c, M, N)
    assert len(r) == len(c) == min(M, N)
    assert np.isclose(tot, _pairs_total(C, r, c), rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("adapter", SOLVERS, ids=[s.name for s in SOLVERS])
def test_forbidden_entries(adapter: SolverAdapter):
    rng = np.random.default_rng(1)
    M, N = 12, 16
    C = rng.normal(0.0, 5.0, size=(M, N)).astype(np.float64)

    # Forbid ~10%, but keep at least one feasible per row/col
    mask = rng.random((M, N)) < 0.1
    for i in range(M):
        if mask[i].all():
            mask[i, rng.integers(0, N)] = False
    for j in range(N):
        if mask[:, j].all():
            mask[rng.integers(0, M), j] = False

    if adapter.forbid_kind == "inf":
        C[mask] = np.inf
    else:
        C[mask] = np.nan

    tot, r, c = adapter.solve(C)
    assert _valid_pairs(r, c, M, N)
    # Matched entries must be finite
    assert np.all(np.isfinite(C[np.asarray(r), np.asarray(c)]))
    # Totals match recomputed
    assert np.isclose(tot, _pairs_total(C, r, c), rtol=1e-6, atol=1e-6)


@pytest.mark.parametrize("adapter", SOLVERS, ids=[s.name for s in SOLVERS])
@pytest.mark.parametrize("dtype", [np.int32, np.int64, np.float32, np.float64])
def test_integer_and_float_inputs(adapter: SolverAdapter, dtype):
    rng = np.random.default_rng(2)
    M, N = 16, 12
    if np.issubdtype(dtype, np.integer):
        C = rng.integers(-50, 50, size=(M, N)).astype(dtype)
    else:
        C = rng.normal(0.0, 10.0, size=(M, N)).astype(dtype)

    tot, r, c = adapter.solve(C.astype(dtype))
    assert _valid_pairs(r, c, M, N)
    assert np.isclose(tot, _pairs_total(C, r, c), rtol=1e-5, atol=1e-5)


@pytest.mark.parametrize("adapter", SOLVERS, ids=[s.name for s in SOLVERS])
def test_invariance_constant_shift(adapter: SolverAdapter):
    rng = np.random.default_rng(3)
    M, N = 20, 35
    C = rng.normal(0.0, 5.0, size=(M, N)).astype(np.float64)

    tot0, r0, c0 = adapter.solve(C)
    K = 7.25
    tot1, r1, c1 = adapter.solve(C + K)
    r = min(M, N)
    assert np.isclose(tot1, tot0 + r * K, rtol=1e-6, atol=1e-6)


def test_crosscheck_totals_between_solvers_square():
    rng = np.random.default_rng(4)
    n = 24
    C = rng.normal(0.0, 10.0, size=(n, n)).astype(np.float64)

    totals = []
    for adapter in SOLVERS:
        tot, r, c = adapter.solve(C)
        totals.append(tot)
        assert _valid_pairs(r, c, n, n)
        assert np.isclose(tot, _pairs_total(C, r, c), rtol=1e-8, atol=1e-8)

    # All solvers should agree on the optimal total
    for t in totals[1:]:
        assert np.isclose(t, totals[0], rtol=1e-8, atol=1e-8)
