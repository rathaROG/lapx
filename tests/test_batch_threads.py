"""Check the same thread-count rules for every public batch solver."""

import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

import lap
from test_utils import sparse_from_masked


BATCH_SOLVERS = [lap.lapjvx_batch, lap.lapjvxa_batch,
                 lap.lapjvs_batch, lap.lapjvsa_batch, lap.lapmod_batch]


def make_batch(solver, batch_size=3):
    costs = np.array([[[1., 4.], [3., 2.]],
                      [[5., 1.], [2., 4.]],
                      [[2., 7.], [8., 3.]]])[:batch_size]
    if solver is lap.lapmod_batch:
        return [sparse_from_masked(cost) for cost in costs]
    return costs


def assert_same_result(actual, expected):
    if isinstance(expected, (tuple, list)):
        assert type(actual) is type(expected)
        assert len(actual) == len(expected)
        for item, expected_item in zip(actual, expected):
            assert_same_result(item, expected_item)
    else:
        np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('n_threads,cpu_count,workers', [
    (None, 8, [3]), (0, 8, [3]), (0, 2, [2]),
    (None, None, []), (0, None, []), (0, 0, []), (0, 1, []),
    (-2, 8, []), (1, 8, []), (2, 8, [2]), (8, 8, [3]),
    (np.int64(0), 8, [3]), (np.int64(2), 8, [2]),
])
def test_worker_count_and_results(monkeypatch, solver, return_cost,
                                  n_threads, cpu_count, workers):
    batch = make_batch(solver)
    expected = solver(batch, n_threads=1, return_cost=return_cost)
    created = []

    def get_cpu_count():
        assert n_threads is None or n_threads == 0
        return cpu_count

    def make_pool(max_workers):
        created.append(max_workers)
        return ThreadPoolExecutor(max_workers=max_workers)

    monkeypatch.setattr(os, 'cpu_count', get_cpu_count)
    monkeypatch.setattr(sys.modules[solver.__module__], 'ThreadPoolExecutor', make_pool)
    result = solver(batch, n_threads=n_threads, return_cost=return_cost)
    assert created == workers
    assert_same_result(result, expected)


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('batch_size', [0, 1])
@pytest.mark.parametrize('n_threads', [None, 0, 1, 8])
def test_small_batches_skip_pool(monkeypatch, solver, return_cost, batch_size,
                                 n_threads):
    batch = make_batch(solver, batch_size)
    expected = solver(batch, n_threads=1, return_cost=return_cost)

    def unexpected_pool(*args, **kwargs):
        pytest.fail('An empty or singleton batch created a thread pool')

    monkeypatch.setattr(sys.modules[solver.__module__], 'ThreadPoolExecutor', unexpected_pool)
    result = solver(batch, n_threads=n_threads, return_cost=return_cost)
    assert_same_result(result, expected)


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('return_cost', [False, True])
@pytest.mark.parametrize('batch_size', [0, 1, 3])
@pytest.mark.parametrize('n_threads,error', [
    ('', ValueError), (b'', ValueError), ([], TypeError),
    ((), TypeError), ({}, TypeError), ('two', ValueError),
])
def test_invalid_thread_counts_raise_before_work(monkeypatch, solver, return_cost,
                                                 batch_size, n_threads, error):
    batch = make_batch(solver, batch_size)

    def unexpected_work(*args, **kwargs):
        pytest.fail('Invalid n_threads triggered CPU detection, a pool, or a solve')

    module = sys.modules[solver.__module__]
    monkeypatch.setattr(os, 'cpu_count', unexpected_work)
    monkeypatch.setattr(module, 'ThreadPoolExecutor', unexpected_work)
    single_name = '_' + solver.__name__.replace('_batch', '_single')
    monkeypatch.setattr(module, single_name, unexpected_work)
    with pytest.raises(error):
        solver(batch, n_threads=n_threads, return_cost=return_cost)
