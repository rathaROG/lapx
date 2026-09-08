"""Check for regressions with large costs in public solvers, within each solver's cost range."""

import numpy as np
import pytest

import lap


SINGLE_SOLVERS = [
    pytest.param('lapjv', {}, id='lapjv'),
    pytest.param('lapjvx', {}, id='lapjvx'),
    pytest.param('lapjvxa', {}, id='lapjvxa'),
    pytest.param('lapjvc', {}, id='lapjvc'),
    pytest.param('lapjvs', {}, id='lapjvs'),
    pytest.param('lapjvs', {'jvx_like': False}, id='lapjvs-mappings'),
    pytest.param('lapjvsa', {}, id='lapjvsa'),
    pytest.param('lapjvs', {'prefer_float32': False}, id='lapjvs-float64'),
    pytest.param('lapjvs', {'prefer_float32': False, 'jvx_like': False},
                 id='lapjvs-float64-mappings'),
    pytest.param('lapjvsa', {'prefer_float32': False}, id='lapjvsa-float64'),
]
BATCH_SOLVERS = [
    pytest.param('lapjvx_batch', {}, id='lapjvx_batch'),
    pytest.param('lapjvxa_batch', {}, id='lapjvxa_batch'),
    pytest.param('lapjvs_batch', {}, id='lapjvs_batch'),
    pytest.param('lapjvsa_batch', {}, id='lapjvsa_batch'),
    pytest.param('lapjvs_batch', {'prefer_float32': False}, id='lapjvs_batch-float64'),
    pytest.param('lapjvsa_batch', {'prefer_float32': False}, id='lapjvsa_batch-float64'),
]
DTYPES = [np.int32, np.int64, np.float32, np.float64]
SHAPES = [(3, 3), (3, 5), (5, 3)]


def _pairs(name, assignments, shape, options):
    if name in ('lapjv', 'lapmod') or (name == 'lapjvs' and not options.get('jvx_like', True)):
        x, y = assignments
        assert x.shape == (shape[0],) and y.shape == (shape[1],)
        rows = np.nonzero(x >= 0)[0]
        cols = x[rows]
        np.testing.assert_array_equal(y[cols], rows)
        np.testing.assert_array_equal(np.nonzero(y >= 0)[0], np.sort(cols))
        pairs = np.column_stack((rows, cols))
    elif name in ('lapjvxa', 'lapjvsa'):
        pairs = assignments
    else:
        pairs = np.column_stack(assignments)
    assert pairs.ndim == 2 and pairs.shape[1] == 2
    assert pairs.dtype.kind in 'iu'
    rows, cols = pairs.T
    assert np.all((rows >= 0) & (rows < shape[0]))
    assert np.all((cols >= 0) & (cols < shape[1]))
    assert len(np.unique(rows)) == len(np.unique(cols)) == len(pairs)
    return pairs[np.lexsort((cols, rows))]


def _single(name, options, cost, return_cost):
    kwargs = dict(options, return_cost=return_cost)
    if name != 'lapjvc':
        kwargs['extend_cost'] = cost.shape[0] != cost.shape[1]
    result = getattr(lap, name)(cost, **kwargs)
    assignments = result[1:] if return_cost else result
    if name in ('lapjvxa', 'lapjvsa') and return_cost:
        assignments = assignments[0]
    return (result[0] if return_cost else None), _pairs(name, assignments, cost.shape, options)


def _known_case(shape, dtype, case=0, forbidden=False):
    # These values are exactly representable in all four dtypes, including
    # float32. The unique optimum separates assignment errors from rounding.
    low, high = [(1_000_000_000, 2_000_000_000),
                 (500_000_000, 2_000_000_000), (-1_000_000_000, 0)][case]
    cost = np.full(shape, np.inf if forbidden else high, dtype=dtype)
    k = min(shape)
    rows = np.roll(np.arange(shape[0]), case)[:k]
    cols = np.roll(np.arange(shape[1]), -case)[:k]
    cost[rows, cols] = low
    pairs = np.column_stack((rows, cols))
    pairs = pairs[np.argsort(rows)]
    return cost, k * float(low), pairs


@pytest.mark.parametrize('name,options', SINGLE_SOLVERS)
@pytest.mark.parametrize('dtype', DTYPES)
@pytest.mark.parametrize('shape', SHAPES)
def test_large_cost_single_solvers_agree(name, options, dtype, shape):
    # Case 0 is the original regression: a 3x3 diagonal optimum of 3e9 was
    # incorrectly returned as 5e9 by the dense JV kernel's fixed LARGE bound.
    for case in range(3):
        cost, expected_total, expected_pairs = _known_case(shape, dtype, case)
        original = cost.copy()
        cost.setflags(write=False)
        for return_cost in (True, False):
            total, pairs = _single(name, options, cost, return_cost)
            np.testing.assert_array_equal(pairs, expected_pairs)
            assert cost[pairs[:, 0], pairs[:, 1]].sum(dtype=np.float64) == expected_total
            if return_cost:
                assert total == expected_total
        np.testing.assert_array_equal(cost, original)


