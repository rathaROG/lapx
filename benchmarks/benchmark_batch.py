"""Compare dense and sparse batch assignment timings.

R/H use direct pairs and precision='native' on float64 inputs.
Total-cost calculation is optional via --cost. Input preparation, warmup,
and result checks are outside timing.
"""

import argparse
from functools import partial
from io import TextIOWrapper
import sys
import time
from unicodedata import east_asian_width

if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

import lap
import numpy as np
from scipy.optimize import linear_sum_assignment


def do_lapx_loop(cost_matrix_batch, extend_cost=False, backend='lapjvx', return_cost=False):
    if backend not in ('lapjvx', 'lapjvs', 'lapjvr', 'lapjvh'):
        raise ValueError(f'Unknown backend: {backend}')
    solver = getattr(lap, backend)
    direct_pairs = backend in ('lapjvr', 'lapjvh')
    if direct_pairs:
        solver = partial(solver, precision='native', output='pairs')
    totals = np.empty(len(cost_matrix_batch), dtype=np.float64) if return_cost else None
    assignments = []
    for i, cost_matrix in enumerate(cost_matrix_batch):
        result = solver(cost_matrix, extend_cost=extend_cost, return_cost=return_cost)
        if totals is not None:
            totals[i] = result[0]
            result = result[1] if direct_pairs else result[1:]
        assignments.append(result if direct_pairs else np.column_stack(result))
    return (totals, assignments) if totals is not None else assignments


def do_scipy_loop(cost_matrix_batch, return_cost=False):
    """Solve each problem in sequence. Include NumPy cost sums only when requested."""
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
    """Store finite entries in lapmod's row-major format. Include zero costs."""
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
    """Validate assignments and sum their costs outside timing."""
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


def measure(label, solve, batch_costs, return_cost=False,
            assignment_format='indices', expected=None, problems=None):
    """Time one solve, then validate its assignments and optional costs."""
    inputs = problems if assignment_format == 'mapping' else batch_costs
    start = time.perf_counter()
    result = solve(inputs)
    elapsed = time.perf_counter() - start
    if return_cost:
        reported_totals = np.asarray(result[0], dtype=np.float64)
        assignments = result[1] if assignment_format == 'pairs' else result[1:]
    else:
        reported_totals = None
        assignments = result
    totals = checked_assignment_costs(batch_costs, assignments, assignment_format)
    if reported_totals is not None:
        np.testing.assert_allclose(
            reported_totals, totals, rtol=1e-6, atol=1e-8,
            err_msg=f'{label}: returned costs differ from assignment costs')
    if expected is not None:
        np.testing.assert_allclose(
            totals, expected, rtol=1e-6, atol=1e-8,
            err_msg=f'{label}: per-problem costs differ')
    return elapsed, totals.sum() if return_cost else None


def print_ranking(timings, return_cost=False):
    """Print one table sorted by time, using SciPy as the baseline."""
    baseline_time = next(elapsed for label, elapsed, _ in timings if label == 'scipy-loop')
    header = ('Solver', 'Check', 'Time (ms)', 'vs SciPy')
    if return_cost:
        header += ('Cost (last round)',)
    rows = []
    for rank, (label, elapsed, total) in enumerate(sorted(timings, key=lambda row: row[1]), 1):
        if label == 'scipy-loop':
            check, relative = '⭐ BASE', '⭐ baseline'
        elif elapsed <= 0 or baseline_time <= 0:
            check, relative = '✅ PASS', 'n/a'
        elif elapsed == baseline_time:
            check, relative = '✅ PASS', '🤝 same'
        elif elapsed > baseline_time:
            check, relative = '✅ PASS', f'🐌 {elapsed / baseline_time:.2f}x slower'
        else:
            marker = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, '🏆')
            check, relative = '✅ PASS', f'{marker} {baseline_time / elapsed:.2f}x faster'
        row = (label, check, f'{elapsed * 1e3:.6f}', relative)
        if return_cost:
            row += (f'{total:.8f}',)
        rows.append(row)

    def display_width(text):
        return sum(2 if east_asian_width(char) in ('W', 'F') else 1 for char in text)

    widths = [max(display_width(cell) for cell in column) for column in zip(header, *rows)]

    def format_row(row):
        cells = []
        for index, (cell, width) in enumerate(zip(row, widths)):
            padding = ' ' * (width - display_width(cell))
            cells.append(padding + cell if index in (2, 4) else cell + padding)
        return '  '.join(cells).rstrip()

    separator = '-' * (sum(widths) + 2 * (len(widths) - 1))
    print(format_row(header))
    print(separator)
    for row in rows:
        print(format_row(row))
    print(separator)


