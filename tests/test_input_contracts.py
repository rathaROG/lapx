"""Check small error cases in the public API, including exceptions from batch workers."""

import numpy as np
import pytest

import lap


SINGLE_SOLVERS = [lap.lapjv, lap.lapjvx, lap.lapjvxa,
                  lap.lapjvc, lap.lapjvs, lap.lapjvsa]
BATCH_SOLVERS = [lap.lapjvx_batch, lap.lapjvxa_batch,
                 lap.lapjvs_batch, lap.lapjvsa_batch]


@pytest.mark.parametrize('solver', SINGLE_SOLVERS)
@pytest.mark.parametrize('shape', [(), (2,), (1, 2, 2)])
def test_single_solvers_reject_wrong_dimensions(solver, shape):
    # The classic pybind11 solver reports RuntimeError; the others use ValueError.
    error = RuntimeError if solver is lap.lapjvc else ValueError
    with pytest.raises(error, match='dimension|2D'):
        solver(np.zeros(shape))


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('shape', [(), (2, 2), (1, 2, 2, 2)])
def test_batch_solvers_reject_wrong_dimensions(solver, shape):
    with pytest.raises(ValueError, match='3-dimensional'):
        solver(np.zeros(shape))


@pytest.mark.parametrize('solver', BATCH_SOLVERS)
@pytest.mark.parametrize('n_threads', [1, 2])
def test_batch_worker_errors_propagate_and_next_call_succeeds(solver, n_threads):
    good = np.array([[[0., 4.], [4., 1.]], [[4., 2.], [0., 4.]]])
    if solver in (lap.lapjvx_batch, lap.lapjvxa_batch):
        bad, options = good, {'cost_limit': np.nan}
    else:
        bad = good.copy()
        bad[1, :, 1] = np.inf  # No full assignment exists in the second matrix.
        options = {}
    for return_cost in (False, True):
        with pytest.raises(ValueError):
            solver(bad, n_threads=n_threads, return_cost=return_cost, **options)
        result = solver(good, n_threads=n_threads, return_cost=True)
        np.testing.assert_array_equal(result[0], [1., 2.])
        if solver in (lap.lapjvxa_batch, lap.lapjvsa_batch):
            assignments = result[1]
        else:
            assignments = [np.column_stack(pair) for pair in zip(*result[1:])]
        assert len(assignments) == 2
        np.testing.assert_array_equal(assignments[0], [[0, 0], [1, 1]])
        np.testing.assert_array_equal(assignments[1], [[0, 1], [1, 0]])


def test_sparse_entry_limit_checked_without_allocating_large_arrays():
    entries = 2**31
    cc = np.broadcast_to(np.array(0.), (entries,))
    kk = np.broadcast_to(np.array(0, dtype=np.int32), (entries,))
    with pytest.raises(ValueError, match='too many entries'):
        lap.lapmod(1, cc, np.array([0, entries], dtype=np.int64), kk)
