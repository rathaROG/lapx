from functools import partial

import numpy as np
import pytest

import lap
from lap import _lapjvs_wp, _lapmod_wp


BATCH_SOLVERS = [lap.lapjvx_batch, lap.lapjvxa_batch,
                 lap.lapjvs_batch, lap.lapjvsa_batch]
JVS_SOLVERS = [lap.lapjvs, partial(lap.lapjvs, jvx_like=False), lap.lapjvsa]
JVS_IDS = ['rows-cols', 'mappings', 'pairs']


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('n_threads', [None, 0, 1, 2])
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('shape', [(0, 3, 3), (0, 2, 3), (0, 0, 0)])
def test_empty_batches(solver, n_threads, return_cost, shape):
    result = solver(np.empty(shape), extend_cost=True,
                    n_threads=n_threads, return_cost=return_cost)
    pairs = solver in (lap.lapjvxa_batch, lap.lapjvsa_batch)
    if return_cost:
        totals, *assignments = result
        assert totals.shape == (0,)
        assert totals.dtype == np.float64
        assert assignments == ([[]] if pairs else [[], []])
    else:
        assert result == ([] if pairs else ([], []))


@pytest.mark.parametrize('solver', JVS_SOLVERS, ids=JVS_IDS)
@pytest.mark.parametrize('shape', [(3, 3), (3, 5), (5, 3)])
@pytest.mark.parametrize('extend_cost', [None, True])
def test_jvs_totals_accumulate_float32_costs_in_float64(solver, shape, extend_cost):
    cost = np.full(shape, 1e9, dtype=np.float32)
    np.fill_diagonal(cost, [1e8, 1, 1])
    assert solver(cost, extend_cost=extend_cost)[0] == 100000002.0


@pytest.mark.parametrize('solver', [lap.lapjvs_batch, lap.lapjvsa_batch])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_jvs_batch_total_precision(solver, n_threads):
    cost = np.full((3, 3), 1e9, dtype=np.float32)
    np.fill_diagonal(cost, [1e8, 1, 1])
    totals = solver(np.stack([cost, cost]), n_threads=n_threads)[0]
    np.testing.assert_array_equal(totals, [100000002.0, 100000002.0])


@pytest.mark.parametrize('solver', JVS_SOLVERS, ids=JVS_IDS)
@pytest.mark.parametrize('shape', [(0, 0), (0, 1000), (1000, 0)])
@pytest.mark.parametrize('return_cost', [False, True])
def test_empty_jvs_problems_skip_native_solver(monkeypatch, solver, shape, return_cost):
    def unexpected_kernel(*args, **kwargs):
        pytest.fail('An empty assignment problem must not invoke the native solver')

    for name in ('_lapjvs_native', '_lapjvs_float32',
                 '_lapjvsa_native', '_lapjvsa_float32'):
        monkeypatch.setattr(_lapjvs_wp, name, unexpected_kernel)
    result = solver(np.empty(shape), return_cost=return_cost)
    if return_cost:
        assert result[0] == 0.0
        result = result[1] if solver is lap.lapjvsa else result[1:]
    if solver is lap.lapjvsa:
        assert result.shape == (0, 2)
        assert result.dtype == np.int64
    else:
        x, y = result
        assert (len(x), len(y)) == ((0, 0) if solver is lap.lapjvs else shape)
        assert x.dtype == y.dtype == np.int64
        assert np.all(x == -1) and np.all(y == -1)


@pytest.mark.parametrize('solver', JVS_SOLVERS, ids=JVS_IDS)
def test_empty_rectangular_jvs_still_requires_extension(solver):
    with pytest.raises(ValueError, match='square'):
        solver(np.empty((0, 5)), extend_cost=False)


@pytest.mark.parametrize('solver', [lap.lapjvs, lap.lapjvsa])
@pytest.mark.parametrize('shape', [(7, 7), (7, 11), (11, 7)])
@pytest.mark.parametrize('prefer_float32', [False, True])
def test_jvs_readonly_strided_costs(solver, shape, prefer_float32):
    scipy_opt = pytest.importorskip('scipy.optimize')
    cost = np.asfortranarray(np.random.default_rng(42).normal(size=shape))[:, ::-1]
    original = cost.copy()
    cost.setflags(write=False)
    result = solver(cost, extend_cost=True, prefer_float32=prefer_float32)
    total = result[0]
    rows, cols = result[1].T if solver is lap.lapjvsa else result[1:]
    expected_rows, expected_cols = scipy_opt.linear_sum_assignment(cost)
    assert len(rows) == min(shape)
    assert len(np.unique(rows)) == len(np.unique(cols)) == len(rows)
    assert total == cost[rows, cols].sum(dtype=np.float64)
    assert total == pytest.approx(cost[expected_rows, expected_cols].sum())
    np.testing.assert_array_equal(cost, original)


