# Copyright (c) 2026 Ratha SIV | MIT License
"""The same numerical and API contract suite runs against both public R/H families."""

import itertools
from concurrent.futures import ThreadPoolExecutor
from importlib.util import find_spec

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

@pytest.fixture(scope="module", params=["lapjvr", "lapjvh"])
def native(request):
    import lap
    from types import SimpleNamespace

    if find_spec('lap._lapjv_rh') is None:
        pytest.skip('R/H is omitted from this legacy-only installation')
    # Exercise the public lazy exports, including their packaging and wiring.
    return SimpleNamespace(lapjvr=getattr(lap, request.param),
                           lapjvr_batch=getattr(lap, request.param + "_batch"))


def as_pairs(result, output) -> np.ndarray:
    if output == 'pairs':
        assert isinstance(result, np.ndarray)
        return result
    return np.column_stack(result)


def selected_total(cost, pairs):
    # Python 3.12 changed sum() to compensated accumulation. The API returns
    # the original costs accumulated in row order with ordinary float64 adds.
    total = 0.0
    for row, col in pairs:
        total += float(cost[row, col])
    return total


def working_dtype_for(cost):
    dtype = np.asarray(cost).dtype
    return np.float32 if dtype.kind == 'f' and dtype.itemsize == 4 else np.float64


def objective(cost, pairs, limit, *, working_dtype):
    # Optimization sees represented working costs; returned API totals are
    # checked separately with selected_total on the original input.
    represented = np.asarray(cost, dtype=working_dtype)
    total = represented[tuple(pairs.T)].sum(dtype=np.float64)
    if not np.isfinite(limit):
        return total
    half = float(np.dtype(working_dtype).type(float(limit) / 2))
    return total + (sum(represented.shape) - 2 * len(pairs)) * half


def reference(cost, limit, *, working_dtype):
    represented = np.asarray(cost, dtype=working_dtype)
    if np.isfinite(limit):
        n, m = represented.shape
        half = float(np.dtype(working_dtype).type(float(limit) / 2))
        a = np.zeros((n+m, n+m), dtype=np.float64)
        a[:n, :m] = represented
        a[:n, m:] = a[n:, :m] = half
    else:
        a = represented
    rows, cols = linear_sum_assignment(a)
    return a[rows, cols].sum(dtype=np.float64)


@pytest.mark.parametrize('precision,working_dtype', [
    ('float32', np.float32), ('float64', np.float64),
])
def test_reference_uses_represented_half_limit(native, precision, working_dtype):
    cost = np.array([[2**-27, .5], [.5, 2]], dtype=np.float64)
    limit = 1 - 2**-25
    total, pairs = native.lapjvr(cost, cost_limit=limit, precision=precision,
                                output='pairs')
    # Float32 rounds each half upward to .5. Float64 preserves the lower raw
    # half. These two represented objectives have strictly different optima.
    expected = 1.0 if working_dtype == np.float32 else 1 - 3 * 2**-27
    assert reference(cost, limit, working_dtype=working_dtype) == expected
    assert objective(cost, pairs, limit, working_dtype=working_dtype) == expected
    assert len(pairs) == (2 if working_dtype == np.float32 else 1)
    assert total == selected_total(cost, pairs)


@pytest.mark.parametrize('precision,working_dtype', [
    ('float32', np.float32), ('float64', np.float64),
])
def test_reference_quantizes_costs_but_returned_total_uses_original_input(
        native, precision, working_dtype):
    eps = float(np.finfo(np.float32).eps)
    cost = np.array([[1 + 5 * eps / 8, 1., 4.],
                     [1 + 11 * eps / 8, 1 + 5 * eps / 8, 4.]], dtype=np.float64)
    selected_optimum = 2 + eps if working_dtype == np.float32 else 2 + 5 * eps / 4
    for limit in (np.inf, 3.):
        total, pairs = native.lapjvr(cost, extend_cost=True, cost_limit=limit,
                                    precision=precision, output='pairs')
        # A 2x3 complete matching leaves one column unmatched in finite mode.
        expected = selected_optimum + (1.5 if np.isfinite(limit) else 0.)
        assert reference(cost, limit, working_dtype=working_dtype) == expected
        assert objective(cost, pairs, limit, working_dtype=working_dtype) == expected
        assert total == selected_total(cost, pairs)
        if working_dtype == np.float32:
            assert total > 2 + 5 * eps / 4  # Different optimum before quantization.


@pytest.mark.parametrize('seed', [20261017, 20261023, 20261101])
@pytest.mark.parametrize('offsets', ['rows', 'columns', 'both'])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
def test_float32_affine_offsets(native, seed, offsets, output):
    # Retain the two original 1000x1000 failures. Sum the actual float32 costs
    # in float64 so cancellation cannot hide a more expensive assignment.
    n = 1000
    cost = np.random.default_rng(seed).random((n, n))
    shift = np.linspace(-100, 100, n)
    if offsets in ('rows', 'both'):
        cost += shift[:, None]
    if offsets in ('columns', 'both'):
        cost += shift[None, :]
    cost = cost.astype(np.float32)
    cost.setflags(write=False)
    expected = reference(cost, np.inf, working_dtype=working_dtype_for(cost))
    for precision in ('native', 'float32'):
        total, *result = native.lapjvr(cost, precision=precision, output=output)
        pairs = as_pairs(result[0] if output == 'pairs' else result, output)
        assert len(pairs) == len(np.unique(pairs[:, 1])) == n
        assert objective(cost, pairs, np.inf, working_dtype=working_dtype_for(cost)) == expected
        assert total == selected_total(cost, pairs)

    # Reused workspaces and worker threads must return the same optimum.
    native.lapjvr(np.zeros((3, 3), dtype=np.float32))
    batch = np.stack([cost, cost])
    for threads in (1, 2, 0):
        totals, *result = native.lapjvr_batch(batch, n_threads=threads, output=output)
        arrays = result[0] if output == 'pairs' else list(zip(*result))
        np.testing.assert_array_equal(totals, [total, total])
        for array in arrays:
            np.testing.assert_array_equal(as_pairs(array, output), pairs)


