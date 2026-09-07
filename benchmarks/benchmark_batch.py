"""Compare dense batches and equivalent dense/CSR views of sparse problems."""

import argparse
from functools import partial
import os
import time

import lap
import numpy as np
from scipy.optimize import linear_sum_assignment


def do_lapx_loop(cost_matrix_batch, extend_cost=False, backend='lapjvx', return_cost=False):
    if backend == 'lapjvs':
        solver = lap.lapjvs
    elif backend == 'lapjvx':
        solver = lap.lapjvx
    else:
        raise ValueError(f'Unknown backend: {backend}')
    totals = np.empty(len(cost_matrix_batch), dtype=np.float64) if return_cost else None
    assignments = []
    for i, cost_matrix in enumerate(cost_matrix_batch):
        if totals is not None:
            cost, row_indices, col_indices = solver(
                cost_matrix, extend_cost=extend_cost, return_cost=True)
            totals[i] = cost
        else:
            row_indices, col_indices = solver(
                cost_matrix, extend_cost=extend_cost, return_cost=False)
        assignments.append(np.stack([row_indices, col_indices], axis=1))
    return (totals, assignments) if totals is not None else assignments


def do_scipy_loop(cost_matrix_batch, return_cost=False):
    """Solve sequentially; include NumPy cost sums only when requested."""
    totals = np.empty(len(cost_matrix_batch), dtype=np.float64) if return_cost else None
    assignments = []
    for i, cost_matrix in enumerate(cost_matrix_batch):
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        if totals is not None:
            totals[i] = cost_matrix[row_indices, col_indices].sum(dtype=np.float64)
        assignments.append(np.stack([row_indices, col_indices], axis=1))
    return (totals, assignments) if totals is not None else assignments


def do_lapmod_loop(problems, return_cost=False):
    totals = np.empty(len(problems), dtype=np.float64) if return_cost else None
    x_list, y_list = [], []
    for i, problem in enumerate(problems):
        if totals is not None:
            total, x, y = lap.lapmod(*problem, fast=True, return_cost=True)
            totals[i] = total
        else:
            x, y = lap.lapmod(*problem, fast=True, return_cost=False)
        x_list.append(x)
        y_list.append(y)
    return (totals, x_list, y_list) if totals is not None else (x_list, y_list)


def sparse_problems_from_dense(cost_matrix_batch):
    """Store finite entries, including zero costs, in lapmod's row-major format."""
    batch = np.asarray(cost_matrix_batch)
    if batch.ndim != 3 or batch.shape[1] != batch.shape[2]:
        raise ValueError('lapmod requires a batch of square matrices')
    n = batch.shape[1]
    problems = []
    for cost in batch:
        present = np.isfinite(cost)
        cc = np.ascontiguousarray(cost[present], dtype=np.float64)
        ii = np.empty(n + 1, dtype=np.uint32)
        ii[0] = 0
        np.cumsum(present.sum(axis=1), dtype=np.uint32, out=ii[1:])
        kk = np.nonzero(present)[1].astype(np.uint32)
        problems.append((n, cc, ii, kk))
    return problems


def make_sparse_costs(batch_size, n, density, seed):
    """Generate non-negative costs with a feasible diagonal in every problem."""
    rng = np.random.default_rng(seed)
    costs = rng.random((batch_size, n, n))
    for cost in costs:
        present = rng.random((n, n)) < density
        np.fill_diagonal(present, True)
        cost[~present] = np.inf
    return costs


