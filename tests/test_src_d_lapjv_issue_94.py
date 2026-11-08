"""Reproduce the three precision cases from src-d/lapjv issue 94.

https://github.com/src-d/lapjv/issues/94

The final comment corrects the reported Rust failure: that example printed
another solver's costs. Compare each solver's own selected costs here.
"""

from fractions import Fraction
from functools import lru_cache
from importlib.util import find_spec
from itertools import permutations
import math

import lap
import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment


ISSUE = 'https://github.com/src-d/lapjv/issues/94'
N = 1000
CHEAP_ROWS = 950
NATIVE = ('lapjvr', 'lapjvh')


class SuboptimalAssignment(AssertionError):
    """A valid assignment has a larger objective than the independent reference."""


# Each entry gives the test ID, public function, options, and result layout.
SINGLE_VARIANTS = [
    ('lapjv', 'lapjv', {}, 'mapping'),
    ('lapjvx', 'lapjvx', {}, 'indices'),
    ('lapjvxa', 'lapjvxa', {}, 'pairs'),
    ('lapjvc', 'lapjvc', {}, 'indices'),
]
for prefer_float32 in (True, False):
    suffix = '' if prefer_float32 else '-float64'
    options = {'prefer_float32': prefer_float32}
    SINGLE_VARIANTS.extend([
        ('lapjvs' + suffix, 'lapjvs', options, 'indices'),
        ('lapjvs-mappings' + suffix, 'lapjvs',
         dict(options, jvx_like=False), 'mapping'),
        ('lapjvsa' + suffix, 'lapjvsa', options, 'pairs'),
    ])
for name in NATIVE:
    SINGLE_VARIANTS.append((name + '-indices', name, {}, 'indices'))
    for precision in ('native', 'float32', 'float64'):
        SINGLE_VARIANTS.append((
            name + '-pairs-' + precision, name,
            {'output': 'pairs', 'precision': precision}, 'pairs',
        ))
BATCH_VARIANTS = [
    (label, name + '_batch', options, layout)
    for label, name, options, layout in SINGLE_VARIANTS
    if name not in ('lapjv', 'lapjvc') and layout != 'mapping'
]


def _parameters(variants, large=False):
    parameters = []
    for label, name, options, layout in variants:
        for dtype in ('float32', 'float64'):
            for high in ((10**6, 10**15) if large else (2**24,)):
                marks = []
                base_name = name[:-6] if name.endswith('_batch') else name
                known_failure = large and (
                    (high == 10**15 and base_name not in NATIVE)
                    or (name == 'lapjvc' and dtype == 'float32' and high == 10**6)
                )
                if known_failure:
                    marks.append(pytest.mark.xfail(
                        strict=True, raises=SuboptimalAssignment,
                        reason='Known mixed-scale optimality limit: ' + ISSUE,
                    ))
                case = '{}-{}-high{}'.format(label, dtype, high)
                parameters.append(pytest.param(name, options, layout, dtype, high,
                                               marks=marks, id=case))
    return parameters


def _solver(name):
    if name.startswith(NATIVE) and find_spec('lap._lapjv_rh') is None:
        pytest.skip('R/H is omitted from this legacy-only installation')
    return getattr(lap, name)


def _working_dtype(name, options, input_dtype):
    if name.startswith(('lapjvs', 'lapjvsa')):
        return 'float32' if options.get('prefer_float32', True) else input_dtype
    if name.startswith(NATIVE):
        precision = options.get('precision', 'native')
        return input_dtype if precision == 'native' else precision
    return input_dtype if name == 'lapjvc' else 'float64'


@lru_cache(maxsize=None)
def _reported_cost(high, dtype, large):
    if large:
        # RandomState preserves the issue's np.random.seed(0)/rand sequence.
        cost = np.random.RandomState(0).random_sample((N, N)) * 10
        cost[CHEAP_ROWS:] = high
        cost = cost.astype(dtype)
    else:
        cost = np.array([[high, high], [.125, .25]], dtype=dtype)
    cost.setflags(write=False)
    return cost


@lru_cache(maxsize=None)
def _cheap_reference(input_dtype, working_dtype):
    cheap = _reported_cost(10**6, input_dtype, True)[:CHEAP_ROWS].astype(working_dtype)
    rows, cols = linear_sum_assignment(cheap)
    return math.fsum(float(value) for value in cheap[rows, cols])