def benchmark_solvers(batch_shape, n_threads, density=None, return_cost=False,
                      *, seed=2026, repeats=2):
    """Compare median solve times on a fresh shared batch each round."""
    batch_size, n, m = batch_shape
    extend_cost = n != m
    if repeats > 1:
        print(f'* Median of {repeats} shuffled rounds;')
        print(f'input seeds={seed}..{seed + repeats - 1}; warmup each round.\n')
    batch_solvers = [
        ('lapx-batch-jvx', lap.lapjvx_batch, 'indices'),
        ('lapx-batch-jvs', lap.lapjvs_batch, 'indices'),
        ('lapx-batch-jvxa', lap.lapjvxa_batch, 'pairs'),
        ('lapx-batch-jvsa', lap.lapjvsa_batch, 'pairs'),
        ('lapx-batch-jvsa64', partial(lap.lapjvsa_batch, prefer_float32=False), 'pairs'),
    ]
    loop_backends = ['lapjvx', 'lapjvs']
    for backend in ('lapjvr', 'lapjvh'):
        solver = getattr(lap, f'{backend}_batch', None)
        if solver is not None:
            batch_solvers.append((f'lapx-batch-{backend[3:]}',
                                  partial(solver, precision='native', output='pairs'), 'pairs'))
        else:
            print(f'  Skipping {backend}_batch: unavailable in the installed lapx.')
        if hasattr(lap, backend):
            loop_backends.append(backend)
        else:
            print(f'  Skipping {backend} loop: unavailable in the installed lapx.')

    cases = [(label, partial(solver, return_cost=return_cost,
                             extend_cost=extend_cost, n_threads=n_threads), assignment_format)
             for label, solver, assignment_format in batch_solvers]
    for backend in loop_backends:
        cases.append((f'lapx-loop-{backend[3:]}',
                      partial(do_lapx_loop, extend_cost=extend_cost,
                              backend=backend, return_cost=return_cost), 'pairs'))
    cases.append(('scipy-loop', partial(do_scipy_loop, return_cost=return_cost), 'pairs'))
    if density is not None:
        cases.extend([
            ('lapx-loop-mod', partial(do_lapmod_loop, return_cost=return_cost), 'mapping'),
            ('lapx-batch-mod-1t', partial(lap.lapmod_batch, return_cost=return_cost,
                                         n_threads=1), 'mapping'),
        ])
        if n_threads in (None, 0) or n_threads > 1:
            cases.append(('lapx-batch-mod', partial(lap.lapmod_batch,
                          return_cost=return_cost, n_threads=n_threads), 'mapping'))

    order_rng = np.random.default_rng([seed, batch_size, n, m, 1])
    samples = [[] for _ in cases]
    totals = [None] * len(cases)
    for round_index in range(repeats):
        input_seed = [seed + round_index, batch_size, n, m]
        if density is None:
            batch_costs = np.random.default_rng(input_seed).random(batch_shape)
            problems = None
        else:
            batch_costs = make_sparse_costs(batch_size, n, density, seed=input_seed)
            problems = sparse_problems_from_dense(batch_costs)
        for label, solve, assignment_format in cases:
            result = solve(problems if assignment_format == 'mapping' else batch_costs)
            if label == 'scipy-loop':
                assignments = result[1] if return_cost else result
                expected = checked_assignment_costs(batch_costs, assignments, 'pairs')
                del assignments
            del result
        for index in order_rng.permutation(len(cases)):
            label, solve, assignment_format = cases[index]
            elapsed, total = measure(label, solve, batch_costs, return_cost=return_cost,
                                     assignment_format=assignment_format, expected=expected,
                                     problems=problems)
            samples[index].append(elapsed)
            totals[index] = total
        del batch_costs, problems
    timings = [(label, float(np.median(times)), total)
               for (label, _, _), times, total in zip(cases, samples, totals)]
    print_ranking(timings, return_cost=return_cost)


def benchmark_dense_cases(cases, n_threads, return_cost=False, *, seed=2026, repeats=2):
    for batch_size, n, m in cases:
        case_repeats = 1 if max(n, m) >= 3000 else repeats
        print(f'\n### Dense {batch_size} x ({n}x{m}) | n_threads={n_threads}'
              f' | return_cost={return_cost}\n')
        benchmark_solvers((batch_size, n, m), n_threads, return_cost=return_cost,
                          seed=seed, repeats=case_repeats)


def benchmark_sparse_cases(cases, n_threads, return_cost=False, *, seed=2026, repeats=2):
    for batch_size, n, density in cases:
        case_repeats = 1 if n >= 3000 else repeats
        print(f'\n### Sparse {batch_size} x ({n}x{n}) | target density={density:.2%}'
              f' | n_threads={n_threads} | return_cost={return_cost}\n')
        benchmark_solvers((batch_size, n, n), n_threads, density=density, return_cost=return_cost,
                          seed=seed, repeats=case_repeats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true',
                        help='Skip the 4000x4000 dense case.')
    parser.add_argument('--sparse-only', action='store_true',
                        help='Run only the sparse square comparisons.')
    parser.add_argument('--cost', action='store_true',
                        help='Include total-cost calculation and print costs (default: assignments only).')
    parser.add_argument('--threads', type=int, default=0,
                        help="Worker threads; 0 uses each solver's automatic policy (default: 0).")
    parser.add_argument('--seed', type=int, default=2026,
                        help='Base seed; each round uses seed + round index (default: 2026).')
    parser.add_argument('--repeats', type=int, default=2,
                        help='Timed rounds (default: 2); dimensions >=3000 run once.')
    args = parser.parse_args()
    if args.repeats < 1 or args.seed < 0:
        parser.error('--repeats must be positive and --seed must be non-negative')
    n_threads = args.threads
    print('\n\nNote: R/H native float64, JVS default float32, jvsa64 float64.\n')

    dense_cases = [(10, 4000, 4000), (20, 3000, 2000), (50, 2000, 2000),
                   (100, 1000, 2000), (500, 1000, 1000)]
    sparse_cases = [(100, 1000, .01), (50, 2000, .05)]
    if args.quick:
        dense_cases = [case for case in dense_cases if case[1:] != (4000, 4000)]
    if not args.sparse_only:
        benchmark_dense_cases(dense_cases, n_threads, return_cost=args.cost,
                              seed=args.seed, repeats=args.repeats)
    if hasattr(lap, 'lapmod_batch'):
        benchmark_sparse_cases(sparse_cases, n_threads, return_cost=args.cost,
                               seed=args.seed, repeats=args.repeats)
    else:
        print('\n# Sparse batch comparison skipped: the installed lapx has no lapmod_batch.')


if __name__ == '__main__':
    main()