def checked_assignment_costs(batch_costs, assignments, assignment_format):
    """Validate each solver's output and calculate costs outside solve timing."""
    batch_size, n, m = batch_costs.shape
    size = min(n, m)
    if assignment_format == 'pairs':
        assert len(assignments) == batch_size
        for pairs in assignments:
            assert pairs.shape == (size, 2)
        indices = ((pairs[:, 0], pairs[:, 1]) for pairs in assignments)
    elif assignment_format in ('indices', 'mapping'):
        first, second = assignments
        assert len(first) == len(second) == batch_size
        indices = zip(first, second)
    else:
        raise ValueError(f'Unknown assignment format: {assignment_format}')

    totals = np.empty(batch_size, dtype=np.float64)
    for i, (cost, (rows, cols)) in enumerate(zip(batch_costs, indices)):
        if assignment_format == 'mapping':
            x, y = rows, cols
            assert n == m and x.shape == y.shape == (n,)
            rows, cols = np.arange(n), x
            np.testing.assert_array_equal(np.sort(x), rows)
            np.testing.assert_array_equal(y[x], rows)
        assert rows.shape == cols.shape == (size,)
        assert np.all((rows >= 0) & (rows < n))
        assert np.all((cols >= 0) & (cols < m))
        assert np.unique(rows).size == np.unique(cols).size == size
        selected_costs = cost[rows, cols]
        assert np.isfinite(selected_costs).all()
        totals[i] = selected_costs.sum(dtype=np.float64)
    return totals


def measure(label, solve, warmup, batch_costs, return_cost=False,
            assignment_format='indices', expected=None):
    """Time one solve, then validate results; print costs only when requested."""
    warmup()
    start = time.perf_counter()
    result = solve()
    elapsed = time.perf_counter() - start
    if return_cost:
        reported_totals = np.asarray(result[0], dtype=np.float64)
        assignments = result[1] if assignment_format == 'pairs' else result[1:]
        cost_text = f'cost={reported_totals.sum():.8f}, '
    else:
        reported_totals = None
        assignments = result
        cost_text = ''
    totals = checked_assignment_costs(batch_costs, assignments, assignment_format)
    if reported_totals is not None:
        np.testing.assert_allclose(
            reported_totals, totals, rtol=1e-6, atol=1e-8,
            err_msg=f'{label}: returned costs differ from assignment costs')
    if expected is not None:
        np.testing.assert_allclose(
            totals, expected, rtol=1e-6, atol=1e-8,
            err_msg=f'{label}: per-problem costs differ')
    print(f'  CPU {label:<22}:  {cost_text}time={elapsed:.8f}s')
    return totals


def benchmark_solvers(batch_costs, n_threads, problems=None, return_cost=False):
    """Time solver calls after warm-up; compare costs outside the timed region."""
    _, n, m = batch_costs.shape
    extend_cost = n != m
    # Sparse cases retain a feasible diagonal when taking these square views.
    warmup_costs = batch_costs[:2, :min(n, 128), :min(m, 128)]
    measure_case = partial(measure, batch_costs=batch_costs, return_cost=return_cost)
    expected = None
    for label, solver, assignment_format in (
        ('lapx-batch-jvx', lap.lapjvx_batch, 'indices'),
        ('lapx-batch-jvs', lap.lapjvs_batch, 'indices'),
        ('lapx-batch-jvxa', lap.lapjvxa_batch, 'pairs'),
        ('lapx-batch-jvsa', lap.lapjvsa_batch, 'pairs'),
        ('lapx-batch-jvsa64', partial(lap.lapjvsa_batch, prefer_float32=False), 'pairs'),
    ):
        totals = measure_case(
            label,
            lambda: solver(batch_costs, return_cost=return_cost,
                           extend_cost=extend_cost, n_threads=n_threads),
            lambda: solver(warmup_costs, return_cost=return_cost,
                           extend_cost=extend_cost, n_threads=n_threads),
            assignment_format=assignment_format, expected=expected)
        if expected is None:
            expected = totals

    for backend in ('lapjvx', 'lapjvs'):
        measure_case(
            f'lapx-loop-{backend[3:]}',
            lambda: do_lapx_loop(batch_costs, extend_cost=extend_cost, backend=backend,
                                return_cost=return_cost),
            lambda: do_lapx_loop(warmup_costs, extend_cost=extend_cost, backend=backend,
                                return_cost=return_cost),
            assignment_format='pairs', expected=expected)

    measure_case('scipy-loop',
                 lambda: do_scipy_loop(batch_costs, return_cost=return_cost),
                 lambda: do_scipy_loop(warmup_costs, return_cost=return_cost),
                 assignment_format='pairs', expected=expected)

    if problems is not None:
        warmup_problems = sparse_problems_from_dense(warmup_costs)
        measure_case('lapx-loop-mod',
                     lambda: do_lapmod_loop(problems, return_cost=return_cost),
                     lambda: do_lapmod_loop(warmup_problems, return_cost=return_cost),
                     assignment_format='mapping', expected=expected)
        measure_case('lapx-batch-mod-1t',
                     lambda: lap.lapmod_batch(problems, return_cost=return_cost, n_threads=1),
                     lambda: lap.lapmod_batch(warmup_problems, return_cost=return_cost, n_threads=1),
                     assignment_format='mapping', expected=expected)
        if n_threads > 1:
            measure_case('lapx-batch-mod',
                         lambda: lap.lapmod_batch(problems, return_cost=return_cost, n_threads=n_threads),
                         lambda: lap.lapmod_batch(warmup_problems, return_cost=return_cost, n_threads=n_threads),
                         assignment_format='mapping', expected=expected)


