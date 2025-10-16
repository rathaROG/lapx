import sys
import timeit
import lap
import numpy as np
from scipy.optimize import linear_sum_assignment

sys.stdout.reconfigure(encoding='utf-8')


def do_lapjvc(input, n_m=None):
    start_time = timeit.default_timer()
    x, y = lap.lapjvc(input, return_cost=False)
    r = np.array(list(zip(x, y)))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjv(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    x, y = lap.lapjv(input, extend_cost=ext_cost, return_cost=False)
    r = np.array([[y[i],i] for i in x if i >= 0])
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def do_lapjvx(input, n_m=None):
    start_time = timeit.default_timer()
    ext_cost = input.shape[0] != input.shape[1]
    x, y = lap.lapjvx(input, extend_cost=ext_cost, return_cost=False)
    r = np.array(list(zip(x, y)))
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

def do_scipy(input, n_m=None):
    start_time = timeit.default_timer()
    x, y = linear_sum_assignment(input)
    r = np.array(list(zip(x, y)))
    if n_m is not None: r = filter_assignment(r, n_m)
    t = timeit.default_timer() - start_time
    return r, t

def filter_assignment(assignment, n_m):
    """Keep only assignment pairs where 0 <= row < n_rows and 0 <= col < n_cols."""
    return np.array([[r, c] for r, c in assignment if 0 <= r < n_m[0] and 0 <= c < n_m[1]])

def assignments_equal(a1, a2):
    """Returns True if two assignment arrays (N,2) contain the same pairs, regardless of order."""
    return set(map(tuple, a1)) == set(map(tuple, a2))

def compare_results(baseline, candidates, debug=False):
    """
    baseline: (result, time, name)
    candidates: list of (result, time, name)
    """
    if debug:
        print(f"\n # {baseline[2]}:")
        print(f"{baseline[0]}")
        for c in candidates:
            print(f"\n # {c[2]}:")
            print(f"{c[0]}")
        print()

    for c in candidates:
        if assignments_equal(baseline[0], c[0]):
            if c[1] <= baseline[1]:
                print(f" * {c[2]} : ✅ Passed 🏆 {round((baseline[1]/c[1]), 2)} x faster ")
            else:
                print(f" * {c[2]} : ✅ Passed 🐌 {round((c[1]/baseline[1]), 2)} x slower ")
        else:
            print(f" * {c[2]} : ❌ Failed!")
    
    # print ranking by time
    ranking = sorted(candidates + [baseline], key=lambda x: x[1])
    print("\n ----- 🎉 SPEED RANKING 🎉 ----- ")
    for idx, (_, t, n) in enumerate(ranking, 1):
        print(f"   {idx}. {n} \t: {t:.8f}s")
    print(" ------------------------------- \n")

def test(n, m, debug=False):
    print("-----------------------------------------")
    print(f"Test ({n}, {m})")
    print("-----------------------------------------")
    a = np.random.rand(n, m)
    (r_b, t_b), n_b = do_scipy(a), "scipy"
    (r_c1, t_c1), n_c1 = do_lapjvc(a), "lapjvc"
    (r_c2, t_c2), n_c2 = do_lapjv(a), "lapjv"
    (r_c3, t_c3), n_c3 = do_lapjvx(a), "lapjvx"
    (r_c4, t_c4), n_c4 = do_lapjvxa(a), "lapjvxa"
    compare_results(
        (r_b, t_b, n_b), 
        [(r_c1, t_c1, n_c1), (r_c2, t_c2, n_c2), 
         (r_c3, t_c3, n_c3), (r_c4, t_c4, n_c4)], 
        debug=debug
    )


if __name__ == '__main__':

    test(n=4, m=5)
    test(n=5, m=5)
    test(n=5, m=6)

    test(n=45, m=50)
    test(n=50, m=50)
    test(n=50, m=55)

    test(n=450, m=500)
    test(n=500, m=500)
    test(n=500, m=550)
    
    test(n=2500, m=5000)
    test(n=5000, m=5000)
    test(n=5000, m=7500)
