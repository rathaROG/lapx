# Copyright (c) 2025 Ratha SIV | MIT License

"""
Benchmark `lapx` Assignment Methods for Object Tracking

This benchmark script compares the performance and correctness of various LAPX assignment solvers
(`lapjv`, `lapjvx`, `lapjvc`) against `scipy.optimize.linear_sum_assignment` in the context of 
object tracking, where partial assignment and cost thresholding are often required.

- Tests both square and rectangular cost matrices.
- Evaluates speed and result equivalence for typical object tracking scenarios.
- Highlights differences in assignment and unmatched sets due to thresholding and solver internals.

Dependencies:
    numpy, lapx, scipy
"""

import numpy as np
import lap
import scipy.optimize
import time

def lapx_jv(cost_matrix, thresh):
    x, y = lap.lapjv(cost_matrix, extend_cost=True, cost_limit=thresh, return_cost=False)
    matches = np.array([[ix, mx] for ix, mx in enumerate(x) if mx >= 0])
    unmatched_a = np.where(x < 0)[0]
    unmatched_b = np.where(y < 0)[0]
    return matches, unmatched_a, unmatched_b

def lapx_jvx(cost_matrix, thresh):
    x, y  = lap.lapjvx(cost_matrix, extend_cost=True, return_cost=False)
    matches = np.asarray([[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh])
    if len(matches) == 0:
        unmatched_a = list(np.arange(cost_matrix.shape[0]))
        unmatched_b = list(np.arange(cost_matrix.shape[1]))
    else:
        unmatched_a = list(frozenset(np.arange(cost_matrix.shape[0])) - frozenset(matches[:, 0]))
        unmatched_b = list(frozenset(np.arange(cost_matrix.shape[1])) - frozenset(matches[:, 1]))
    return matches, unmatched_a, unmatched_b

def lapx_jvc(cost_matrix, thresh):
    x, y = lap.lapjvc(cost_matrix, return_cost=False)
    matches = np.asarray([[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh])
    if len(matches) == 0:
        unmatched_a = list(np.arange(cost_matrix.shape[0]))
        unmatched_b = list(np.arange(cost_matrix.shape[1]))
    else:
        unmatched_a = list(frozenset(np.arange(cost_matrix.shape[0])) - frozenset(matches[:, 0]))
        unmatched_b = list(frozenset(np.arange(cost_matrix.shape[1])) - frozenset(matches[:, 1]))
    return matches, unmatched_a, unmatched_b

def scipy_way(cost_matrix, thresh):
    x, y = scipy.optimize.linear_sum_assignment(cost_matrix)
    matches = np.asarray([[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh])
    if len(matches) == 0:
        unmatched_a = list(np.arange(cost_matrix.shape[0]))
        unmatched_b = list(np.arange(cost_matrix.shape[1]))
    else:
        unmatched_a = list(frozenset(np.arange(cost_matrix.shape[0])) - frozenset(matches[:, 0]))
        unmatched_b = list(frozenset(np.arange(cost_matrix.shape[1])) - frozenset(matches[:, 1]))
    return matches, unmatched_a, unmatched_b

def benchmark(sizes, thresh=1e6, repeats=3):
    print(f"\n{'Size':>10} | {'LAPX JV':>10} | {'LAPX JVX':>10} | {'LAPX JVC':>10} | {'Scipy':>10} | {'Diff From Scipy':>15}")
    print("-"*80)
    for n, m in sizes:
        t_jv, t_jvx, t_jvc, t_sp = 0, 0, 0, 0
        diff_names = set()
        r = 1 if max(n, m) >= 2000 else repeats
        for i in range(r):
            cost_matrix = np.random.rand(n, m)
            # Scipy baseline
            start = time.time()
            matches_s, unmatched_a_s, unmatched_b_s = scipy_way(cost_matrix, thresh)
            t_sp += (time.time() - start) * 1000
            start = time.time()
            matches_jv, unmatched_a_jv, unmatched_b_jv = lapx_jv(cost_matrix, thresh)
            t_jv += (time.time() - start) * 1000
            start = time.time()
            matches_jvx, unmatched_a_jvx, unmatched_b_jvx = lapx_jvx(cost_matrix, thresh)
            t_jvx += (time.time() - start) * 1000
            start = time.time()
            matches_jvc, unmatched_a_jvc, unmatched_b_jvc = lapx_jvc(cost_matrix, thresh)
            t_jvc += (time.time() - start) * 1000

            # Compare results to scipy
            for name, matches, unmatched_a, unmatched_b in [
                ('JV', matches_jv, unmatched_a_jv, unmatched_b_jv),
                ('JVX', matches_jvx, unmatched_a_jvx, unmatched_b_jvx),
                ('JVC', matches_jvc, unmatched_a_jvc, unmatched_b_jvc),
            ]:
                if set(map(tuple, matches)) != set(map(tuple, matches_s)) or set(unmatched_a) != set(unmatched_a_s) or set(unmatched_b) != set(unmatched_b_s):
                    diff_names.add(name)
            print(f"  {n}x{m} repeat {i+1}/{r} done...", end="\r")
        diff_names_str = ", ".join(sorted(diff_names)) if diff_names else ""
        print(f"{n:>5}x{m:<4} | {t_jv/r:>10.2f} | {t_jvx/r:>10.2f} | {t_jvc/r:>10.2f} | {t_sp/r:>10.2f} | {diff_names_str}")


if __name__ == "__main__":
    sizes = [
        (10, 10),
        (25, 25),
        (50, 50),
        (100, 150),
        (200, 200),
        (550, 500),
        (1000, 1000),
        (5000, 5000)
    ]

    thresh = [1e6, 0.1, 0.5, 0.7, 0.9]

    for t in thresh:
        print(f"\nBenchmark with threshold = {t}")
        benchmark(sizes, thresh=t, repeats=5)

