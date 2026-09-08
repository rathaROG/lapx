# Copyright (c) 2026 Ratha SIV | MIT License

"""Benchmark lapx assignment methods for object tracking.

This module compares LAPX solvers (lapjv, lapjvx, lapjvc) with SciPy's
:func:`scipy.optimize.linear_sum_assignment` (LSA). The object tracking cases
require partial assignments and cost thresholds.

The wrappers convert solver outputs to a common format: matched pairs and
lists of unmatched indices. The benchmark measures the full wrapper call.
This includes the solve, the removal of matches above the cost threshold,
and the calculation of unmatched indices.

The benchmark uses square and rectangular cost matrices. It shows differences
that can result from threshold rules and solver internals.

Notes
-----
- The benchmark measures behavior that object tracking code typically needs.
  Each solver produces a full assignment. The wrapper then removes matches
  above the cost threshold to create matched and unmatched sets.
- The benchmark intentionally applies the threshold after the solve for these reasons:
  * The output has the matched and unmatched sets that tracking code expects.
  * This avoids slower internal paths that partial-assignment options such as cost_limit may select.
- To enforce partial assignment during optimization, pass cost_limit directly
  to a solver that accepts it. This prevents costly matches during the solve.
  Expect differences in performance and unmatched sets compared with threshold checks after the solve.
"""

import sys
from io import TextIOWrapper
if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

import timeit
import lap
import numpy as np
import scipy.optimize


def _decorate_return(n_rows, n_cols, matches):
    """Convert matches to a standard array. Calculate lists of unmatched indices.

    Parameters
    ----------
    n_rows : int
        The number of rows in the original cost matrix, or left-side items.
    n_cols : int
        The number of columns in the original cost matrix, or right-side items.
    matches : array-like
        A sequence of matched (row, col) pairs. This can be a Python list or a
        NumPy array. An empty sequence means that no matches exist.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        The array of matches in the standard format.
        If no matches exist, the array has shape (0, 2) and data type int.
    unmatched_rows : list of int
        These indices identify rows, or left-side items, without matches.
    unmatched_cols : list of int
        These indices identify columns, or right-side items, without matches.

    Notes
    -----
    All wrappers use this helper to convert matches to the same NumPy shape and
    data type. They also use it to create consistent lists of unmatched indices.
    """
    # Ensure ndarray
    matches = np.asarray(matches)

    # Normalize empty result and dtype
    if matches.size == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = matches.astype(int)

    # Compute unmatched lists
    if matches.size == 0:
        unmatched_rows = list(np.arange(n_rows))
        unmatched_cols = list(np.arange(n_cols))
    else:
        unmatched_rows = list(np.setdiff1d(np.arange(n_rows), matches[:, 0]))
        unmatched_cols = list(np.setdiff1d(np.arange(n_cols), matches[:, 1]))

    return matches, unmatched_rows, unmatched_cols


