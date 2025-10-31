import numpy as np
import pytest
import lap


def _gen_batch(B, M, N, seed=0):
    rng = np.random.RandomState(seed)
    return rng.randn(B, M, N).astype(np.float64)


@pytest.mark.parametrize("make_view", [
    lambda A: A[:, :, ::-1],       # reverse columns per matrix
    lambda A: A[:, ::-1, :],       # reverse rows per matrix
    lambda A: np.asfortranarray(A) # F-order batch buffer
], ids=["cols-rev", "rows-rev", "F-order"])
@pytest.mark.parametrize("B,M,N", [(2, 7, 9), (3, 6, 6)])
@pytest.mark.parametrize("solver", ["lapjvx_batch", "lapjvsa_batch", "lapjvs_batch"], ids=["lapjvx_batch", "lapjvsa_batch", "lapjvs_batch"])
def test_batch_vs_single_on_noncontiguous_inputs(solver, B, M, N, make_view):
    batch = _gen_batch(B, M, N, seed=2024)
    view = make_view(batch)

    if solver == "lapjvx_batch":
        costs_b, rows_b, cols_b = lap.lapjvx_batch(view, extend_cost=True, return_cost=True, n_threads=2)
        for b in range(B):
            c_s, r_s, c_s_ = lap.lapjvx(view[b], extend_cost=True, return_cost=True)
            assert np.isclose(costs_b[b], c_s)
            assert np.array_equal(rows_b[b], r_s)
            assert np.array_equal(cols_b[b], c_s_)
    elif solver == "lapjvsa_batch":
        costs_b, assigns_b = lap.lapjvsa_batch(view, extend_cost=True, return_cost=True, n_threads=2)
        for b in range(B):
            c_s, a_s = lap.lapjvsa(view[b], extend_cost=True, return_cost=True)
            assert np.isclose(costs_b[b], c_s)
            assert np.array_equal(assigns_b[b], a_s)
    else:
        costs_b, rows_b, cols_b = lap.lapjvs_batch(view, extend_cost=True, return_cost=True, n_threads=2)
        for b in range(B):
            c_s, r_s, c_s_ = lap.lapjvs(view[b], extend_cost=True, return_cost=True, jvx_like=True)
            assert np.isclose(costs_b[b], c_s)
            assert np.array_equal(rows_b[b], r_s)
            assert np.array_equal(cols_b[b], c_s_)


@pytest.mark.parametrize("solver, as_pairs", [
    (lap.lapjvx_batch, False),
    (lap.lapjvsa_batch, True),
    (lap.lapjvs_batch, False),
], ids=["lapjvx_batch", "lapjvsa_batch", "lapjvs_batch"])
def test_batch_tie_case_threading_determinism(solver, as_pairs):
    # Construct a tie-heavy batch to stress ordering determinism
    B, M, N = 4, 5, 5
    batch = np.zeros((B, M, N), dtype=np.float64)

    results = []
    for nt in (None, 1, 2, 4):
        out = solver(batch, extend_cost=False, return_cost=True, n_threads=nt)
        results.append(out)

    base = results[0]
    for r in results[1:]:
        # costs equal
        assert np.allclose(r[0], base[0])
        # assignments equal
        if as_pairs:
            for b in range(B):
                assert np.array_equal(r[1][b], base[1][b])
        else:
            for b in range(B):
                assert np.array_equal(r[1][b], base[1][b])
                assert np.array_equal(r[2][b], base[2][b])


@pytest.mark.parametrize("B,M,N", [(3, 8, 8), (2, 6, 10), (2, 10, 6)])
def test_batch_square_no_extend_equivalence_on_views(B, M, N):
    # Mirrors single-thread parity checks but with F-order and reversed views
    rng = np.random.RandomState(31415)
    batch = rng.rand(B, M, N).astype(np.float64)

    for make_view in (lambda A: np.asfortranarray(A), lambda A: A[:, :, ::-1]):
        view = make_view(batch)

        # jvx
        cx, rx, cx_ = lap.lapjvx_batch(view, extend_cost=(M != N), return_cost=True, n_threads=2)
        for b in range(B):
            c_s, r_s, c_s_ = lap.lapjvx(view[b], extend_cost=(M != N), return_cost=True)
            assert np.isclose(cx[b], c_s)
            assert np.array_equal(rx[b], r_s)
            assert np.array_equal(cx_[b], c_s_)

        # jvsa
        ca, aa = lap.lapjvsa_batch(view, extend_cost=(M != N), return_cost=True, n_threads=2)
        for b in range(B):
            c_s, a_s = lap.lapjvsa(view[b], extend_cost=(M != N), return_cost=True)
            assert np.isclose(ca[b], c_s)
            assert np.array_equal(aa[b], a_s)

        # jvs
        cs, rs, cs_ = lap.lapjvs_batch(view, extend_cost=(M != N), return_cost=True, n_threads=2)
        for b in range(B):
            c_s, r_s, c_s_ = lap.lapjvs(view[b], extend_cost=(M != N), return_cost=True, jvx_like=True)
            assert np.isclose(cs[b], c_s)
            assert np.array_equal(rs[b], r_s)
            assert np.array_equal(cs_[b], c_s_)