def _pairs(result, layout, n):
    if layout == 'pairs':
        assert isinstance(result, np.ndarray) and result.shape == (n, 2)
        rows, cols = result.T
    else:
        assert isinstance(result, tuple) and len(result) == 2
        rows, cols = result
        assert isinstance(rows, np.ndarray) and isinstance(cols, np.ndarray)
        assert rows.shape == cols.shape == (n,)
    assert rows.dtype.kind in 'iu' and cols.dtype.kind in 'iu'
    assert np.all((rows >= 0) & (rows < n))
    assert np.all((cols >= 0) & (cols < n))
    assert len(np.unique(rows)) == len(np.unique(cols)) == n
    if layout == 'mapping':
        x, y = rows, cols
        np.testing.assert_array_equal(y[x], np.arange(n))
        rows, cols = np.arange(n), x
    return np.column_stack((rows, cols))


def _check_total(total, cost, pairs):
    assert np.ndim(total) == 0 and np.isfinite(total)
    selected = cost[tuple(pairs.T)]
    # Allow float64 accumulation error only for the reported API total.
    # Optimality is checked below without the large constant contribution.
    expected = math.fsum(float(value) for value in selected)
    tolerance = len(selected) * np.finfo(np.float64).eps
    assert math.isclose(float(total), expected, rel_tol=tolerance, abs_tol=0)


def _single_result(result, layout, n, return_cost):
    if return_cost:
        assert isinstance(result, tuple)
        assert len(result) == (2 if layout == 'pairs' else 3)
        total = result[0]
        assignment = result[1] if layout == 'pairs' else result[1:]
    else:
        total, assignment = None, result
    return total, _pairs(assignment, layout, n)


def _batch_result(result, layout, costs, return_cost):
    if return_cost:
        assert isinstance(result, tuple)
        assert len(result) == (2 if layout == 'pairs' else 3)
        totals = result[0]
        assert isinstance(totals, np.ndarray)
        assert totals.shape == (len(costs),) and totals.dtype == np.float64
        assignments = result[1] if layout == 'pairs' else result[1:]
    else:
        totals, assignments = None, result
    if layout == 'pairs':
        assert isinstance(assignments, list) and len(assignments) == len(costs)
    else:
        assert isinstance(assignments, tuple) and len(assignments) == 2
        rows, cols = assignments
        assert isinstance(rows, list) and isinstance(cols, list)
        assert len(rows) == len(cols) == len(costs)
        assignments = list(zip(rows, cols))
    pairs = [_pairs(item, layout, costs.shape[1]) for item in assignments]
    if return_cost:
        for total, cost, assignment in zip(totals, costs, pairs):
            _check_total(total, cost, assignment)
    return pairs


def _cheap_selected_cost(cost, pairs, working_dtype):
    cheap_pairs = pairs[pairs[:, 0] < CHEAP_ROWS]
    assert len(cheap_pairs) == CHEAP_ROWS
    selected = cost[tuple(cheap_pairs.T)].astype(working_dtype)
    return math.fsum(float(value) for value in selected)


def _check_optimum(cost, pairs, working_dtype, large):
    if large:
        # Every full matching pays for all 50 constant rows. Remove that fixed
        # contribution from both objectives, not from the solver's input.
        actual = _cheap_selected_cost(cost, pairs, working_dtype)
        expected = _cheap_reference(cost.dtype.name, working_dtype)
        gap = actual - expected
        assert gap >= -1e-10, 'The reference is more expensive than the solver result'
        if gap > 1e-10:
            raise SuboptimalAssignment(
                'Cheap-row cost {:.15g}; optimum {:.15g}; gap {:.15g}'.format(
                    actual, expected, gap))
    else:
        represented = cost.astype(working_dtype)
        exact = lambda row, col: Fraction.from_float(float(represented[row, col]))
        actual = sum((exact(row, col) for row, col in pairs), Fraction())
        expected = min(sum((exact(row, col) for row, col in enumerate(cols)), Fraction())
                       for cols in permutations(range(len(cost))))
        assert expected == Fraction(2**24) + Fraction(1, 8)
        assert actual == expected


