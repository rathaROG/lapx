"""Check for regressions in native solvers through the public wrappers."""

from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

import lap
from lap import _lapjvs


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
@pytest.mark.parametrize('dtype', [np.float16, np.float32])
def test_jv_totals_accumulate_in_float64(solver, dtype):
    cost = np.full((3, 3), 10000, dtype=dtype)
    np.fill_diagonal(cost, [1000, .1, .1])
    assert solver(cost)[0] == cost.diagonal().sum(dtype=np.float64)


@pytest.mark.parametrize('solver', [lap.lapjvx_batch, lap.lapjvxa_batch])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_jvx_batch_total_precision(solver, n_threads):
    cost = np.full((3, 3), 10000, dtype=np.float32)
    np.fill_diagonal(cost, [1000, .1, .1])
    totals = solver(np.stack([cost, cost]), n_threads=n_threads)[0]
    np.testing.assert_array_equal(totals, [cost.diagonal().sum(dtype=np.float64)] * 2)


@pytest.mark.parametrize('dtype, values', [
    (np.float32, [1000, .1, .1]),
    (np.int32, [2_000_000_000] * 3),
])
def test_jvc_total_does_not_round_or_overflow(dtype, values):
    cost = np.full((3, 3), max(values), dtype=dtype)
    np.fill_diagonal(cost, values)
    assert lap.lapjvc(cost)[0] == cost.diagonal().sum(dtype=np.float64)