@pytest.mark.parametrize('fast', [False, True])
@pytest.mark.parametrize('changes', [
    {'n': 0},
    {'n': -1},
    {'n': 2**32 + 2},
    {'cc': [[1., 4.], [3., 2.]]},
    {'ii': [[0, 2, 4]]},
    {'kk': [[0, 1, 0, 1]]},
    {'ii': [0, 4]},
    {'ii': [1, 2, 4]},
    {'ii': [0, 2, 3]},
    {'ii': [0, 5, 4]},
    {'ii': [0, -1, 4]},
    {'ii': [0., 2., 4.]},
    {'ii': np.array([0, 2**32 + 2, 4], dtype=np.uint64)},
    {'cc': [1., 4., 3.]},
    {'cc': [], 'ii': [0, 0, 0], 'kk': np.array([], dtype=int)},
    {'cc': [np.nan, 4., 3., 2.]},
    {'cc': [np.inf, 4., 3., 2.]},
    {'cc': [-1., 4., 3., 2.]},
    {'cc': [lap.LARGE, 4., 3., 2.]},
    {'cc': [1j, 4., 3., 2.]},
    {'kk': [-1, 1, 0, 1]},
    {'kk': [0, 2, 0, 1]},
    {'kk': [0, 2**32 + 1, 0, 1]},
    {'kk': [0., 1., 0., 1.]},
    {'kk': [1, 0, 0, 1]},
    {'kk': [0, 0, 0, 1]},
])
def test_malformed_sparse_input_rejected_before_solving(monkeypatch, fast, changes):
    def unexpected_solver(*args, **kwargs):
        pytest.fail('Malformed sparse data reached the solver')

    monkeypatch.setattr(_lapmod_wp, '_lapmod', unexpected_solver)
    monkeypatch.setattr(_lapmod_wp, '_pycrrt', unexpected_solver)
    args = dict(n=2, cc=[1., 4., 3., 2.], ii=[0, 2, 4], kk=[0, 1, 0, 1])
    args.update(changes)
    for name in ('cc', 'ii', 'kk'):
        args[name] = np.asarray(args[name])
    with pytest.raises(ValueError):
        lap.lapmod(**args, fast=fast)


@pytest.mark.parametrize('fast', [False, True])
@pytest.mark.parametrize('index_dtype', [np.int32, np.int64, np.uint32, np.uint64])
def test_sparse_strided_indices(fast, index_dtype):
    cc = np.array([1., 99., 4., 99., 3., 99., 2., 99.])[::2]
    ii = np.array([0, 99, 2, 99, 4, 99], dtype=index_dtype)[::2]
    kk = np.array([0, 99, 1, 99, 0, 99, 1, 99], dtype=index_dtype)[::2]
    total, x, y = lap.lapmod(np.int64(2), cc, ii, kk, fast=fast)
    assert total == 3.0
    np.testing.assert_array_equal(x, [0, 1])
    np.testing.assert_array_equal(y, [0, 1])


def test_sparse_empty_rows_remain_valid_structure():
    # Empty rows make this problem infeasible, but the CSR structure is valid.
    total, x, y = lap.lapmod(4, np.array([1., 2.]),
                             np.array([0, 0, 1, 1, 2], dtype=np.uint64),
                             np.array([1, 3], dtype=np.uint64))
    assert total == np.inf
    assert x.shape == y.shape == (4,)


@pytest.mark.parametrize('fast', [False, True])
@pytest.mark.parametrize('cc', [
    np.array([100000., .001, .001], dtype=np.float32),
    np.array([40000., 40000.], dtype=np.float16),
])
def test_sparse_totals_accumulate_in_float64(fast, cc):
    n = len(cc)
    total, x, y = lap.lapmod(n, cc, np.arange(n + 1), np.arange(n), fast=fast)
    assert total == cc.sum(dtype=np.float64)
    np.testing.assert_array_equal(x, np.arange(n))
    np.testing.assert_array_equal(y, np.arange(n))
