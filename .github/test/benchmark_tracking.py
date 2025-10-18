# Copyright (c) 2025 Ratha SIV | MIT License

"""
Benchmark `lapx` Assignment Methods for Object Tracking
=======================================================

Short summary
-------------
Benchmark wrapper utilities that compare LAPX assignment solvers (lapjv, lapjvx, lapjvc)
against SciPy's :func:`scipy.optimize.linear_sum_assignment` (LSA) in common object-tracking
scenarios where partial assignment and cost thresholding are required.

Extended description
--------------------
This module provides small wrapper functions that adapt solver outputs into a common
(matched pairs + unmatched lists) format used by tracking code, and it measures
end-to-end wrapper performance (assignment + post-filtering + unmatched computation).
It tests both square and rectangular cost matrices and highlights differences that
can arise from thresholding semantics and solver internals.

Notes
-----
- The benchmark measures application-level behaviour (what tracking code typically needs):
  the solver is run to produce a full assignment, and then matches are filtered by a
  cost threshold to produce the matched/unmatched sets.
- For object tracking this post-filtering approach (run solver -> drop matches above
  threshold) is intentionally used because it:
    * Produces matched and unmatched sets in the form tracking code expects.
    * Avoids slower solver internal paths that may be triggered when using in-solver
      partial-assignment options (e.g., passing ``cost_limit`` into the solver).
- If you require the solver to enforce partial assignment during optimization (i.e.,
  the solver must avoid assigning costly matches while solving), pass ``cost_limit``
  directly to the solver. Expect differences in performance and in the unmatched sets
  compared to the post-filter approach.
"""

import sys
import timeit
import lap
import numpy as np
import scipy.optimize

sys.stdout.reconfigure(encoding='utf-8')


def _decorate_return(n_rows, n_cols, matches):
    """
    Normalize `matches` and compute unmatched index lists.

    Parameters
    ----------
    n_rows : int
        Number of rows in the original cost matrix (number of left-side items).
    n_cols : int
        Number of columns in the original cost matrix (number of right-side items).
    matches : array-like
        Sequence of (row, col) pairs representing matched indices. May be a Python
        list of pairs or a numpy array. An empty sequence indicates no matches.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Normalized matches array. When there are no matches an empty array with shape
        (0, 2) and dtype int is returned.
    unmatched_rows : list of int
        Indices of rows (left-side items) that are unmatched.
    unmatched_cols : list of int
        Indices of columns (right-side items) that are unmatched.

    Notes
    -----
    This helper centralizes:
      - conversion of arbitrary sequence-like `matches` into the canonical numpy
        shape/dtype used by the wrappers,
      - consistent generation of unmatched lists across all wrappers.
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
    """
    Run :func:`lap.lapjv` (LAPX JV) with in-function filtering using `cost_limit`.

    This variant passes ``cost_limit=thresh`` into the solver so the solver enforces
    the partial-assignment constraint internally. As a result, some matches that would
    be produced by the post-filter approach are prevented during optimization.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        Cost matrix for assignment.
    thresh : float
        Cost threshold. Matches with cost > thresh will be discarded.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Array of (row, col) matched index pairs after thresholding.
    u_a : list of int
        List of unmatched row indices.
    u_b : list of int
        List of unmatched column indices.

    Notes
    -----
    - In-solver filtering may trigger slower internal code paths depending on the
      solver implementation and options; expect different performance characteristics.
    - We still normalize the solver output into the common (matches, u_a, u_b)
      format using :func:`_decorate_return` for consistency with other wrappers.
    """
    x, y = lap.lapjv(cost_matrix, extend_cost=True, cost_limit=thresh, return_cost=False)
    # Solver should already respect cost_limit, but for safety we still ensure matched pairs
    # reference valid indices (mx >= 0). No extra post-thresholding is performed here.
    matches = [[ix, mx] for ix, mx in enumerate(x) if mx >= 0]
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jv(cost_matrix, thresh):
    """
    Run :func:`lap.lapjv` (LAPX JV) and post-filter assignments by cost threshold.

    The function calls ``lap.lapjv`` without passing ``cost_limit`` and then removes
    any matches whose cost exceeds ``thresh``. This mirrors the post-filtering
    strategy used for other wrappers in this benchmark.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        Cost matrix for assignment.
    thresh : float
        Cost threshold. Matches with cost > thresh will be discarded.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Array of (row, col) matched index pairs after thresholding.
    u_a : list of int
        List of unmatched row indices.
    u_b : list of int
        List of unmatched column indices.

    Notes
    -----
    - Post-filtering (run solver -> drop matches above ``thresh``) is chosen here
      to match the behaviour used by :func:`lapx_jvx` and :func:`scipy_lsa`.
    - If you require the solver to enforce partial assignment during optimization,
      call :func:`lap.lapjv` with ``cost_limit`` set; expect potential performance
      differences and different unmatched sets.
    """
    x, y = lap.lapjv(cost_matrix, extend_cost=True, return_cost=False)
    matches = [[ix, mx] for ix, mx in enumerate(x) if mx >= 0 and cost_matrix[ix, mx] <= thresh]
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jvx(cost_matrix, thresh):
    """
    Run :func:`lap.lapjvx` (LAPX JVX) and post-filter assignments by cost threshold.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        Cost matrix for assignment.
    thresh : float
        Cost threshold. Matches with cost > thresh will be discarded.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Array of (row, col) matched index pairs after thresholding.
    u_a : list of int
        List of unmatched row indices.
    u_b : list of int
        List of unmatched column indices.

    Notes
    -----
    - Passing ``cost_limit`` and/or ``return_cost=True`` into ``lapjvx`` may trigger
      slower code paths. The benchmark uses post-filtering to measure the wrapper
      end-to-end performance consistently.
    """
    x, y = lap.lapjvx(cost_matrix, extend_cost=True, return_cost=False)
    matches = [[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh]
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def lapx_jvc(cost_matrix, thresh):
    """
    Run :func:`lap.lapjvc` (LAPX JVC) and post-filter assignments by cost threshold.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        Cost matrix for assignment.
    thresh : float
        Cost threshold. Matches with cost > thresh will be discarded.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Array of (row, col) matched index pairs after thresholding.
    u_a : list of int
        List of unmatched row indices.
    u_b : list of int
        List of unmatched column indices.
    """
    x, y = lap.lapjvc(cost_matrix, return_cost=False)
    matches = [[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh]
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)


def scipy_lsa(cost_matrix, thresh):
    """
    Wrapper for :func:`scipy.optimize.linear_sum_assignment` (LSA). Builds (row, col)
    pairs and post-filters by `thresh` to produce matches and unmatched lists.

    Parameters
    ----------
    cost_matrix : ndarray, shape (n_rows, n_cols)
        Cost matrix for assignment.
    thresh : float
        Cost threshold. Matches with cost > thresh will be discarded.

    Returns
    -------
    matches : ndarray, shape (k, 2), dtype=int
        Array of (row, col) matched index pairs after thresholding.
    u_a : list of int
        List of unmatched row indices.
    u_b : list of int
        List of unmatched column indices.
    """
    x, y = scipy.optimize.linear_sum_assignment(cost_matrix)
    matches = [[x[i], y[i]] for i in range(len(x)) if cost_matrix[x[i], y[i]] <= thresh]
    return _decorate_return(cost_matrix.shape[0], cost_matrix.shape[1], matches)

def compare_results_tabular(
    test_size,
    baseline,
    candidates,
    table_rows,
    all_results,
):
    """
    Accumulate a table row for the summary table for all methods.
    Each row: (size, baseline_time, [candidate_times + remarks])
    Also accumulates method-wise times and remarks for overall summary.
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
    positions = ["1st", "2nd", "3rd", "4th", "5th"]
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
    """
    Print the overall ranking summary below the table.
    Shows for each method how many times it placed 1st, 2nd, etc. using medals/flags.
    """
    method_count = len(header) - 1
    method_names = header[1:]
    # Compute sum of times for each method
    total_times = [sum(method["times"]) for method in all_results]
    sorted_idx = sorted(range(method_count), key=lambda i: total_times[i])

    # Map rank index to emoji
    pos_map = {0: "🥇", 1: "🥈", 2: "🥉", 3: "🚩", 4: "🏳️"}
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
    print("\n 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉 ")
    for rank, idx in enumerate(sorted_idx, 1):
        name = method_names[idx]
        ms = total_times[idx] * 1000
        medals, extra = emoji_summaries[idx]
        print(f"     {rank}. {name:<15}: {ms:10.4f} ms | {extra} | {medals}")
    print(" 🎉 ------------------------------------------------------------------- 🎉 \n")