def test_jvc_valid_cost_equal_to_internal_sentinel_is_retained():
    cost = np.array([[np.iinfo(np.int32).max // 2]], dtype=np.int32)
    total, rows, cols = lap.lapjvc(cost)
    assert total == float(cost[0, 0])
    np.testing.assert_array_equal(rows, [0])
    np.testing.assert_array_equal(cols, [0])


@pytest.mark.parametrize('cost', [np.empty((0, 3)), np.full((2, 2), np.nan)])
@pytest.mark.parametrize('return_cost', [True, False])
def test_jvc_empty_indices_have_integer_dtype(cost, return_cost):
    result = lap.lapjvc(cost, return_cost=return_cost)
    rows, cols = result[1:] if return_cost else result
    assert rows.shape == cols.shape == (0,)
    assert rows.dtype.kind == cols.dtype.kind == 'i'


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
@pytest.mark.parametrize('shape', [(4, 4), (4, 7), (7, 4)])
@pytest.mark.parametrize('cost_limit', [np.inf, .5])
def test_jv_readonly_strided_inputs_preserve_mappings(solver, shape, cost_limit):
    cost = np.asfortranarray(np.random.default_rng(18).random(shape).astype(np.float32))[:, ::-1]
    original = cost.copy()
    cost.setflags(write=False)
    result = solver(cost, extend_cost=True, cost_limit=cost_limit)
    reference = solver(cost.copy(), extend_cost=True, cost_limit=cost_limit)
    for got, expected in zip(result, reference):
        np.testing.assert_array_equal(got, expected)
    if solver is lap.lapjv:
        x, y = result[1:]
        rows = np.nonzero(x >= 0)[0]
        np.testing.assert_array_equal(y[x[rows]], rows)
        assert len(x) == shape[0] and len(y) == shape[1]
    np.testing.assert_array_equal(cost, original)


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
@pytest.mark.parametrize('cost_limit', [np.nan, -np.inf])
def test_invalid_cost_limits_are_rejected(solver, cost_limit):
    with pytest.raises(ValueError, match='cost_limit'):
        solver(np.ones((2, 2)), cost_limit=cost_limit)


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
def test_jv_dimension_checked_before_materializing_broadcast_input(solver):
    cost = np.broadcast_to(np.array(0.), (1, 2**31))
    with pytest.raises(ValueError, match='int32 indices'):
        solver(cost, extend_cost=True)


def _jv_pairs(solver, result):
    if solver is lap.lapjv:
        rows = np.nonzero(result[1] >= 0)[0]
        cols = result[1][rows]
        np.testing.assert_array_equal(result[2][cols], rows)
        return np.column_stack((rows, cols))
    if solver is lap.lapjvx:
        return np.column_stack(result[1:])
    return result[1]


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
@pytest.mark.parametrize('cost,cost_limit,total,pairs', [
    ([[1e6, 1e6 + 1], [1e6 + 1, 1e6]], np.inf, 2e6, [[0, 0], [1, 1]]),
    ([[0, -2e9], [-2e9, -3e9]], np.inf, -4e9, [[0, 1], [1, 0]]),
    ([[1e9, np.inf], [np.inf, 2e9]], np.inf, 3e9, [[0, 0], [1, 1]]),
    ([[1e9, 9e9], [9e9, 4e9]], 2e9, 1e9, [[0, 0]]),
    ([[1e100]], np.inf, 1e100, [[0, 0]]),
])
def test_jv_cost_range_and_forbidden_edges(solver, cost, cost_limit, total, pairs):
    result = solver(np.asarray(cost, dtype=np.float64), cost_limit=cost_limit)
    assert result[0] == total
    np.testing.assert_array_equal(_jv_pairs(solver, result), pairs)


@pytest.mark.parametrize('solver', [lap.lapjv, lap.lapjvx, lap.lapjvxa])
def test_jv_large_infeasible_costs_keep_infinite_total(solver):
    cost = np.array([[1e9, np.inf], [2e9, np.inf]])
    assert solver(cost)[0] == np.inf


@pytest.mark.parametrize('fp_version', [0, 4])
def test_sparse_invalid_path_version_rejected_even_without_augmentation(fp_version):
    with pytest.raises(ValueError, match='fp_version'):
        lap.lapmod(2, np.array([1., 2.]), np.arange(3), np.arange(2), fp_version=fp_version)


@pytest.mark.parametrize('solver_name', ['lapjv', 'lapjvc', 'lapmod'])
def test_native_solvers_share_readonly_inputs_across_threads(solver_name):
    cost = np.random.default_rng(24).random((64, 64))
    cost.setflags(write=False)
    if solver_name == 'lapmod':
        cc = cost.ravel()
        ii = np.arange(65) * 64
        kk = np.tile(np.arange(64), 64)
        solve = lambda: lap.lapmod(64, cc, ii, kk)
    else:
        solve = lambda: getattr(lap, solver_name)(cost)
    expected = solve()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda _: solve(), range(16)):
            for got, reference in zip(result, expected):
                np.testing.assert_array_equal(got, reference)


@pytest.mark.parametrize('kernel', [
    _lapjvs.lapjvs_native, _lapjvs.lapjvs_float32,
    _lapjvs.lapjvsa_native, _lapjvs.lapjvsa_float32,
])
@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_jvs_infeasible_inputs_allow_thread_and_scratch_reuse(kernel, dtype):
    # Exercise C++ exceptions while the GIL is released, then reuse the same
    # thread-local scratch buffers at different dimensions.
    infeasible_costs = [
        [[0, np.inf], [1, np.inf]],
        [[0, 1], [np.inf, np.inf]],
        [[0, np.inf, np.inf], [0, np.inf, np.inf], [np.inf, 0, 1]],
    ]

    def work():
        for bad in infeasible_costs:
            with pytest.raises(ValueError):
                kernel(np.asarray(bad, dtype=dtype))
            for n in [5, 1, 0, 3]:
                good = np.ones((n, n), dtype=dtype)
                np.fill_diagonal(good, 0)
                result = kernel(good)
                if isinstance(result, tuple):
                    np.testing.assert_array_equal(result[0], np.arange(n))
                    np.testing.assert_array_equal(result[1], np.arange(n))
                else:
                    np.testing.assert_array_equal(result, np.column_stack([np.arange(n)] * 2))

    with ThreadPoolExecutor(max_workers=1) as pool:
        pool.submit(work).result(timeout=5)


@pytest.mark.parametrize('solver', [lap.lapjvs, lap.lapjvsa])
@pytest.mark.parametrize('prefer_float32', [True, False])
def test_jvs_displacement_limit_preserves_minimum_assignment(solver, prefer_float32):
    # When row reduction reaches its limit, it must keep the cheapest column
    # and leave the displaced row for augmentation.
    cost = np.array([
        [892, 268, 833, 935],
        [499, 240, 956, 778],
        [312, 269, 683, 479],
        [320, 351, 355, 97],
    ], dtype=np.float64)
    result = solver(cost, prefer_float32=prefer_float32)
    assert result[0] == 1482.0