def lapx_jv_ift(cost_matrix, thresh):
    """Run :func:`lap.lapjv` (LAPX JV) with cost_limit to control partial assignment.

    The wrapper passes cost_limit=thresh to the solver.
    The solver then enforces the partial-assignment constraint during optimization.
    This prevents some matches that could occur if the wrapper applied the
    threshold only after the solve.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.

    Notes
    -----
    - The partial-assignment option may select slower internal paths, depending
      on the solver implementation and options. Expect differences in performance.
    - The wrapper uses :func:`_decorate_return` to return
      (matches, unmatched_rows, unmatched_cols), consistent with the other wrappers.
    """
    x, y = lap.lapjv(cost_matrix, extend_cost=True, cost_limit=thresh, return_cost=False)
    # Solver should already respect cost_limit, but for safety we still ensure matched pairs
    # reference valid indices (mx >= 0). No extra post-thresholding is performed here.
    # matches = [[ix, mx] for ix, mx in enumerate(x) if mx >= 0]
    valid = x >= 0
    matches = np.column_stack((np.where(valid)[0], x[valid]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jv(cost_matrix, thresh):
    """Run :func:`lap.lapjv` (LAPX JV). Then remove assignments above the cost threshold.

    The wrapper calls lap.lapjv without cost_limit. It then removes matches whose
    cost exceeds thresh. The other wrappers in this benchmark use the same method.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.

    Notes
    -----
    - The wrapper applies the threshold after the solve, as in :func:`lapx_jvx`
      and :func:`scipy_lsa`.
    - To enforce partial assignment during optimization, call :func:`lap.lapjv`
      with cost_limit. Performance and unmatched sets may differ.
    """
    x, y = lap.lapjv(cost_matrix, extend_cost=True, return_cost=False)
    # matches = [[ix, mx] for ix, mx in enumerate(x) if mx >= 0 and cost_matrix[ix, mx] <= thresh]
    valid = (x >= 0) & (cost_matrix[np.arange(len(x)), x] <= thresh)
    matches = np.column_stack((np.where(valid)[0], x[valid]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jvx(cost_matrix, thresh):
    """Run :func:`lap.lapjvx` (LAPX JVX). Then remove assignments above the cost threshold.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.

    Notes
    -----
    cost_limit, return_cost=True, or both may select slower code paths in lapjvx.
    The benchmark applies the threshold after the solve to measure the full
    wrapper call consistently.
    """
    rids, cids = lap.lapjvx(cost_matrix, extend_cost=True, return_cost=False)
    # matches = [[rids[i], cids[i]] for i in range(len(rids)) if cost_matrix[rids[i], cids[i]] <= thresh]
    mask = cost_matrix[rids, cids] <= thresh
    matches = np.column_stack((rids[mask], cids[mask]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jvs(cost_matrix, thresh):
    """Run :func:`lap.lapjvs` (LAPX JVS). Then remove assignments above the cost threshold.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.

    Notes
    -----
    return_cost=True may select slower code paths in lapjvs.
    The benchmark applies the threshold after the solve to measure the full
    wrapper call consistently.
    """
    rids, cids = lap.lapjvs(cost_matrix, extend_cost=True, return_cost=False)
    # matches = [[rids[i], cids[i]] for i in range(len(rids)) if cost_matrix[rids[i], cids[i]] <= thresh]
    mask = cost_matrix[rids, cids] <= thresh
    matches = np.column_stack((rids[mask], cids[mask]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jvc(cost_matrix, thresh):
    """Run :func:`lap.lapjvc` (LAPX JVC). Then remove assignments above the cost threshold.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.
    """
    rids, cids = lap.lapjvc(cost_matrix, return_cost=False)
    # matches = [[rids[i], cids[i]] for i in range(len(rids)) if cost_matrix[rids[i], cids[i]] <= thresh]
    mask = cost_matrix[rids, cids] <= thresh
    matches = np.column_stack((rids[mask], cids[mask]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def scipy_lsa(cost_matrix, thresh):
    """Solve with :func:`scipy.optimize.linear_sum_assignment` (LSA).

    The wrapper creates (row, col) pairs. It then applies thresh to produce
    matched pairs and lists of unmatched indices.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        The cost matrix for assignment.
    thresh : float
        The cost threshold. The wrapper removes matches with cost > thresh.
    """
    rids, cids = scipy.optimize.linear_sum_assignment(cost_matrix)
    # matches = [[rids[i], cids[i]] for i in range(len(rids)) if cost_matrix[rids[i], cids[i]] <= thresh]
    mask = cost_matrix[rids, cids] <= thresh
    matches = np.column_stack((rids[mask], cids[mask]))
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)

def compare_results_tabular(
    test_size,
    baseline,
    candidates,
    table_rows,
    all_results,
):
    """Add one row for all methods to the summary table.

    Each row contains (size, baseline_time, [candidate_times + remarks]).
    The function also collects times and remarks by method for the overall summary.
    """
    b_m, b_un_a, b_un_b, b_time, b_name = baseline

    remarks = []
    for c in candidates:
        c_m, c_un_a, c_un_b, c_time, c_name = c
        m_ok = set(map(tuple, b_m)) == set(map(tuple, c_m))
        un_a_ok = set(b_un_a) == set(c_un_a)
        un_b_ok = set(b_un_b) == set(c_un_b)
        if m_ok and un_a_ok and un_b_ok:
            remark = "✓"
        else:
            remark = "✗"
        remarks.append(remark)

    # Ranking by time (ascending)
    all_methods = [baseline] + candidates
    times = [x[3] for x in all_methods]
    idx_sorted = sorted(range(len(times)), key=lambda i: times[i])
    positions = ["1st", "2nd", "3rd", "4th", "5th", "6th"]
    position_by_idx = {i: positions[j] for j, i in enumerate(idx_sorted)}

    # Build row: test size, baseline (time+rank+remark), candidates (time+rank+remark)
    row = []
    size_str = f"{test_size[0]}x{test_size[1]}"
    row.append(size_str)
    # Baseline
    row.append(f"{b_time:.6f}s {position_by_idx[0]}")
    # Accumulate for summary
    all_results[0]["times"].append(b_time)
    all_results[0]["remarks"].append("✓")  # baseline always considered "✓"
    for i, c in enumerate(candidates, 1):
        c_time = c[3]
        remark = remarks[i - 1]
        row.append(f"{c_time:.6f}s {remark} {position_by_idx[i]}")
        all_results[i]["times"].append(c_time)
        all_results[i]["remarks"].append(remark)
    table_rows.append(row)

def print_overall_ranking(header, all_results, position_records):
    """Print the overall rankings below the table.

    For each method, show how often it ranks first, second, and so on.
    Use medals and flags to indicate the ranks.
    """
    method_count = len(header) - 1
    method_names = header[1:]
    # Compute sum of times for each method
    total_times = [sum(method["times"]) for method in all_results]
    sorted_idx = sorted(range(method_count), key=lambda i: total_times[i])

    # Map rank index to emoji
    pos_map = {0: "🥇", 1: "🥈", 2: "🥉", 3: "🚩", 4: "🏳️", 5: "🥴"}
    # Compose emoji summary per method
    emoji_summaries = []
    for idx in range(method_count):
        # Count medals for this method
        counts = {}
        for pos in position_records[idx]:
            counts[pos] = counts.get(pos, 0) + 1
        summary = []
        for pos_idx in range(method_count):
            if counts.get(pos_idx, 0):
                summary.append(f"{pos_map[pos_idx]}x{counts[pos_idx]}")
        summary_str = " ".join(summary)
        # Add correctness/remark
        if idx == 0:
            extra = "⭐"
        elif any(r == "✗" for r in all_results[idx]["remarks"]):
            extra = "⚠️"
        else:
            extra = "✅"
        emoji_summaries.append((summary_str, extra))

    # Compose output lines
    print("\n 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 ")
    for rank, idx in enumerate(sorted_idx, 1):
        name = method_names[idx]
        ms = total_times[idx] * 1000
        medals, extra = emoji_summaries[idx]
        print(f"     {rank}. {name:<15}: {ms:10.4f} ms | {extra} | {medals}")
    print(" 🎉 ------------------------------------------------------------------------- 🎉 \n")


def benchmark_tabular(sizes, thresh=1e6, debug=False):
    """For each size, compare the solvers on one random cost matrix.

    Collect the results for a final summary table.
    """
    table_rows = []
    header = [
        "Size",
        "BASELINE SciPy",
        "LAPX LAPJV-IFT",
        "LAPX LAPJV",
        "LAPX LAPJVX",
        "LAPX LAPJVC",
        "LAPX LAPJVS",
    ]
    # For summary: accumulate times and remarks per method
    all_results = [
        {"times": [], "remarks": []},  # BASELINE SciPy
        {"times": [], "remarks": []},  # LAPX LAPJV-IFT
        {"times": [], "remarks": []},  # LAPX LAPJV
        {"times": [], "remarks": []},  # LAPX LAPJVX
        {"times": [], "remarks": []},  # LAPX LAPJVC
        {"times": [], "remarks": []},  # LAPX LAPJVS
    ]
    # For overall medal/flag counts per method
    position_records = [[] for _ in range(len(header) - 1)]

    for n, m in sizes:
        a = np.random.rand(n, m)
        a_warm = np.random.rand(100, 100)

        # SciPy baseline
        scipy_lsa(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_s, u_a_s, u_b_s = scipy_lsa(a, thresh)
        t_s = timeit.default_timer() - start
        baseline = (m_s, u_a_s, u_b_s, t_s, "BASELINE SciPy")

        # lapjvc
        lapx_jvc(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_jvc, u_a_jvc, u_b_jvc = lapx_jvc(a, thresh)
        t_jvc = timeit.default_timer() - start

        # lapjv (post-filter)
        lapx_jv(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_jv, u_a_jv, u_b_jv = lapx_jv(a, thresh)
        t_jv = timeit.default_timer() - start

        # lapjv in-function (cost_limit)
        lapx_jv_ift(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_jv_ift, u_a_jv_ift, u_b_jv_ift = lapx_jv_ift(a, thresh)
        t_jv_ift = timeit.default_timer() - start

        # lapjvx
        lapx_jvx(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_jvx, u_a_jvx, u_b_jvx = lapx_jvx(a, thresh)
        t_jvx = timeit.default_timer() - start

        # lapjvs
        lapx_jvs(a_warm, thresh)  # warm-up
        start = timeit.default_timer()
        m_jvs, u_a_jvs, u_b_jvs = lapx_jvs(a, thresh)
        t_jvs = timeit.default_timer() - start

        candidates = [
            (m_jv_ift, u_a_jv_ift, u_b_jv_ift, t_jv_ift, "LAPX LAPJV-IFT"),
            (m_jv, u_a_jv, u_b_jv, t_jv, "LAPX LAPJV"),
            (m_jvx, u_a_jvx, u_b_jvx, t_jvx, "LAPX LAPJVX"),
            (m_jvc, u_a_jvc, u_b_jvc, t_jvc, "LAPX LAPJVC"),
            (m_jvs, u_a_jvs, u_b_jvs, t_jvs, "LAPX LAPJVS"),
        ]

        compare_results_tabular((n, m), baseline, candidates, table_rows, all_results)

        # Record position index for each method
        all_methods = [baseline] + candidates
        times = [x[3] for x in all_methods]
        idx_sorted = sorted(range(len(times)), key=lambda i: times[i])
        for place, method_idx in enumerate(idx_sorted):
            position_records[method_idx].append(place)

    # Print big table
    colwidths = [max(len(str(cell)) for cell in col) for col in zip(header, *table_rows)]
    fmt_row = " | ".join(f"{{:<{w}}}" for w in colwidths)
    print("\n" + "-" * (sum(colwidths) + 3 * len(colwidths)))
    print(fmt_row.format(*header))
    print("-" * (sum(colwidths) + 3 * len(colwidths)))
    for row in table_rows:
        print(fmt_row.format(*row))
    print("-" * (sum(colwidths) + 3 * len(colwidths)) + "\n")
    print("Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).")
    print_overall_ranking(header, all_results, position_records)


if __name__ == "__main__":

    sizes = [
        (10, 10),
        (25, 20),
        (50, 50),
        (100, 150),
        (250, 250),
        (550, 500),
        (1000, 1000),
        (2000, 2500),
        (5000, 5000)
    ]

    thresh = [0.05, 0.1, 0.5, 1.0, 1e9]

    for t in thresh:
        print("\n" + "#" * 65)
        print(f"# Benchmark with threshold (cost_limit) = {t}")
        print("#" * 65)
        benchmark_tabular(sizes, thresh=t)
