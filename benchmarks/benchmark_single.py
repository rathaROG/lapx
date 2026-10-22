"""Compare the time needed to produce assignment pairs.

All solvers use return_cost=False. R/H preserve the generated float64 inputs
with precision='native'; existing solvers keep their default precision settings.
Pairs are requested directly where supported; required conversion is timed.
Input generation, warmup, and result checks are outside timing.
"""

import argparse
import sys
from io import TextIOWrapper
from unicodedata import east_asian_width
if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

import timeit
import lap
import numpy as np
from scipy.optimize import linear_sum_assignment


def do_lapjvs(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    x, y = lap.lapjvs(input, extend_cost=ext_cost, return_cost=False)
    r = np.column_stack((x, y))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvsa(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    r = lap.lapjvsa(input, extend_cost=ext_cost, return_cost=False)
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvc(input, n_m=None):
    start_time = timeit.default_timer()
    x, y = lap.lapjvc(input, return_cost=False)
    r = np.column_stack((x, y))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjv(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    x, y = lap.lapjv(input, extend_cost=ext_cost, return_cost=False)
    valid = x >= 0
    r = np.column_stack((np.arange(len(x))[valid], x[valid]))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvx(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    x, y = lap.lapjvx(input, extend_cost=ext_cost, return_cost=False)
    r = np.column_stack((x, y))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvxa(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    r = lap.lapjvxa(input, extend_cost=ext_cost, return_cost=False)
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvr(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    r = lap.lapjvr(input, extend_cost=ext_cost, return_cost=False, precision='native', output='pairs')
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvh(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    r = lap.lapjvh(input, extend_cost=ext_cost, return_cost=False, precision='native', output='pairs')
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_scipy(input, n_m=None):
    start_time = timeit.default_timer()
    x, y = linear_sum_assignment(input)
    r = np.column_stack((x, y))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def filter_assignment(assignment, n_m):
    """Keep only assignment pairs where 0 <= row < n_rows and 0 <= col < n_cols."""
    return np.array([[r, c] for r, c in assignment if 0 <= r < n_m[0] and 0 <= c < n_m[1]])

def assignments_equal(a1, a2):
    """Return True if two assignment arrays with shape (N, 2) contain the same pairs, regardless of order."""
    return set(map(tuple, a1)) == set(map(tuple, a2))

def compare_results(baseline, candidates, debug=False, *, checks=None):
    """Compare a baseline result with candidate results.

    baseline is a (result, time, name) tuple.
    candidates is a list of (result, time, name) tuples.
    """
    if debug:
        print(f"\n # {baseline[2]}:")
        print(f"{baseline[0]}")
        for c in candidates:
            print(f"\n # {c[2]}:")
            print(f"{c[0]}")
        print()

    # One table, sorted by time. Always display milliseconds for every matrix size.
    ranking = sorted(candidates + [baseline], key=lambda x: x[1])
    header = ('Solver', 'Check', 'Time (ms)', 'vs SciPy')
    rows = []
    for rank, candidate in enumerate(ranking, 1):
        result, elapsed, name = candidate
        if candidate is baseline:
            check, relative = '⭐ BASE', '⭐ baseline'
        elif not (checks[name] if checks is not None else assignments_equal(baseline[0], result)):
            check, relative = '❌ FAIL', '-'
        else:
            check = '✅ PASS'
            if elapsed <= 0 or baseline[1] <= 0:
                relative = 'n/a'
            elif elapsed == baseline[1]:
                relative = '🤝 same'
            elif elapsed < baseline[1]:
                medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, '🏆')
                relative = f'{medal} {baseline[1] / elapsed:.2f}x faster'
            else:
                relative = f'🐌 {elapsed / baseline[1]:.2f}x slower'
        rows.append((name, check, f'{elapsed * 1e3:.6f}', relative))

    # These emoji occupy two terminal columns, unlike their Python string length.
    def display_width(text):
        return sum(2 if east_asian_width(char) in ('W', 'F') else 1 for char in text)

    widths = [max(display_width(cell) for cell in column) for column in zip(header, *rows)]

    def format_row(row):
        cells = []
        for cell, width, align in zip(row, widths, ('<', '<', '>', '<')):
            padding = ' ' * (width - display_width(cell))
            cells.append(padding + cell if align == '>' else cell + padding)
        return '  '.join(cells).rstrip()

    separator = '-' * (sum(widths) + 2 * (len(widths) - 1))
    print(format_row(header))
    print(separator)
    for row in rows:
        print(format_row(row))
    print(separator)

def test(n, m, debug=False, *, seed=2026, repeats=3):
    print(f'\n### Matrix {n} x {m} | float64 | return_cost=False\n')
    calls = 25 if max(n, m) <= 64 else 1
    if repeats > 1:
        print(f'* Median of {repeats} shuffled rounds, {calls} calls/round;')
        print(f'input seeds={seed}..{seed + repeats - 1}; warmup each round.\n')
    solvers = [
        ('lapjvc', do_lapjvc), ('lapjv', do_lapjv),
        ('lapjvx', do_lapjvx), ('lapjvxa', do_lapjvxa),
        ('lapjvs', do_lapjvs), ('lapjvsa', do_lapjvsa),
    ]
    for name, solve in (('lapjvr', do_lapjvr), ('lapjvh', do_lapjvh)):
        if hasattr(lap, name):
            solvers.append((name, solve))
        else:
            print(f'# Skipping {name}: the installed LAPX does not include this family.')

    solvers.insert(0, ('scipy', do_scipy))
    order_rng = np.random.default_rng([seed, n, m, 1])
    samples = [[] for _ in solvers]
    outputs = [None] * len(solvers)
    checks = {name: True for name, _ in solvers}
    for round_index in range(repeats):
        a = np.random.default_rng([seed + round_index, n, m]).random((n, m))
        for name, solve in solvers:
            solve(a)  # Warm every solver on this round's shared input, outside timing.
        for index in order_rng.permutation(len(solvers)):
            elapsed = 0.0
            for _ in range(calls):
                result, duration = solvers[index][1](a)
                elapsed += duration
            samples[index].append(elapsed / calls)
            outputs[index] = result
        for index, (name, _) in enumerate(solvers):
            checks[name] &= assignments_equal(outputs[0], outputs[index])
        del a
    results = [(result, float(np.median(times)), name)
               for result, times, (name, _) in zip(outputs, samples, solvers)]
    compare_results(results[0], results[1:], debug=debug, checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Run sizes through 2500x5000.')
    parser.add_argument('--seed', type=int, default=2026,
                        help='Base seed; each round uses seed + round index (default: 2026).')
    parser.add_argument('--repeats', type=int, default=3, help='Timed rounds (default: 3).')
    args = parser.parse_args()
    if args.repeats < 1 or args.seed < 0:
        parser.error('--repeats must be positive and --seed must be non-negative')
    print('\n\nNote: R/H native float64, JVS default float32.\n')
    sizes = [(4, 5), (5, 5), (5, 6), (45, 50), (50, 50), (50, 55),
             (450, 500), (500, 500), (500, 550),
             (2500, 5000), (5000, 5000), (5000, 7500)]
    for n, m in sizes[:10] if args.quick else sizes:
        repeats = args.repeats
        if n >= 5000 or m >= 5000:
            repeats = 1
        test(n, m, seed=args.seed, repeats=repeats)


if __name__ == '__main__':
    main()
