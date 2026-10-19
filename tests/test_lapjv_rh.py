# Copyright (c) 2026 Ratha SIV | MIT License
"""Package coexistence, family identity, and mixed-family worker reuse."""

from concurrent.futures import ThreadPoolExecutor
import importlib
import inspect

import lap
import numpy as np
import pytest

pytest.importorskip('lap._lapjv_rh')


def test_public_exports_and_identical_signatures():
    for suffix in ('', '_batch'):
        rust = getattr(lap, 'lapjvr' + suffix)
        hybrid = getattr(lap, 'lapjvh' + suffix)
        assert rust is not hybrid
        assert inspect.signature(rust) == inspect.signature(hybrid)
        for function in (rust, hybrid):
            assert function.__name__ in lap.__all__
            assert function.__name__ in dir(lap)
            assert function is getattr(importlib.import_module(function.__module__), function.__name__)
            assert function.__doc__


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
@pytest.mark.parametrize('output', ['indices', 'pairs'])
@pytest.mark.parametrize('return_cost', [False, True])
def test_alternating_and_concurrent_families(dtype, output, return_cost):
    rng = np.random.default_rng(20261019)
    # Repeated rows force completion; changing shapes also exercises scratch reuse.
    square = rng.random((6, 96, 96)).astype(dtype)
    square[:, :70] = square[:, :1]
    cases = [(square, np.inf), (rng.random((5, 33, 27)).astype(dtype), np.inf),
             (rng.random((4, 31, 31)).astype(dtype), .15)]
    options = dict(extend_cost=True, return_cost=return_cost, output=output)

    def same(actual, expected):
        if isinstance(expected, (tuple, list)):
            assert type(actual) is type(expected) and len(actual) == len(expected)
            for a, e in zip(actual, expected):
                same(a, e)
        else:
            np.testing.assert_array_equal(actual, expected)

    expected = []
    for costs, limit in cases:
        costs.setflags(write=False)
        expected.append(lap.lapjvr_batch(costs, cost_limit=limit, n_threads=1, **options))

    def run(task):
        family, case, threads = task
        costs, limit = cases[case]
        actual = family(costs, cost_limit=limit, n_threads=threads, **options)
        same(actual, expected[case])

    tasks = [(family, case, threads) for threads in (1, 0, 2, 3)
             for case in range(len(cases)) for family in (lap.lapjvr_batch, lap.lapjvh_batch)]
    for task in tasks:
        run(task)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, reversed(tasks)))

    bad = np.zeros((4, 8, 8), dtype=dtype)
    bad[2] = np.inf
    for family in (lap.lapjvh_batch, lap.lapjvr_batch):
        with pytest.raises(ValueError, match='batch index 2'):
            family(bad, n_threads=2)
    run(tasks[0])