@pytest.mark.parametrize('name,options,layout,dtype,high', _parameters(SINGLE_VARIANTS))
@pytest.mark.parametrize('return_cost', [False, True])
def test_issue_94_exact_float32_example(name, options, layout, dtype, high, return_cost):
    cost = _reported_cost(high, dtype, False)
    original = cost.copy()
    result = _solver(name)(cost, return_cost=return_cost, **options)
    total, pairs = _single_result(result, layout, len(cost), return_cost)
    np.testing.assert_array_equal(cost, original)
    if return_cost:
        _check_total(total, cost, pairs)
    _check_optimum(cost, pairs, _working_dtype(name, options, dtype), False)


@pytest.mark.parametrize('name,options,layout,dtype,high', _parameters(SINGLE_VARIANTS, large=True))
@pytest.mark.parametrize('return_cost', [False, True])
def test_issue_94_large_constant_rows(name, options, layout, dtype, high, return_cost):
    cost = _reported_cost(high, dtype, True)
    original = cost.copy()
    result = _solver(name)(cost, return_cost=return_cost, **options)
    total, pairs = _single_result(result, layout, len(cost), return_cost)
    np.testing.assert_array_equal(cost, original)
    if return_cost:
        _check_total(total, cost, pairs)
    _check_optimum(cost, pairs, _working_dtype(name, options, dtype), True)


def _check_batch(name, options, layout, dtype, high, return_cost, n_threads, large):
    base = _reported_cost(high, dtype, large)
    # A column permutation preserves the optimum but changes the assignments.
    costs = np.stack((base, base[:, ::-1]))
    original = costs.copy()
    costs.setflags(write=False)
    result = _solver(name)(costs, return_cost=return_cost, n_threads=n_threads, **options)
    assignments = _batch_result(result, layout, costs, return_cost)
    np.testing.assert_array_equal(costs, original)
    # Check every result's structure and total before a known optimality failure
    # can trigger xfail. No malformed later result can be hidden by an earlier one.
    working_dtype = _working_dtype(name, options, dtype)
    single_name = name[:-6]
    if large and high == 10**15 and single_name not in NATIVE:
        # For known suboptimal paths, a swapped batch result must still fail
        # normally. Compare each cheap objective with its corresponding single
        # call before checking either result against the independent optimum.
        for cost, pairs in zip(costs, assignments):
            single = _solver(single_name)(cost, return_cost=False, **options)
            _, single_pairs = _single_result(single, layout, len(cost), False)
            actual = _cheap_selected_cost(cost, pairs, working_dtype)
            corresponding = _cheap_selected_cost(cost, single_pairs, working_dtype)
            assert math.isclose(actual, corresponding, rel_tol=0, abs_tol=1e-10), (
                'Batch result differs from its corresponding single call')
        np.testing.assert_array_equal(costs, original)
    for cost, pairs in zip(costs, assignments):
        _check_optimum(cost, pairs, working_dtype, large)


@pytest.mark.parametrize('name,options,layout,dtype,high', _parameters(BATCH_VARIANTS))
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_issue_94_exact_example_batch(name, options, layout, dtype, high, return_cost, n_threads):
    _check_batch(name, options, layout, dtype, high, return_cost, n_threads, False)


@pytest.mark.parametrize('name,options,layout,dtype,high', _parameters(BATCH_VARIANTS, large=True))
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_issue_94_large_constant_rows_batch(name, options, layout, dtype, high, return_cost, n_threads):
    _check_batch(name, options, layout, dtype, high, return_cost, n_threads, True)


@pytest.mark.parametrize('high,large', [(2**24, False), (10**6, True), (10**15, True)])
@pytest.mark.parametrize('fast', [False, True])
def test_issue_94_costs_exceed_sparse_contract(high, large, fast):
    cost = _reported_cost(high, 'float64', large)
    n = len(cost)
    problem = (n, cost.reshape(-1), np.arange(n + 1, dtype=np.int32) * n,
               np.tile(np.arange(n, dtype=np.int32), n))
    assert high >= lap.LARGE
    with pytest.raises(ValueError, match='Cost matrix values must be less than'):
        lap.lapmod(*problem, fast=fast)
    with pytest.raises(ValueError, match='Cost matrix values must be less than'):
        lap.lapmod_batch([problem], fast=fast, n_threads=1)
