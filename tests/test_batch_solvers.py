import numpy as np
import pytest
import lap


def generate_batch(B: int, N: int, M: int, seed: int = 0) -> np.ndarray:
    # Use RandomState for broad NumPy compatibility on older environments
    rng = np.random.RandomState(seed)
    return rng.rand(B, N, M)


@pytest.mark.parametrize(
    "B,N,M",
    [
        (2, 4, 4),  # square
        (2, 4, 5),  # rectangular (N < M)
        (2, 5, 4),  # rectangular (N > M)
    ],
)
def test_lapjvx_batch_matches_single(B, N, M):
    batch_costs = generate_batch(B, N, M, seed=123)
    costs_b, rows_b, cols_b = lap.lapjvx_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )

    assert isinstance(rows_b, list) and isinstance(cols_b, list)
    assert len(rows_b) == B and len(cols_b) == B
    assert costs_b.shape == (B,)

    for b in range(B):
        cost_s, rows_s, cols_s = lap.lapjvx(
            batch_costs[b], extend_cost=True, return_cost=True
        )
        assert np.isclose(cost_s, costs_b[b])
        assert np.array_equal(rows_s, rows_b[b])
        assert np.array_equal(cols_s, cols_b[b])

        K = min(N, M)
        assert rows_b[b].shape == (K,)
        assert cols_b[b].shape == (K,)


@pytest.mark.parametrize(
    "B,N,M",
    [
        (2, 4, 4),  # square
        (2, 4, 5),  # rectangular (N < M)
        (2, 5, 4),  # rectangular (N > M)
    ],
)
def test_lapjvxa_batch_matches_single_and_jvx(B, N, M):
    batch_costs = generate_batch(B, N, M, seed=456)

    costs_a, assignments_b = lap.lapjvxa_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )
    assert isinstance(assignments_b, list) and len(assignments_b) == B
    assert costs_a.shape == (B,)

    costs_x, rows_b, cols_b = lap.lapjvx_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )

    for b in range(B):
        K = min(N, M)
        assert assignments_b[b].shape == (K, 2)
        assert np.array_equal(assignments_b[b][:, 0], rows_b[b])
        assert np.array_equal(assignments_b[b][:, 1], cols_b[b])
        assert np.isclose(costs_a[b], costs_x[b])

        cost_s, assignments_s = lap.lapjvxa(
            batch_costs[b], extend_cost=True, return_cost=True
        )
        assert np.isclose(cost_s, costs_a[b])
        assert np.array_equal(assignments_s, assignments_b[b])


@pytest.mark.parametrize(
    "B,N,M",
    [
        (2, 4, 4),  # square
        (2, 4, 5),  # rectangular (N < M)
        (2, 5, 4),  # rectangular (N > M)
    ],
)
def test_lapjvs_batch_matches_single(B, N, M):
    batch_costs = generate_batch(B, N, M, seed=789)
    costs_b, rows_b, cols_b = lap.lapjvs_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )

    assert isinstance(rows_b, list) and isinstance(cols_b, list)
    assert len(rows_b) == B and len(cols_b) == B
    assert costs_b.shape == (B,)

    for b in range(B):
        cost_s, rows_s, cols_s = lap.lapjvs(
            batch_costs[b], extend_cost=True, return_cost=True, jvx_like=True
        )
        assert np.isclose(cost_s, costs_b[b])
        assert np.array_equal(rows_s, rows_b[b])
        assert np.array_equal(cols_s, cols_b[b])

        K = min(N, M)
        assert rows_b[b].shape == (K,)
        assert cols_b[b].shape == (K,)


@pytest.mark.parametrize(
    "B,N,M",
    [
        (2, 4, 4),  # square
        (2, 4, 5),  # rectangular (N < M)
        (2, 5, 4),  # rectangular (N > M)
    ],
)
def test_lapjvsa_batch_matches_single_and_jvs(B, N, M):
    batch_costs = generate_batch(B, N, M, seed=101112)

    costs_a, assignments_b = lap.lapjvsa_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )
    assert isinstance(assignments_b, list) and len(assignments_b) == B
    assert costs_a.shape == (B,)

    costs_s, rows_b, cols_b = lap.lapjvs_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )

    for b in range(B):
        K = min(N, M)
        assert assignments_b[b].shape == (K, 2)

        assert np.array_equal(assignments_b[b][:, 0], rows_b[b])
        assert np.array_equal(assignments_b[b][:, 1], cols_b[b])
        assert np.isclose(costs_a[b], costs_s[b])

        cost_single, assignments_single = lap.lapjvsa(
            batch_costs[b], extend_cost=True, return_cost=True
        )
        assert np.isclose(cost_single, costs_a[b])
        assert np.array_equal(assignments_single, assignments_b[b])


