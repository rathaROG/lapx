"""Check public dense solvers against exhaustive small-problem optima."""

from itertools import permutations

import numpy as np
import pytest

import lap


def _solvers(required, optional):
    # Only R/H may be absent in an intentionally legacy-only installation.
    found = [(name, getattr(lap, name)) for name in required]
    available = [name for name in optional if hasattr(lap, name)]
    assert len(available) in (0, len(optional)), 'Incomplete R/H exports'
    found.extend((name, getattr(lap, name)) for name in available)
    assert all(callable(function) for _, function in found)
    return found


def _optimal_total(cost):
    """Enumerate all full rectangular matchings, independently of any solver."""
    n, m = cost.shape
    if n <= m:
        return min(sum(float(cost[row, col]) for row, col in enumerate(cols))
                   for cols in permutations(range(m), n))
    return min(sum(float(cost[row, col]) for col, row in enumerate(rows))
               for rows in permutations(range(n), m))


def _validate_indices(rows, cols, n, m):
    assert isinstance(rows, np.ndarray) and isinstance(cols, np.ndarray)
    assert rows.ndim == cols.ndim == 1
    assert rows.dtype.kind in 'iu' and cols.dtype.kind in 'iu'
    assert len(rows) == len(cols) == min(n, m)
    assert np.all((rows >= 0) & (rows < n))
    assert np.all((cols >= 0) & (cols < m))
    assert len(np.unique(rows)) == len(np.unique(cols)) == len(rows)


def _to_pairs_single(name, result, n, m):
    assert isinstance(result, tuple)
    if name in ('lapjvxa', 'lapjvsa'):
        assert len(result) == 2
        total, pairs = result
        assert isinstance(pairs, np.ndarray) and pairs.ndim == 2 and pairs.shape[1] == 2
        rows, cols = pairs.T
    else:
        assert len(result) == 3
        total, rows, cols = result
        if name == 'lapjv':
            x, y = rows, cols
            assert isinstance(x, np.ndarray) and isinstance(y, np.ndarray)
            assert x.shape == (n,) and y.shape == (m,)
            assert x.dtype.kind in 'iu' and y.dtype.kind in 'iu'
            assert np.all(x >= -1) and np.all(y >= -1)
            rows = np.nonzero(x >= 0)[0]
            cols = x[rows]
            _validate_indices(rows, cols, n, m)
            np.testing.assert_array_equal(y[cols], rows)
            assert np.count_nonzero(y >= 0) == len(rows)
    _validate_indices(rows, cols, n, m)
    assert np.ndim(total) == 0 and np.isfinite(total)
    return total, rows, cols


def _to_pairs_batch(name, result, b, n, m):
    assert isinstance(result, tuple)
    totals = result[0]
    assert isinstance(totals, np.ndarray) and totals.shape == (b,)
    assert totals.dtype == np.float64
    single_name = name[:-len('_batch')]
    if name in ('lapjvxa_batch', 'lapjvsa_batch'):
        assert len(result) == 2 and isinstance(result[1], list) and len(result[1]) == b
        items = [(totals[index], pairs) for index, pairs in enumerate(result[1])]
    else:
        assert len(result) == 3
        rows, cols = result[1:]
        assert isinstance(rows, list) and isinstance(cols, list)
        assert len(rows) == len(cols) == b
        items = [(totals[index], rows[index], cols[index]) for index in range(b)]
    normalized = [_to_pairs_single(single_name, item, n, m) for item in items]
    return totals, [item[1] for item in normalized], [item[2] for item in normalized]


@pytest.mark.smoke
@pytest.mark.parametrize('shape', [(4, 5), (5, 4), (4, 4)])
def test_single_matrix_solvers_smoke(shape):
    n, m = shape
    # Binary fractions are exact in float32 and float64, so every precision
    # solves the same represented problem. Tied optima may use different pairs.
    cost = np.random.default_rng(12345).integers(-8, 32, size=shape) / 8.0
    original = cost.copy()
    cost.setflags(write=False)
    optimum = _optimal_total(cost)
    solvers = _solvers(('lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa'),
                       ('lapjvr', 'lapjvh'))
    for name, function in solvers:
        options = {'return_cost': True}
        if name != 'lapjvc':
            options['extend_cost'] = True
        if name == 'lapjvs':
            options['jvx_like'] = True
        total, rows, cols = _to_pairs_single(name, function(cost, **options), n, m)
        assert np.isfinite(cost[rows, cols]).all()
        assert total == cost[rows, cols].sum(dtype=np.float64)
        assert total == optimum, f'{name}: nonoptimal assignment'
        np.testing.assert_array_equal(cost, original)


@pytest.mark.smoke
@pytest.mark.parametrize('shape', [(4, 5), (5, 4), (4, 4)])
def test_batch_matrix_solvers_smoke(shape):
    b, (n, m) = 3, shape
    costs = np.random.default_rng(54321).integers(-8, 32, size=(b, n, m)) / 8.0
    original = costs.copy()
    costs.setflags(write=False)
    optima = [_optimal_total(cost) for cost in costs]
    solvers = _solvers(('lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch'),
                       ('lapjvr_batch', 'lapjvh_batch'))
    for name, function in solvers:
        result = function(costs, extend_cost=True, return_cost=True, n_threads=2)
        totals, rows, cols = _to_pairs_batch(name, result, b, n, m)
        for index in range(b):
            selected = costs[index, rows[index], cols[index]]
            assert np.isfinite(selected).all()
            assert totals[index] == selected.sum(dtype=np.float64)
            assert totals[index] == optima[index], f'{name}: nonoptimal assignment'
        np.testing.assert_array_equal(costs, original)