@pytest.mark.parametrize('output', ['indices', 'pairs'])
def test_float32_offsets_during_reduction_and_search(native, output):
    # The 2x2 case finishes in row reduction; the 32x32 case needs a shortest
    # path. Widening only the search phase does not fix either failure.
    costs = [np.array([[1000, 1000], [.0001, .00011]], dtype=np.float32)]
    costs.append((np.random.default_rng(1384).random((32, 32))
                  + np.linspace(-100, 100, 32)[:, None]).astype(np.float32))
    for cost in costs:
        result = native.lapjvr(cost, return_cost=False, output=output)
        pairs = as_pairs(result, output)
        assert objective(cost, pairs, np.inf, working_dtype=working_dtype_for(cost)) == reference(cost, np.inf, working_dtype=working_dtype_for(cost))


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('seed,n', [
    (20261017, 127), (20261017, 128), (20261017, 129),
    (20261017, 250), (20261023, 250), (20261101, 250),
    (20261017, 1000), (20261023, 1000), (20261101, 1000),
])
def test_required_block_conflicts_and_workspace_reuse(native, dtype, output, seed, n):
    rng = np.random.default_rng(seed)
    cost = np.full((n, n), 10, dtype=dtype)
    cost[:3*n//4, :n//4] = rng.random((3*n//4, n//4))
    cost[3*n//4:, n//4:] = rng.random((n-3*n//4, n-n//4))
    permuted = cost[rng.permutation(n)][:, rng.permutation(n)]
    forbidden = permuted.copy()
    forbidden[0, :n//2] = np.inf
    shifted = cost + np.linspace(-100, 100, n, dtype=dtype)[:, None]
    balanced = np.full((n, n), 10, dtype=dtype)
    balanced[:n//2, :n//2] = rng.random((n//2, n//2))
    balanced[n//2:, n//2:] = rng.random((n-n//2, n-n//2))
    repeated = cost[np.where(np.arange(n) < 3*n//4, 0, n-1)]
    for actual in (cost, permuted, cost.T, forbidden, shifted, balanced, repeated):
        actual.setflags(write=False)
        total, *result = native.lapjvr(actual, output=output)
        pairs = as_pairs(result[0] if output == 'pairs' else result, output)
        np.testing.assert_array_equal(pairs[:, 0], np.arange(n))
        np.testing.assert_array_equal(np.sort(pairs[:, 1]), np.arange(n))
        expected = reference(actual, np.inf, working_dtype=working_dtype_for(actual))
        if dtype == np.float32:
            assert objective(actual, pairs, np.inf, working_dtype=working_dtype_for(actual)) == expected
        else:
            np.testing.assert_allclose(objective(actual, pairs, np.inf, working_dtype=working_dtype_for(actual)), expected,
                                       rtol=1e-12, atol=1e-12)
        assert total == selected_total(actual, pairs)
        native.lapjvr(np.zeros((3, 3), dtype=dtype))
        repeated = native.lapjvr(actual, return_cost=False, output=output)
        np.testing.assert_array_equal(as_pairs(repeated, output), pairs)

    batch = np.stack([cost, permuted])
    serial = native.lapjvr_batch(batch, output=output, n_threads=1)
    for threads in (2, 0):
        parallel = native.lapjvr_batch(batch, output=output, n_threads=threads)
        for actual, expected in zip(parallel, serial):
            np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('n', [127, 128, 129, 511, 512, 769])
def test_heterogeneous_square_rows_offsets_forbidden_and_permutations(native, dtype, output, n):
    rng = np.random.default_rng(97031+n)
    costs = rng.integers(80, 101, (n, n)).astype(dtype)
    easy = np.arange(3*n//4)
    costs[easy, (easy*7+3) % n] = 0
    permuted = costs[rng.permutation(n)][:, rng.permutation(n)]
    forbidden = permuted.copy()
    forbidden[1, :n//2] = np.inf
    misleading = rng.integers(0, 32, (n, n)).astype(dtype)
    misleading[np.arange(8)*(n-1)//7] += np.arange(8, dtype=dtype)[:, None]*100
    row_offsets = np.arange(n, dtype=dtype)[:, None]*8
    magnitude = 2**18 if dtype == np.float32 else 2**40
    for centered in (costs, permuted, forbidden, misleading, costs+row_offsets):
        # Exact integer costs let us check centered objectives exactly, even
        # after a large common offset that would hide errors in a relative check.
        for offset in (-magnitude, 0, magnitude):
            actual = centered+dtype(offset)
            actual.setflags(write=False)
            result = native.lapjvr(actual, output=output)
            selected = as_pairs(result[1] if output == 'pairs' else result[1:], output)
            assert len(selected) == n
            assert len(np.unique(selected[:, 1])) == n
            assert objective(centered, selected, np.inf, working_dtype=working_dtype_for(centered)) == reference(centered, np.inf, working_dtype=working_dtype_for(centered))
            assert result[0] == selected_total(actual, selected)
    infeasible = costs.copy()
    infeasible[1] = np.inf
    with pytest.raises(ValueError):
        native.lapjvr(infeasible)
    assert native.lapjvr(costs)[0] == reference(costs, np.inf, working_dtype=working_dtype_for(costs))


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('shape', [(1, 1), (1, 6), (6, 1), (4, 4), (3, 8), (8, 3)])
@pytest.mark.parametrize('limit', [np.inf, 0.5, -0.5, 0.0])
def test_seeded_objective_orientation_and_original_totals(native, dtype, output, shape, limit):
    rng = np.random.default_rng(417)
    for _ in range(5):
        cost = rng.integers(-4, 7, size=shape).astype(dtype)
        total, *rest = native.lapjvr(cost, extend_cost=True, cost_limit=limit, output=output)
        pairs = rest[0] if output == 'pairs' else np.column_stack(rest)
        assert pairs.shape[1] == 2 and pairs.dtype == np.int64
        assert len(np.unique(pairs[:, 0])) == len(np.unique(pairs[:, 1])) == len(pairs)
        assert np.all(pairs[1:, 0] > pairs[:-1, 0])
        assert total == cost[tuple(pairs.T)].sum(dtype=np.float64)
        if not np.isfinite(limit):
            assert len(pairs) == min(shape)
        assert objective(cost, pairs, limit, working_dtype=working_dtype_for(cost)) == pytest.approx(reference(cost, limit, working_dtype=working_dtype_for(cost)))


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_small_tied_optional_objective_by_enumeration(native, dtype):
    # Independent of any JV implementation or the augmented SciPy reference.
    rng = np.random.default_rng(515)
    for n, m in [(2, 3), (3, 2), (3, 3)]:
        for _ in range(30):
            cost = rng.integers(-3, 6, (n, m)).astype(dtype)
            limit = float(rng.integers(-2, 5))
            half = float(np.dtype(dtype).type(limit / 2))
            best = np.inf
            for k in range(min(n, m) + 1):
                for rows in itertools.combinations(range(n), k):
                    for cols in itertools.permutations(range(m), k):
                        value = sum(float(cost[i, j]) for i, j in zip(rows, cols)) + (n+m-2*k)*half
                        best = min(best, value)
            pairs = native.lapjvr(cost, cost_limit=limit, return_cost=False, output='pairs')
            assert objective(cost, pairs, limit, working_dtype=working_dtype_for(cost)) == best


@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('threads', [None, 0, -2, 1, 2, 8, np.int64(2)])
@pytest.mark.parametrize('limit', [np.inf, 0.5])
def test_batch_matches_single_exactly_and_preserves_input(native, output, threads, limit):
    costs = np.random.default_rng(6).random((7, 9, 5))[:, ::-1, ::-1]
    original = costs.copy()
    costs.setflags(write=False)
    results = native.lapjvr_batch(costs, extend_cost=True, cost_limit=limit,
                                  n_threads=threads, output=output)
    totals, arrays = results if output == 'pairs' else (results[0], list(zip(results[1], results[2])))
    for b, (total, result) in enumerate(zip(totals, arrays)):
        expected = native.lapjvr(costs[b], extend_cost=True, cost_limit=limit, output=output)
        expected_pairs = expected[1] if output == 'pairs' else np.column_stack(expected[1:])
        assert total == expected[0]
        np.testing.assert_array_equal(as_pairs(result, output), expected_pairs)
    np.testing.assert_array_equal(costs, original)


@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('shape', [(0, 3), (3, 0), (0, 0)])
def test_empty_inputs_and_singleton_batches(native, output, shape):
    cost = np.empty(shape)
    result = native.lapjvr(cost, output=output)
    assert result[0] == 0.0
    pairs = result[1] if output == 'pairs' else np.column_stack(result[1:])
    assert pairs.shape == (0, 2)
    for b in [0, 1, 3]:
        batch = native.lapjvr_batch(np.empty((b,) + shape), n_threads=8, output=output)
        assert len(batch[0]) == b
        np.testing.assert_array_equal(batch[0], 0)
        assert len(batch[1]) == b


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('shape', [(4, 4), (4, 7), (7, 4)])
def test_forbidden_edges_and_error_recovery(native, dtype, shape):
    cost = np.full(shape, np.inf, dtype=dtype)
    np.fill_diagonal(cost, 1)
    result = native.lapjvr(cost, extend_cost=True, output='pairs')
    assert result[0] == min(shape)
    np.testing.assert_array_equal(result[1], np.column_stack([np.arange(min(shape))] * 2))
    bad = np.full((3, 3), np.inf, dtype=dtype)
    bad[:, 0] = 0
    for _ in range(2):
        with pytest.raises(ValueError, match='infeasible'):
            native.lapjvr(bad)
        assert native.lapjvr(np.eye(2, dtype=dtype))[0] == 0
    np.testing.assert_array_equal(native.lapjvr(np.array([[-10, 3], [np.inf, 3]], dtype=dtype), output='pairs')[1], [[0, 0], [1, 1]])


def test_limit_fixture_totals_original_precision_and_range(native):
    total, pairs = native.lapjvr(np.array([[.1, .2], [.2, 1.]]), cost_limit=.15, output='pairs')
    assert total == .1
    np.testing.assert_array_equal(pairs, [[0, 0]])
    # Explicit float32 changes which represented problem is optimized, but the
    # returned total must use the original float64 costs selected by that solve.
    a = np.array([[1.00000001, 9], [9, 2.00000002]])
    assert native.lapjvr(a, precision='float32')[0] == a.diagonal().sum()
    assert native.lapjvr(np.array([[1e100]]))[0] == 1e100
    with pytest.raises(ValueError, match='overflow'):
        native.lapjvr(np.array([[1e100]]), precision='float32')
    with pytest.raises(ValueError, match='overflow'):
        native.lapjvr(np.ones((1, 1), dtype=np.float32), cost_limit=1e100)


@pytest.mark.parametrize('sign', [-1, 1])
def test_float32_downcast_checks_original_range_and_recovers(native, sign):
    largest = float(np.finfo(np.float32).max)
    # The next float64 value would round back into float32 range on conversion.
    # It must nevertheless be rejected, preserving the strict input contract.
    outside = np.nextafter(largest, np.inf)
    for value in (outside, 1e100):
        with pytest.raises(ValueError, match='Finite costs overflow float32'):
            native.lapjvr(np.array([[sign * value]]), precision='float32')
    total, pairs = native.lapjvr(np.array([[sign * largest]]),
                               precision='float32', output='pairs')
    assert total == sign * largest
    np.testing.assert_array_equal(pairs, [[0, 0]])


@pytest.mark.parametrize('layout', ['contiguous', 'strided', 'unaligned', 'big-endian'])
def test_float32_downcast_preserves_original_totals_and_forbidden_edges(native, layout):
    cost = np.array([[1.00000001, np.inf, 9.],
                     [np.inf, 2.00000002, 8.]])
    if layout == 'strided':
        storage = np.zeros((2, 6))
        storage[:, ::2] = cost
        cost = storage[:, ::2]
    elif layout == 'unaligned':
        storage = np.ndarray(cost.shape, dtype=np.float64,
                             buffer=bytearray(cost.nbytes + 1), offset=1)
        storage[:] = cost
        cost = storage
    elif layout == 'big-endian':
        cost = cost.astype('>f8')
    cost.setflags(write=False)
    total, pairs = native.lapjvr(cost, extend_cost=True, precision='float32', output='pairs')
    np.testing.assert_array_equal(pairs, [[0, 0], [1, 1]])
    assert total == float(cost[0, 0]) + float(cost[1, 1])
    totals, batch = native.lapjvr_batch(np.stack([cost] * 3), extend_cost=True,
                                      precision='float32', n_threads=2, output='pairs')
    np.testing.assert_array_equal(totals, [total] * 3)
    for result in batch:
        np.testing.assert_array_equal(result, pairs)


@pytest.mark.parametrize('shape', [(65, 33), (97, 65), (129, 32)])
@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('limit', [np.inf, .5])
def test_tall_tile_boundaries_preserve_objective_and_original_indices(native, shape, dtype, limit):
    costs = np.random.default_rng(1927).normal(size=(3,) + shape).astype(dtype)
    totals, arrays = native.lapjvr_batch(costs, extend_cost=True, cost_limit=limit,
                                       output='pairs', n_threads=2)
    for cost, total, pairs in zip(costs, totals, arrays):
        assert np.all(pairs[1:, 0] > pairs[:-1, 0])
        assert total == pytest.approx(cost[tuple(pairs.T)].sum(dtype=np.float64), rel=1e-14)
        assert objective(cost, pairs, limit, working_dtype=working_dtype_for(cost)) == pytest.approx(reference(cost, limit, working_dtype=working_dtype_for(cost)))
        single = native.lapjvr(cost, extend_cost=True, cost_limit=limit, output='pairs')
        np.testing.assert_array_equal(single[1], pairs)


@pytest.mark.parametrize('output', ['indices', 'pairs'])
def test_return_modes_precision_and_empty_batch(native, output):
    # Each precision has a unique optimum; this does not freeze an arbitrary
    # tie-breaking choice for costs that all round to the same float32 value.
    eps = float(np.finfo(np.float32).eps)
    a = np.array([[1. + 5 * eps / 8, 1.],
                  [1. + 11 * eps / 8, 1. + 5 * eps / 8]], dtype=np.float64)
    assert native.lapjvr(a, output=output)[0] == a.diagonal().sum()
    low = native.lapjvr(a, precision='float32', output=output)
    low_pairs = low[1] if output == 'pairs' else np.column_stack(low[1:])
    assert low[0] == a[tuple(low_pairs.T)].sum(dtype=np.float64)
    np.testing.assert_array_equal(low_pairs, [[0, 1], [1, 0]])
    batch = np.stack([a] * 3)
    result = native.lapjvr_batch(batch, precision='float32', n_threads=2, output=output)
    without_total = native.lapjvr_batch(batch, precision='float32', n_threads=2,
                                      output=output, return_cost=False)
    actual = without_total if output == 'pairs' else list(zip(*without_total))
    for item in actual:
        np.testing.assert_array_equal(as_pairs(item, output), low_pairs)
    np.testing.assert_array_equal(result[0], [low[0]] * 3)
    empty = native.lapjvr_batch(np.empty((0, 2, 3)), output=output)
    assert empty[0].shape == (0,) and len(empty[1]) == 0
    native.lapjvr(a.astype('>f4'), output=output)


def test_displacement_regression_and_close_float64_costs(native):
    a = np.array([[892, 268, 833, 935], [499, 240, 956, 778],
                  [312, 269, 683, 479], [320, 351, 355, 97]], dtype=np.float64)
    assert native.lapjvr(a)[0] == 1482
    a = np.array([[1e9 + .2, 1e9], [1e9, 1e9 + .2]])
    total, pairs = native.lapjvr(a, output='pairs')
    assert total == 2e9
    np.testing.assert_array_equal(pairs, [[0, 1], [1, 0]])


def test_unaligned_numeric_and_strided_conversions(native):
    cost = np.ndarray((4, 4), dtype=np.float64, buffer=bytearray(4*4*8+1), offset=1)
    cost[:] = np.arange(16).reshape(4, 4)
    assert not cost.flags.aligned
    assert native.lapjvr(cost)[0] == reference(cost, np.inf, working_dtype=working_dtype_for(cost))
    for dtype in (np.float16, np.int16, np.int64, np.bool_):
        a = np.eye(3, dtype=dtype)[:, ::-1]
        assert native.lapjvr(a)[0] == reference(a.astype(float), np.inf, working_dtype=working_dtype_for(a.astype(float)))


@pytest.mark.parametrize('kind', ['list', 'subclass', 'array-protocol'])
@pytest.mark.parametrize('batch', [False, True])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
def test_array_like_inputs_keep_numpy_conversion_semantics(native, kind, batch, output):
    class CostArray(np.ndarray):
        pass

    class ArrayLike:
        def __array__(self, dtype=None, copy=None):
            return np.array(cost, dtype=dtype, copy=True)

    cost = np.array([[.1, .9, .8], [.8, .2, .9]])
    if batch:
        cost = np.stack([cost] * 3)
    if kind == 'list':
        value = cost.tolist()
    elif kind == 'subclass':
        value = cost.view(CostArray)
    else:
        value = ArrayLike()
    solve = native.lapjvr_batch if batch else native.lapjvr
    result = solve(value, extend_cost=True, return_cost=False, output=output)
    if not batch:
        arrays = [result]
    elif output == 'pairs':
        arrays = result
    else:
        arrays = list(zip(*result))
    for array in arrays:
        pairs = as_pairs(array, output)
        assert type(pairs) is np.ndarray
        assert pairs.dtype == np.int64 and pairs.flags.aligned
        np.testing.assert_array_equal(pairs, [[0, 0], [1, 1]])


def test_concurrent_calls_and_deterministic_batch_failure(native):
    batch = np.random.default_rng(91).random((16, 30, 25))
    batch.setflags(write=False)
    def run(threads):
        return native.lapjvr_batch(batch, extend_cost=True, n_threads=threads, output='pairs')
    expected = run(1)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(run, [1, 2, 8, 3, 2, 1, 4, 8]):
            np.testing.assert_array_equal(result[0], expected[0])
            for actual, wanted in zip(result[1], expected[1]):
                np.testing.assert_array_equal(actual, wanted)
    bad = np.zeros((5, 3, 3))
    bad[2, :, 1:] = np.inf
    bad[4, :, :] = np.inf
    with pytest.raises(ValueError, match='batch index 2'):
        native.lapjvr_batch(bad, n_threads=3)
    assert len(run(3)[0]) == 16


@pytest.mark.parametrize('kwargs', [dict(precision='bad'), dict(output='bad'),
                                  dict(cost_limit=np.nan), dict(cost_limit=-np.inf)])
def test_invalid_options(native, kwargs):
    with pytest.raises(ValueError):
        native.lapjvr(np.ones((2, 2)), **kwargs)


def test_structural_validation_before_materialization(native):
    with pytest.raises(ValueError, match='int32'):
        native.lapjvr(np.broadcast_to(0., (1, 2**31)), extend_cost=True)
    with pytest.raises(ValueError, match='Square'):
        native.lapjvr(np.zeros((2, 3)))
    with pytest.raises(TypeError):
        native.lapjvr(np.array([[1j]]))
    with pytest.raises(ValueError, match='2-dimensional'):
        native.lapjvr(np.zeros((2, 3, 4)))
    with pytest.raises(ValueError, match='3-dimensional'):
        native.lapjvr_batch(np.zeros((2, 3)))
    for value in ('invalid', [], {}):
        with pytest.raises((TypeError, ValueError)):
            native.lapjvr_batch(np.empty((0, 2, 2)), n_threads=value)


@pytest.mark.parametrize('n_threads,cpu_count', [
    (None, 16), (0, 24), (0, 256), (0, None), (0, 0), (0, 1),
    (1, 24), (-2, 24), (32, 2),
])
def test_batch_cpu_count_is_detected_per_automatic_call(native, monkeypatch, n_threads, cpu_count):
    import os

    costs = np.random.default_rng(20261019).random((12, 96, 96))
    costs.setflags(write=False)
    expected = native.lapjvr_batch(costs, n_threads=1, output='pairs')
    detected = []

    def get_cpu_count():
        assert n_threads is None or n_threads == 0
        detected.append(cpu_count)
        return cpu_count

    monkeypatch.setattr(os, 'cpu_count', get_cpu_count)
    actual = native.lapjvr_batch(costs, n_threads=n_threads, output='pairs')
    assert detected == ([cpu_count] if n_threads is None or n_threads == 0 else [])
    np.testing.assert_array_equal(actual[0], expected[0])
    for pairs, expected_pairs in zip(actual[1], expected[1]):
        np.testing.assert_array_equal(pairs, expected_pairs)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('shape', [(2, 3), (3, 2), (15, 16), (16, 15),
                                  (8, 128), (128, 8), (1, 1024), (1024, 1)])
def test_native_rectangles_negative_forbidden_and_seeded_floats(native, dtype, shape):
    rng = np.random.default_rng(712)
    for _ in range(12):
        a = rng.normal(-3, 4, shape).astype(dtype)
        missing = rng.random(shape) < .35
        np.fill_diagonal(missing, False)
        a[missing] = np.inf
        total, pairs = native.lapjvr(a, extend_cost=True, output='pairs')
        expected = reference(a, np.inf, working_dtype=working_dtype_for(a))
        assert total == pytest.approx(expected, rel=2e-6 if dtype == np.float32 else 1e-11, abs=1e-5 if dtype == np.float32 else 1e-11)
        assert len(pairs) == min(shape)
        assert np.all(pairs[1:, 0] > pairs[:-1, 0])
        assert len(np.unique(pairs[:, 1])) == len(pairs)
        assert np.isfinite(a[tuple(pairs.T)]).all()


@pytest.mark.parametrize('shape', [(2, 5), (5, 2), (20, 1000), (1000, 20)])
@pytest.mark.parametrize('output', ['pairs', 'indices'])
def test_native_rectangular_batch_ties_order_and_failure_recovery(native, shape, output):
    costs = np.zeros((4,) + shape)
    serial = native.lapjvr_batch(costs, extend_cost=True, output=output, n_threads=1)
    for threads in (0, 2, 8):
        parallel = native.lapjvr_batch(costs, extend_cost=True, output=output, n_threads=threads)
        np.testing.assert_array_equal(parallel[0], serial[0])
        for actual_group, expected_group in zip(parallel[1:], serial[1:]):
            for actual, expected in zip(actual_group, expected_group):
                np.testing.assert_array_equal(actual, expected)
    bad = np.ones((3,) + shape)
    bad[1] = np.inf
    with pytest.raises(ValueError, match='batch index 1'):
        native.lapjvr_batch(bad, extend_cost=True, output=output, n_threads=2)
    recovered = native.lapjvr_batch(costs, extend_cost=True, output=output, n_threads=2)
    np.testing.assert_array_equal(recovered[0], serial[0])


def test_rectangular_unused_infinite_columns_and_hall_infeasibility(native):
    a = np.array([[0., 1., np.inf], [0., 100., np.inf]])
    assert native.lapjvr(a, extend_cost=True)[0] == 1.
    bad = np.array([[0., np.inf, np.inf, np.inf], [1., np.inf, np.inf, np.inf]])
    for cost in (bad, bad.T):
        with pytest.raises(ValueError, match='infeasible'):
            native.lapjvr(cost, extend_cost=True)


def test_rectangular_float32_reduced_costs_use_wide_arithmetic(native):
    magnitude = np.float32(3e38)
    a = np.array([[-magnitude, magnitude, magnitude], [-magnitude, 0., magnitude]], dtype=np.float32)
    for cost in (a, a.T):
        total, pairs = native.lapjvr(cost, extend_cost=True, output='pairs')
        assert len(pairs) == 2
        # The reduced-cost range exceeds float32, while the represented optimum
        # and the float64 working arithmetic are finite.
        assert total == -float(magnitude)
        assert float(cost[tuple(pairs.T)].sum(dtype=np.float64)) == total


def test_rectangular_float64_reduced_cost_overflow_is_an_error(native):
    magnitude = 1e308
    a = np.array([[-magnitude, magnitude, magnitude], [-magnitude, 0., magnitude]], dtype=np.float64)
    for cost in (a, a.T):
        with pytest.raises(ValueError, match='overflow'):
            native.lapjvr(cost, extend_cost=True)
    good = np.array([[0., 1., 2.], [1., 0., 2.]], dtype=np.float64)
    assert native.lapjvr(good, extend_cost=True)[0] == 0.


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['pairs', 'indices'])
@pytest.mark.parametrize('shape', [(1, 1), (2, 3), (3, 2), (8, 8), (17, 64), (64, 17)])
@pytest.mark.parametrize('limit', [-2., 0., .15, .5, 4.])
def test_implicit_limits_objective_and_batch(native, dtype, output, shape, limit):
    rng = np.random.default_rng(915)
    costs = rng.normal(0, 2, (4,) + shape).astype(dtype)
    costs[rng.random(costs.shape) < .3] = np.inf
    costs[1] = np.inf  # Optional matching is feasible even without any edges.
    costs.setflags(write=False)
    results = native.lapjvr_batch(costs, cost_limit=limit, output=output, n_threads=2)
    arrays = results[1] if output == 'pairs' else list(zip(*results[1:]))
    for cost, total, array in zip(costs, results[0], arrays):
        pairs = as_pairs(array, output)
        single = native.lapjvr(cost, cost_limit=limit, output=output)
        assert total == single[0]
        assert total == pytest.approx(cost[tuple(pairs.T)].sum(dtype=np.float64), rel=1e-14, abs=1e-14)
        np.testing.assert_array_equal(pairs, as_pairs(single[1] if output == 'pairs' else single[1:], output))
        assert objective(cost, pairs, limit, working_dtype=working_dtype_for(cost)) == pytest.approx(reference(cost, limit, working_dtype=working_dtype_for(cost)), rel=2e-6, abs=2e-6)
        assert len(np.unique(pairs[:, 0])) == len(np.unique(pairs[:, 1])) == len(pairs)
        assert np.all(pairs[1:, 0] > pairs[:-1, 0])
        assert np.isfinite(cost[tuple(pairs.T)]).all()


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_implicit_limit_is_optimized_before_pair_selection(native, dtype):
    a = np.array([[.1, .14], [.14, .9]], dtype=dtype)
    total, pairs = native.lapjvr(a, cost_limit=.15, output='pairs')
    np.testing.assert_array_equal(pairs, [[0, 0]])
    assert total == float(a[0, 0])
    # Every edge equals the rejection threshold: any cardinality is optimal.
    tied = np.full((3, 4), 2., dtype=dtype)
    pairs = native.lapjvr(tied, cost_limit=2., output='pairs')[1]
    assert objective(tied, pairs, 2., working_dtype=working_dtype_for(tied)) == reference(tied, 2., working_dtype=working_dtype_for(tied))
    tiny = np.nextafter(dtype(0), dtype(1))
    tied = np.array([[tiny]], dtype=dtype)
    pairs = native.lapjvr(tied, cost_limit=float(tiny), output='pairs')[1]
    # The represented half-limit underflows to zero in both cost dtypes.
    # Rejection therefore costs zero; raw-limit arithmetic would incorrectly
    # treat matching and rejection as tied at tiny.
    assert len(pairs) == 0
    assert objective(tied, pairs, float(tiny), working_dtype=dtype) == 0.
    assert reference(tied, float(tiny), working_dtype=dtype) == 0.
    assert native.lapjvr(np.array([[-tiny]], dtype=dtype), cost_limit=float(tiny))[0] == -float(tiny)


def test_implicit_limit_concurrent_pools_and_original_totals(native):
    costs = np.random.default_rng(42).random((8, 20, 30))[:, ::-1, ::-1]
    costs.setflags(write=False)
    def run(threads):
        return native.lapjvr_batch(costs, cost_limit=.15, precision='float32', output='pairs', n_threads=threads)
    serial = run(1)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for totals, arrays in pool.map(run, [0, 2, 3, 8, 2, 1, 4, 8]):
            np.testing.assert_array_equal(totals, serial[0])
            for pairs, expected in zip(arrays, serial[1]):
                np.testing.assert_array_equal(pairs, expected)
    for a, total, pairs in zip(costs, serial[0], serial[1]):
        assert total == a[tuple(pairs.T)].sum(dtype=np.float64)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('seed', [20261031, 20261103])
def test_structured_thousand_square_objective_and_workspace_reuse(native, dtype, output, seed):
    from lapjvr_cases import tracking_costs

    cost = tracking_costs(1000, 1000, seed, dtype)
    cost.setflags(write=False)
    total, *result = native.lapjvr(cost, output=output)
    pairs = as_pairs(result[0] if output == 'pairs' else result, output)
    rows, cols = linear_sum_assignment(cost)
    tolerance = 2e-6 if dtype == np.float32 else 1e-10
    np.testing.assert_allclose(total, cost[rows, cols].sum(dtype=np.float64),
                               rtol=tolerance, atol=tolerance)
    assert total == selected_total(cost, pairs)
    np.testing.assert_array_equal(pairs[:, 0], np.arange(1000))
    np.testing.assert_array_equal(np.sort(pairs[:, 1]), np.arange(1000))

    # Reuse the same native workspace at a smaller size before solving again.
    native.lapjvr(np.zeros((3, 3), dtype=dtype))
    repeated = native.lapjvr(cost, return_cost=False, output=output)
    np.testing.assert_array_equal(as_pairs(repeated, output), pairs)
    batch = np.stack([cost, cost])
    for threads in (1, 2, 0):
        totals, *results = native.lapjvr_batch(batch, n_threads=threads, output=output)
        arrays = results[0] if output == 'pairs' else list(zip(*results))
        np.testing.assert_array_equal(totals, [total, total])
        for array in arrays:
            np.testing.assert_array_equal(as_pairs(array, output), pairs)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('n', [9, 17, 65, 129, 257])
def test_square_and_near_square_centered_objectives(native, dtype, n):
    rng = np.random.default_rng(129+n)
    offset = 2**20 if dtype == np.float32 else 2**30
    scale = .5 if dtype == np.float32 else 2**-10
    for shape in [(n,n), (n,n+1), (n+1,n)]:
        a = (offset + rng.normal(0,scale,shape)).astype(dtype)
        forbidden = rng.random(shape)<.15
        np.fill_diagonal(forbidden,False)
        a[forbidden]=np.inf
        total,pairs=native.lapjvr(a,extend_cost=True,output='pairs')
        centered = a.astype(np.float64)-offset
        rows,cols=linear_sum_assignment(centered)
        assert centered[tuple(pairs.T)].sum() == pytest.approx(centered[rows,cols].sum(), rel=1e-8, abs=1e-7)
        assert total == pytest.approx(a[tuple(pairs.T)].sum(dtype=np.float64), rel=1e-14)
        totals,arrays=native.lapjvr_batch(np.stack([a,a,a]),extend_cost=True,output='pairs',n_threads=2)
        np.testing.assert_array_equal(totals,[total]*3)
        for actual in arrays: np.testing.assert_array_equal(actual,pairs)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('width', range(145, 153))
def test_rectangular_initial_minimum_ties_and_forbidden_edges(native, dtype, output, width):
    rng = np.random.default_rng(100150 + width)
    costs = (rng.integers(-4, 9, (3, 100, width)) / 8).astype(dtype)
    costs[0] = rng.normal(-.25, .5, (100, width))
    missing = rng.random(costs.shape) < .2
    for mask in missing:
        np.fill_diagonal(mask, False)
    costs[missing] = np.inf
    costs[1, :, 0] = np.inf
    costs[2, :, -1] = -2
    # Exercise a forbidden first column, a late minimum, tied reductions, and
    # neighboring odd/even widths through both orientations and batch modes.
    for oriented in (costs, costs.transpose(0, 2, 1).copy()):
        for limit in (np.inf, .5):
            serial = native.lapjvr_batch(oriented, extend_cost=True, cost_limit=limit,
                                        output=output, n_threads=1)
            parallel = native.lapjvr_batch(oriented, extend_cost=True, cost_limit=limit,
                                          output=output, n_threads=2)
            np.testing.assert_array_equal(serial[0], parallel[0])
            for i, cost in enumerate(oriented):
                single = native.lapjvr(cost, extend_cost=True, cost_limit=limit, output=output)
                pairs = as_pairs(single[1] if output == 'pairs' else single[1:], output)
                assert objective(cost, pairs, limit, working_dtype=working_dtype_for(cost)) == pytest.approx(
                    reference(cost, limit, working_dtype=working_dtype_for(cost)), rel=2e-6 if dtype == np.float32 else 1e-11)
                assert single[0] == serial[0][i]
                assert single[0] == pytest.approx(cost[tuple(pairs.T)].sum(dtype=np.float64), rel=1e-14)
                for result in (serial, parallel):
                    actual = result[1][i] if output == 'pairs' else (result[1][i], result[2][i])
                    np.testing.assert_array_equal(as_pairs(actual, output), pairs)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('shape', [(16,16), (4,128), (50,75), (75,50)])
@pytest.mark.parametrize('limit', [np.inf, .15])
def test_auto_changing_sizes_concurrent_explicit_and_failure_recovery(native, dtype, output, shape, limit):
    rng = np.random.default_rng(8261)
    costs = rng.random((16,) + shape).astype(dtype)[:, ::-1, ::-1]
    costs.setflags(write=False)
    serial = native.lapjvr_batch(costs, extend_cost=True, cost_limit=limit,
                                 output=output, n_threads=1)
    def run(spec):
        size, threads = spec
        result = native.lapjvr_batch(costs[:size], extend_cost=True, cost_limit=limit,
                                     output=output, n_threads=threads)
        np.testing.assert_array_equal(result[0], serial[0][:size])
        for group, expected in zip(result[1:], serial[1:]):
            for actual, wanted in zip(group, expected):
                np.testing.assert_array_equal(actual, wanted)
    sequence = [(b, 0) for b in (2,4,8,3,7,1,16,0,5,2,4,8)]
    for spec in sequence:
        run(spec)
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(run, sequence + [(16,t) for t in (None,2,3,4,8,1)]))
    bad = costs[:8].copy()
    bad[2] = bad[6] = np.inf
    if np.isinf(limit):
        with pytest.raises(ValueError, match='batch index 2'):
            native.lapjvr_batch(bad, extend_cost=True, output=output, n_threads=0)
    else:
        result = native.lapjvr_batch(bad, cost_limit=limit, output=output)
        assert result[0][2] == result[0][6] == 0
    run((8,0))


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('n', [15, 16, 17, 19, 31, 32, 33, 50, 128, 129, 250])
def test_finite_square_rejection_conflicts_and_complete_sparse_matches(native, dtype, output, n):
    rng = np.random.default_rng(8190+n)
    for limit in (-.25, 0., .5):
        costs = (rng.random((6,n,n)) + limit + .25).astype(dtype)
        # Sparse complete matching, no edges, a Hall conflict despite every
        # vertex having affordable edges, dense acceptance, partial rejection,
        # and costs on either side of the rounded rejection boundary.
        costs[0, np.arange(n), rng.permutation(n)] = limit-.25
        costs[1] = np.inf
        costs[2, :3*n//4, :n//4] = limit-.25
        costs[2, 3*n//4:, n//4:] = limit-.25
        costs[3] = limit-rng.random((n,n))
        costs[4, :3*n//4, :3*n//4] = limit-rng.random((3*n//4,3*n//4))
        costs[5] = dtype(limit)
        costs[5, np.arange(n), rng.permutation(n)] = np.nextafter(dtype(limit), dtype(-np.inf))
        original = costs.copy()
        costs.setflags(write=False)
        singles = [native.lapjvr(a, cost_limit=limit, output=output) for a in costs]
        for index, (a, result) in enumerate(zip(costs, singles)):
            pairs = as_pairs(result[1] if output == 'pairs' else result[1:], output)
            if index in (0,5):
                assert len(pairs) == n  # Unique beneficial permutation, even one ULP below the limit.
            assert objective(a,pairs,limit, working_dtype=working_dtype_for(a)) == pytest.approx(reference(a,limit, working_dtype=working_dtype_for(a)),rel=2e-6,abs=2e-6)
            assert result[0] == selected_total(a, pairs)
            assert len(np.unique(pairs[:,1])) == len(pairs)
            assert np.all(pairs[1:,0] > pairs[:-1,0])
        for threads in (0, 1, 2, 8):
            result = native.lapjvr_batch(costs,cost_limit=limit,output=output,n_threads=threads)
            np.testing.assert_array_equal(result[0],[s[0] for s in singles])
            for i,single in enumerate(singles):
                for group,wanted in zip(result[1:],single[1:]):
                    np.testing.assert_array_equal(group[i],wanted)
        np.testing.assert_array_equal(costs,original)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
def test_optional_scratch_reuse_after_rejection_and_size_changes(native, dtype, output):
    rng = np.random.default_rng(20261018)
    # Grow and shrink the workspace, alternating paths that need a matching
    # with complete rejection. Old scratch columns must never enter a solve.
    for shape in [(71, 75), (17, 19), (50, 50), (31, 33), (129, 129), (50, 50)]:
        for limit in (-.5, .5):
            costs = rng.normal(limit - .25, 1, shape).astype(dtype)
            rejected = np.full(shape, np.inf, dtype=dtype)
            late = costs.copy()
            late[:shape[0] // 2] = np.inf
            tied_prefix = late.copy()
            tied_prefix[:shape[0] // 2] = limit
            inputs = np.stack([costs, rejected, late, tied_prefix, costs])
            singles = [native.lapjvr(a, cost_limit=limit, output=output) for a in inputs]
            for a, result in zip(inputs, singles):
                pairs = as_pairs(result[1] if output == 'pairs' else result[1:], output)
                assert objective(a, pairs, limit, working_dtype=working_dtype_for(a)) == pytest.approx(reference(a, limit, working_dtype=working_dtype_for(a)),
                                                                 rel=2e-6, abs=2e-6)
                assert result[0] == selected_total(a, pairs)
            for threads in (0, 1, 2):
                result = native.lapjvr_batch(inputs, cost_limit=limit, output=output,
                                             n_threads=threads)
                np.testing.assert_array_equal(result[0], [single[0] for single in singles])
                for i, single in enumerate(singles):
                    for group, expected in zip(result[1:], single[1:]):
                        np.testing.assert_array_equal(group[i], expected)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('n', [33, 64, 129])
def test_dense_optional_conflicts_permuted_and_misleading_samples(native, dtype, output, n):
    from lapjvr_cases import conflict_cases
    for name, a, batch, limit in conflict_cases(918721, np.dtype(dtype).name, [n]):
        if batch:
            continue
        inputs = [a, a.T.copy()]
        if 'constant' in name and n >= 64:
            # The fixed sample can suggest congestion even though the full
            # matrix has a cheap complete matching. A hint must never prune.
            misleading = np.full((n,n), .125, dtype=dtype)
            positions = np.arange(32)*(n-1)//31
            misleading[np.ix_(positions,positions)] = .75
            inputs.append(misleading)
            complete = np.full((n,n), .75, dtype=dtype)
            complete[:3*n//4,:n//4] = .125
            complete[3*n//4:,n//4:] = .125
            complete[np.arange(n),np.arange(n)[::-1]] = 0
            inputs.append(complete)
        costs = np.stack(inputs)
        original = costs.copy()
        costs.setflags(write=False)
        singles = [native.lapjvr(a,cost_limit=limit,output=output) for a in costs]
        for a, single in zip(costs,singles):
            selected = as_pairs(single[1] if output == 'pairs' else single[1:],output)
            assert objective(a,selected,limit, working_dtype=working_dtype_for(a)) == pytest.approx(
                reference(a,limit, working_dtype=working_dtype_for(a)), rel=2e-6 if dtype == np.float32 else 1e-11, abs=2e-6)
            assert single[0] == selected_total(a, selected)
            assert len(np.unique(selected[:,1])) == len(selected)
            assert np.all(selected[1:,0] > selected[:-1,0])
        for threads in (0,1,2,8):
            actual = native.lapjvr_batch(costs,cost_limit=limit,output=output,n_threads=threads)
            np.testing.assert_array_equal(actual[0],[single[0] for single in singles])
            for i,single in enumerate(singles):
                for group,wanted in zip(actual[1:],single[1:]):
                    np.testing.assert_array_equal(group[i],wanted)
        np.testing.assert_array_equal(costs,original)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('n', [64, 129])
def test_dense_optional_conflicts_with_large_affine_offsets(native, dtype, output, n):
    rng = np.random.default_rng(87101+n)
    magnitude = 2**18 if dtype == np.float32 else 2**40
    centered = np.ones((n,n))
    centered[:3*n//4,:n//4] = rng.integers(0,4,(3*n//4,n//4))/16
    centered[3*n//4:,n//4:] = rng.integers(0,4,(n-3*n//4,n-n//4))/16
    for offset in (-magnitude,magnitude):
        cost = (offset+centered).astype(dtype)
        limit = offset+.5
        actual_center = cost.astype(np.float64)-offset
        # Center the reference before solving, so a huge constant cannot hide
        # a wrong optional objective behind a large relative tolerance.
        # These offsets and half-penalties are exactly represented in both
        # dtypes. The centered float64 reference avoids quantizing them again.
        expected = reference(actual_center,.5, working_dtype=working_dtype_for(actual_center))
        single = native.lapjvr(cost,cost_limit=limit,output=output)
        selected = as_pairs(single[1] if output == 'pairs' else single[1:],output)
        assert objective(actual_center,selected,.5, working_dtype=working_dtype_for(actual_center)) == expected
        assert single[0] == selected_total(cost, selected)
        for threads in (0,1,8):
            result = native.lapjvr_batch(np.stack([cost]*3),cost_limit=limit,
                                         output=output,n_threads=threads)
            np.testing.assert_array_equal(result[0],[single[0]]*3)
            for i in range(3):
                for group,wanted in zip(result[1:],single[1:]):
                    np.testing.assert_array_equal(group[i],wanted)


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('n', [17, 33, 50, 129])
@pytest.mark.parametrize('limit', [-.5, .5])
def test_optional_sparse_rows_and_misleading_endpoints(native, dtype, output, n, limit):
    rng = np.random.default_rng(20261018 + n)
    empty = np.full((n, n), np.inf, dtype=dtype)
    single = empty.copy()
    single[-1, n // 2] = limit - .25
    sparse = empty.copy()
    sparse[np.arange(n), rng.permutation(n)] = limit - .25
    misleading = rng.normal(limit, 1, (n, n)).astype(dtype)
    misleading[:, [0, -1]] = limit + .5
    rejected = np.full((n, n), limit + .5, dtype=dtype)
    inputs = np.stack([empty, single, sparse, misleading, rejected])
    inputs.setflags(write=False)
    singles = [native.lapjvr(a, cost_limit=limit, output=output) for a in inputs]
    for a, result in zip(inputs, singles):
        pairs = as_pairs(result[1] if output == 'pairs' else result[1:], output)
        assert objective(a, pairs, limit, working_dtype=working_dtype_for(a)) == pytest.approx(reference(a, limit, working_dtype=working_dtype_for(a)),
                                                         rel=2e-6, abs=2e-6)
        assert result[0] == selected_total(a, pairs)
    for threads in (0, 1, 2):
        actual = native.lapjvr_batch(inputs, cost_limit=limit, output=output,
                                     n_threads=threads)
        np.testing.assert_array_equal(actual[0], [single[0] for single in singles])
        for i, single in enumerate(singles):
            for group, expected in zip(actual[1:], single[1:]):
                np.testing.assert_array_equal(group[i], expected)