def benchmark_dense_cases(cases, n_threads, return_cost=False):
    for i, (batch_size, n, m) in enumerate(cases):
        print(f'\n# Dense {batch_size} x ({n}x{m}) | n_threads = {n_threads}'
              f' | return_cost = {return_cost}\n')
        batch_costs = np.random.default_rng(2026 + i).random((batch_size, n, m))
        benchmark_solvers(batch_costs, n_threads, return_cost=return_cost)
        del batch_costs


def benchmark_sparse_cases(cases, n_threads, return_cost=False):
    for i, (batch_size, n, density) in enumerate(cases):
        batch_costs = make_sparse_costs(batch_size, n, density, seed=2026 + i)
        start = time.perf_counter()
        problems = sparse_problems_from_dense(batch_costs)
        conversion_time = time.perf_counter() - start
        entries = sum(problem[1].size for problem in problems)
        actual_density = entries / (batch_size * n * n)
        print(f'\n# Sparse {batch_size} x ({n}x{n}) | density = {actual_density:.2%}'
              f' | n_threads = {n_threads} | return_cost = {return_cost}\n')
        print('  Same problems: dense solvers use inf for missing edges; lapmod uses CSR.')
        print(f'  Dense-to-CSR preparation  :  {conversion_time:.8f}s (excluded from solve times)\n')
        benchmark_solvers(batch_costs, n_threads, problems=problems, return_cost=return_cost)
        del batch_costs, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true',
                        help='Use small batches to check the benchmark quickly.')
    parser.add_argument('--sparse-only', action='store_true',
                        help='Run only the sparse square comparisons.')
    parser.add_argument('--cost', action='store_true',
                        help='Include total-cost calculation and print costs (default: assignments only).')
    parser.add_argument('--threads', type=int, default=0,
                        help='Worker threads; 0 uses the CPU count (default: 0).')
    args = parser.parse_args()
    n_threads = max(1, args.threads or os.cpu_count() or 1)

    dense_cases = [(10, 4000, 4000), (20, 3000, 2000), (50, 2000, 2000),
                   (100, 1000, 2000), (500, 1000, 1000)]
    sparse_cases = [(100, 1000, .01), (50, 2000, .05)]
    if args.quick:
        dense_cases = [(4, 32, 32), (4, 24, 32)]
        sparse_cases = [(4, 32, .1)]
    if not args.sparse_only:
        benchmark_dense_cases(dense_cases, n_threads, return_cost=args.cost)
    if hasattr(lap, 'lapmod_batch'):
        benchmark_sparse_cases(sparse_cases, n_threads, return_cost=args.cost)
    else:
        print('\n# Sparse batch comparison skipped: the installed lapx has no lapmod_batch.')
        print('  Use a build containing lapmod_batch to include the sparse benchmarks.')


if __name__ == '__main__':
    main()