@pytest.mark.parametrize(
    "B,N,M",
    [
        (2, 4, 4),  # square
        (2, 4, 5),  # rectangular (N < M)
        (2, 5, 4),  # rectangular (N > M)
    ],
)
def test_jvx_and_jvs_batch_equivalence(B, N, M):
    batch_costs = generate_batch(B, N, M, seed=2024)

    costs_x, rows_x, cols_x = lap.lapjvx_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )
    costs_s, rows_s, cols_s = lap.lapjvs_batch(
        batch_costs, extend_cost=True, return_cost=True, n_threads=2
    )

    assert np.allclose(costs_x, costs_s)
    for b in range(B):
        assert np.array_equal(rows_x[b], rows_s[b])
        assert np.array_equal(cols_x[b], cols_s[b])


def test_square_no_extend_cost_equivalence():
    # Verify batch vs single when N == M and extend_cost=False
    B, N, M = 3, 5, 5
    batch_costs = generate_batch(B, N, M, seed=31415)

    # lapjvx_batch vs lapjvx
    costs_b, rows_b, cols_b = lap.lapjvx_batch(
        batch_costs, extend_cost=False, return_cost=True, n_threads=2
    )
    assert costs_b.shape == (B,)
    assert len(rows_b) == B and len(cols_b) == B

    for b in range(B):
        cost_s, rows_s, cols_s = lap.lapjvx(
            batch_costs[b], extend_cost=False, return_cost=True
        )
        assert np.isclose(cost_s, costs_b[b])
        assert np.array_equal(rows_s, rows_b[b])
        assert np.array_equal(cols_s, cols_b[b])

    # lapjvsa_batch vs lapjvsa
    costs_a, assignments_b = lap.lapjvsa_batch(
        batch_costs, extend_cost=False, return_cost=True, n_threads=2
    )
    assert costs_a.shape == (B,)
    assert len(assignments_b) == B

    for b in range(B):
        cost_s, assignments_s = lap.lapjvsa(
            batch_costs[b], extend_cost=False, return_cost=True
        )
        assert np.isclose(cost_s, costs_a[b])
        assert np.array_equal(assignments_s, assignments_b[b])


@pytest.mark.parametrize("fn_batch, fn_single, as_pairs", [
    (lap.lapjvx_batch, lap.lapjvx, False),
    (lap.lapjvsa_batch, lap.lapjvsa, True),
])
def test_threading_determinism(fn_batch, fn_single, as_pairs):
    # Same inputs should produce identical results across thread counts
    B, N, M = 4, 6, 8
    batch_costs = generate_batch(B, N, M, seed=20241031)

    results = []
    for nt in (None, 1, 2, 4):
        out = fn_batch(batch_costs, extend_cost=True, return_cost=True, n_threads=nt)
        results.append(out)

    # Compare to first run
    base = results[0]
    for r in results[1:]:
        # costs
        assert np.allclose(r[0], base[0])
        # assignments
        if as_pairs:
            for b in range(B):
                assert np.array_equal(r[1][b], base[1][b])
        else:
            for b in range(B):
                assert np.array_equal(r[1][b], base[1][b])
                assert np.array_equal(r[2][b], base[2][b])

    # Sanity: batch vs single parity
    if as_pairs:
        costs_b, assignments_b = base
        for b in range(B):
            cost_s, assignments_s = fn_single(batch_costs[b], extend_cost=True, return_cost=True)
            assert np.isclose(cost_s, costs_b[b])
            assert np.array_equal(assignments_s, assignments_b[b])
    else:
        costs_b, rows_b, cols_b = base
        for b in range(B):
            cost_s, rows_s, cols_s = fn_single(batch_costs[b], extend_cost=True, return_cost=True)
            assert np.isclose(cost_s, costs_b[b])
            assert np.array_equal(rows_s, rows_b[b])
            assert np.array_equal(cols_s, cols_b[b])
