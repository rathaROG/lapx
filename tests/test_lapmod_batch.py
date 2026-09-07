"""Sparse batches with varying sizes, ordered outputs, and worker failures."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import numpy as np
import pytest

import lap
from lap import _lapmod_batch_wp, _lapmod_wp
from test_utils import sparse_from_masked


@pytest.fixture
def problems():
    return [sparse_from_masked(np.asarray(cost, dtype=np.float64)) for cost in (
        [[1, 4], [3, 2]],
        [[5, np.inf, 3], [np.inf, 2, 2], [1, 5, np.inf]],
        [[1, 2, 1, np.inf], [np.inf, 3, 1, 4],
         [np.inf, 4, 3, 3], [0, np.inf, 2, 0]],
    )]


@pytest.mark.parametrize('fast,fp_version', [
    (False, lap.FP_DYNAMIC), (True, lap.FP_1),
    (True, lap.FP_2), (True, lap.FP_DYNAMIC),
])
@pytest.mark.parametrize('n_threads', [1, 2])
@pytest.mark.parametrize('return_cost', [False, True])
def test_variable_sparse_batches_match_single(problems, fast, fp_version,
                                             n_threads, return_cost):
    expected = [lap.lapmod(*problem, fast=fast, fp_version=fp_version)
                for problem in problems]
    if return_cost:
        totals, x_list, y_list = lap.lapmod_batch(
            problems, fast=fast, fp_version=fp_version, n_threads=n_threads)
        assert totals.dtype == np.float64
        np.testing.assert_array_equal(totals, [result[0] for result in expected])
    else:
        x_list, y_list = lap.lapmod_batch(
            problems, fast=fast, return_cost=False,
            fp_version=fp_version, n_threads=n_threads)
    assert len(x_list) == len(y_list) == len(problems)
    for (n, _, _, _), (_, expected_x, expected_y), x, y in zip(
            problems, expected, x_list, y_list):
        assert x.shape == y.shape == (n,)
        assert x.dtype == y.dtype == np.int32
        np.testing.assert_array_equal(x, expected_x)
        np.testing.assert_array_equal(y, expected_y)


@pytest.mark.parametrize('batch_size', [0, 1])
@pytest.mark.parametrize('n_threads', [None, 0, 1, 8])
@pytest.mark.parametrize('return_cost', [False, True])
def test_empty_and_singleton_batches_skip_pool(monkeypatch, problems, batch_size,
                                              n_threads, return_cost):
    def unexpected_pool(*args, **kwargs):
        pytest.fail('An empty or singleton batch created a thread pool')

    monkeypatch.setattr(_lapmod_batch_wp, 'ThreadPoolExecutor', unexpected_pool)
    batch = tuple(problems[:batch_size])
    if return_cost:
        totals, x_list, y_list = lap.lapmod_batch(batch, n_threads=n_threads)
        assert totals.shape == (batch_size,)
        assert totals.dtype == np.float64
        np.testing.assert_array_equal(totals, [3.] * batch_size)
    else:
        x_list, y_list = lap.lapmod_batch(
            batch, n_threads=n_threads, return_cost=False)
    assert len(x_list) == len(y_list) == batch_size
    for x, y in zip(x_list, y_list):
        np.testing.assert_array_equal(x, [0, 1])
        np.testing.assert_array_equal(y, [0, 1])


@pytest.mark.parametrize('n_threads,cpu_count,workers', [
    (None, 8, [3]), (0, 8, [3]), (2, 8, [2]),
    (None, None, []), (-2, 8, []),
])
def test_worker_count_defaults_and_batch_cap(monkeypatch, problems, n_threads,
                                            cpu_count, workers):
    created = []

    def make_pool(max_workers):
        created.append(max_workers)
        return ThreadPoolExecutor(max_workers=max_workers)

    monkeypatch.setattr(_lapmod_batch_wp.os, 'cpu_count', lambda: cpu_count)
    monkeypatch.setattr(_lapmod_batch_wp, 'ThreadPoolExecutor', make_pool)
    lap.lapmod_batch(problems, n_threads=n_threads)
    assert created == workers


@pytest.mark.parametrize('return_cost', [False, True])
def test_shared_readonly_strided_inputs(return_cost):
    cc = np.array([100000., 99., .001, 99., .001, 99.], dtype=np.float32)[::2]
    ii = np.array([0, 99, 1, 99, 2, 99, 3, 99], dtype=np.uint64)[::2]
    kk = np.array([2, 99, 0, 99, 1, 99], dtype=np.int64)[::2]
    arrays = (cc, ii, kk)
    originals = [array.copy() for array in arrays]
    for array in arrays:
        array.setflags(write=False)
    batch = [(np.int64(3), cc, ii, kk)] * 4
    if return_cost:
        totals, x_list, y_list = lap.lapmod_batch(batch, n_threads=2)
        np.testing.assert_array_equal(totals, [cc.sum(dtype=np.float64)] * 4)
    else:
        x_list, y_list = lap.lapmod_batch(batch, n_threads=2, return_cost=False)
    for x, y in zip(x_list, y_list):
        np.testing.assert_array_equal(x, [2, 0, 1])
        np.testing.assert_array_equal(y, [1, 2, 0])
    x_list[0][:] = -1
    y_list[0][:] = -1
    for x, y in zip(x_list[1:], y_list[1:]):
        np.testing.assert_array_equal(x, [2, 0, 1])
        np.testing.assert_array_equal(y, [1, 2, 0])
    for array, original in zip(arrays, originals):
        assert not array.flags.writeable
        np.testing.assert_array_equal(array, original)


@pytest.mark.parametrize('n_threads', [1, 2])
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('failure,error', [
    ('costs', ValueError), ('size', TypeError),
    ('tuple', ValueError), ('path', ValueError),
])
def test_problem_errors_propagate_and_next_batch_succeeds(problems, n_threads,
                                                         return_cost, failure, error):
    bad = list(problems)
    n, cc, ii, kk = bad[1]
    if failure == 'costs':
        bad[1] = (n, -cc, ii, kk)
    elif failure == 'size':
        bad[1] = (2.5, cc, ii, kk)
    elif failure == 'tuple':
        bad[1] = (n, cc, ii)
    fp_version = 0 if failure == 'path' else lap.FP_DYNAMIC
    with pytest.raises(error):
        lap.lapmod_batch(bad, return_cost=return_cost, n_threads=n_threads,
                         fp_version=fp_version)
    totals, x_list, y_list = lap.lapmod_batch(problems, n_threads=n_threads)
    for problem, total, x, y in zip(problems, totals, x_list, y_list):
        expected_total, expected_x, expected_y = lap.lapmod(*problem)
        assert total == expected_total
        np.testing.assert_array_equal(x, expected_x)
        np.testing.assert_array_equal(y, expected_y)


def test_results_preserve_order_when_later_problem_finishes_first(monkeypatch, problems):
    first_started = Event()
    second_finished = Event()
    finished = []
    single = _lapmod_batch_wp._lapmod_single

    def controlled_single(n, cc, ii, kk, **options):
        if n == 2:
            first_started.set()
            assert second_finished.wait(5), 'The second worker did not finish'
        else:
            assert first_started.wait(5), 'The first worker did not start'
        result = single(n, cc, ii, kk, **options)
        finished.append(n)
        if n == 3:
            second_finished.set()
        return result

    monkeypatch.setattr(_lapmod_batch_wp, '_lapmod_single', controlled_single)
    totals, x_list, y_list = lap.lapmod_batch(problems[:2], n_threads=2)
    assert finished == [3, 2]
    for problem, total, x, y in zip(problems, totals, x_list, y_list):
        expected_total, expected_x, expected_y = lap.lapmod(*problem)
        assert total == expected_total
        np.testing.assert_array_equal(x, expected_x)
        np.testing.assert_array_equal(y, expected_y)


@pytest.mark.parametrize('fast', [False, True])
@pytest.mark.parametrize('n_threads', [1, 2])
def test_return_cost_false_skips_total_calculation(monkeypatch, problems, fast, n_threads):
    def unexpected_cost(*args, **kwargs):
        pytest.fail('return_cost=False calculated a total')

    monkeypatch.setattr(_lapmod_wp, 'get_cost', unexpected_cost)
    x_list, y_list = lap.lapmod_batch(
        problems, fast=fast, return_cost=False, n_threads=n_threads)
    assert len(x_list) == len(y_list) == len(problems)


def test_public_export_and_positional_options(problems):
    assert 'lapmod_batch' in lap.__all__
    assert lap.lapmod_batch is _lapmod_batch_wp.lapmod_batch
    totals, x_list, y_list = lap.lapmod_batch(problems, False, True, lap.FP_DYNAMIC, 1)
    assert totals.shape == (len(problems),)
    assert len(x_list) == len(y_list) == len(problems)