@pytest.mark.parametrize('name,options', SINGLE_SOLVERS)
@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('shape', SHAPES)
def test_large_cost_forbidden_edges_agree(name, options, dtype, shape):
    cost, expected_total, expected_pairs = _known_case(shape, dtype, case=1, forbidden=True)
    for return_cost in (True, False):
        total, pairs = _single(name, options, cost, return_cost)
        np.testing.assert_array_equal(pairs, expected_pairs)
        if return_cost:
            assert total == expected_total


@pytest.mark.parametrize('name,options', BATCH_SOLVERS)
@pytest.mark.parametrize('dtype', DTYPES)
@pytest.mark.parametrize('shape', SHAPES)
def test_large_cost_batches_preserve_results_and_order(name, options, dtype, shape):
    cases = [_known_case(shape, dtype, case) for case in range(3)]
    costs = np.stack([case[0] for case in cases])
    original = costs.copy()
    costs.setflags(write=False)
    single_name = name[:-len('_batch')]
    for n_threads in (1, 2):
        for return_cost in (True, False):
            result = getattr(lap, name)(costs, extend_cost=shape[0] != shape[1],
                                       return_cost=return_cost, n_threads=n_threads, **options)
            if return_cost:
                np.testing.assert_array_equal(result[0], [case[1] for case in cases])
                assert result[0].dtype == np.float64
            if single_name in ('lapjvxa', 'lapjvsa'):
                assignments = result[1] if return_cost else result
            else:
                rows_list, cols_list = result[1:] if return_cost else result
                assert len(rows_list) == len(cols_list) == len(cases)
                assignments = list(zip(rows_list, cols_list))
            assert len(assignments) == len(cases)
            for assignment, (cost, expected_total, expected_pairs) in zip(assignments, cases):
                pairs = _pairs(single_name, assignment, shape, options)
                np.testing.assert_array_equal(pairs, expected_pairs)
                assert cost[pairs[:, 0], pairs[:, 1]].sum(dtype=np.float64) == expected_total
    np.testing.assert_array_equal(costs, original)


@pytest.mark.parametrize('name,options', SINGLE_SOLVERS)
@pytest.mark.parametrize('shape', [(128, 128), (96, 128), (128, 96)])
def test_large_scaled_costs_match_scipy(name, options, shape):
    scipy_opt = pytest.importorskip('scipy.optimize')
    # Integer multiples of a power of two keep the input and reduced costs
    # exactly representable in float32 while exercising large signed values.
    cost = np.random.RandomState(608).randint(-16, 17, size=shape).astype(np.float64) * 2**24
    rows, cols = scipy_opt.linear_sum_assignment(cost)
    optimum = cost[rows, cols].sum(dtype=np.float64)
    for return_cost in (True, False):
        total, pairs = _single(name, options, cost, return_cost)
        assert len(pairs) == min(shape)
        # Equal-cost ties may produce different valid assignments.
        assert cost[pairs[:, 0], pairs[:, 1]].sum(dtype=np.float64) == optimum
        if return_cost:
            assert total == optimum


@pytest.mark.parametrize('name', ['lapjvx_batch', 'lapjvxa_batch'])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_large_cost_limit_in_batches(name, n_threads):
    cost = np.array([[1e9, 8e9], [8e9, 4e9]])
    costs = np.stack((cost, cost[:, ::-1]))
    for return_cost in (True, False):
        result = getattr(lap, name)(costs, cost_limit=2e9, return_cost=return_cost, n_threads=n_threads)
        if return_cost:
            np.testing.assert_array_equal(result[0], [1e9, 1e9])
        if name == 'lapjvxa_batch':
            pairs_list = result[1] if return_cost else result
        else:
            rows, cols = result[1:] if return_cost else result
            pairs_list = [np.column_stack(pair) for pair in zip(rows, cols)]
        assert len(pairs_list) == 2
        np.testing.assert_array_equal(pairs_list[0], [[0, 0]])
        np.testing.assert_array_equal(pairs_list[1], [[0, 1]])


@pytest.mark.parametrize('fast,fp_version', [(False, lap.FP_DYNAMIC), (True, lap.FP_1),
                                           (True, lap.FP_2), (True, lap.FP_DYNAMIC)])
@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_lapmod_near_large_boundary(fast, fp_version, dtype):
    cost = np.array([[lap.LARGE - 1, lap.LARGE - 2],
                     [lap.LARGE - 2, lap.LARGE - 1]], dtype=dtype)
    for return_cost in (True, False):
        result = lap.lapmod(2, cost.ravel(), np.array([0, 2, 4]), np.array([0, 1, 0, 1]),
                            fast=fast, fp_version=fp_version, return_cost=return_cost)
        pairs = _pairs('lapmod', result[1:] if return_cost else result, cost.shape, {})
        np.testing.assert_array_equal(pairs, [[0, 1], [1, 0]])
        if return_cost:
            assert result[0] == 2 * (lap.LARGE - 2)


@pytest.mark.parametrize('fast', [False, True])
@pytest.mark.parametrize('value', [np.nextafter(float(lap.LARGE), np.inf), 1e9])
def test_lapmod_rejects_costs_above_supported_range(fast, value):
    with pytest.raises(ValueError, match='less than'):
        lap.lapmod(1, np.array([value]), np.array([0, 1]), np.array([0]), fast=fast)