def benchmark_tabular(sizes, thresh=1e6, debug=False):
    """
    For each size, run a single random cost matrix and race the solvers.
    Accumulate results for a tabular summary at the end.
    """
    table_rows = []
    header = [
        "Size",
        "BASELINE SciPy",
        "LAPX LAPJV-IFT",
        "LAPX LAPJV",
        "LAPX LAPJVX",
        "LAPX LAPJVC",
    ]
    # For summary: accumulate times and remarks per method
    all_results = [
        {"times": [], "remarks": []},  # BASELINE SciPy
        {"times": [], "remarks": []},  # LAPX LAPJV-IFT
        {"times": [], "remarks": []},  # LAPX LAPJV
        {"times": [], "remarks": []},  # LAPX LAPJVX
        {"times": [], "remarks": []},  # LAPX LAPJVC
    ]
    # For overall medal/flag counts per method
    position_records = [[] for _ in range(len(header) - 1)]

    for n, m in sizes:
        a = np.random.rand(n, m)

        # SciPy baseline
        start = timeit.default_timer()
        m_s, u_a_s, u_b_s = scipy_lsa(a, thresh)
        t_s = timeit.default_timer() - start
        baseline = (m_s, u_a_s, u_b_s, t_s, "BASELINE SciPy")

        # lapjvc
        start = timeit.default_timer()
        m_jvc, u_a_jvc, u_b_jvc = lapx_jvc(a, thresh)
        t_jvc = timeit.default_timer() - start

        # lapjv (post-filter)
        start = timeit.default_timer()
        m_jv, u_a_jv, u_b_jv = lapx_jv(a, thresh)
        t_jv = timeit.default_timer() - start

        # lapjv in-function (cost_limit)
        start = timeit.default_timer()
        m_jv_ift, u_a_jv_ift, u_b_jv_ift = lapx_jv_ift(a, thresh)
        t_jv_ift = timeit.default_timer() - start

        # lapjvx
        start = timeit.default_timer()
        m_jvx, u_a_jvx, u_b_jvx = lapx_jvx(a, thresh)
        t_jvx = timeit.default_timer() - start

        candidates = [
            (m_jv_ift, u_a_jv_ift, u_b_jv_ift, t_jv_ift, "LAPX LAPJV-IFT"),
            (m_jv, u_a_jv, u_b_jv, t_jv, "LAPX LAPJV"),
            (m_jvx, u_a_jvx, u_b_jvx, t_jvx, "LAPX LAPJVX"),
            (m_jvc, u_a_jvc, u_b_jvc, t_jvc, "LAPX LAPJVC"),
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
