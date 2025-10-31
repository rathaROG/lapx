import numpy as np
import pytest

try:
    import lap
except ImportError as e:
    pytest.skip(f"lap module not importable: {e}", allow_module_level=True)


def _has_attr(name: str) -> bool:
    return hasattr(lap, name) and callable(getattr(lap, name))


def _call_single(func, cost):
    for kwargs in (
        dict(extend_cost=True, return_cost=True, jvx_like=True),
        dict(extend_cost=True, return_cost=True),
        dict(return_cost=True),
    ):
        try:
            return func(cost, **kwargs)
        except TypeError:
            continue
    return func(cost)


def _call_batch(func, costs):
    for kwargs in (
        dict(extend_cost=True, return_cost=True, n_threads=2),
        dict(return_cost=True, n_threads=2),
        dict(return_cost=True),
    ):
        try:
            return func(costs, **kwargs)
        except TypeError:
            continue
    return func(costs)


def _to_pairs_single(name, ret, N, M):
    if not isinstance(ret, (tuple, list)):
        raise AssertionError(f"{name}: expected tuple/list return")
    if len(ret) == 2:
        cost_val, assignments = ret
        a = np.asarray(assignments)
        assert a.ndim == 2 and a.shape[1] == 2, f"{name}: assignments must be (K,2)"
        rows, cols = a[:, 0].astype(int), a[:, 1].astype(int)
        return float(cost_val), rows, cols

    if len(ret) == 3:
        cost_val, a2, a3 = ret
        a2 = np.asarray(a2)
        a3 = np.asarray(a3)
        if a2.shape == (N,) and a3.shape == (M,):
            rows = np.arange(N)[a2 >= 0]
            cols = a2[a2 >= 0].astype(int)
            return float(cost_val), rows.astype(int), cols
        if a2.shape == a3.shape and a2.ndim == 1:
            K = a2.shape[0]
            assert K <= min(N, M), f"{name}: K > min(N,M)"
            return float(cost_val), a2.astype(int), a3.astype(int)

    raise AssertionError(f"{name}: unsupported return structure: {type(ret)} len={len(ret)}")


def _recompute_cost_from_pairs(C, rows, cols):
    rows = np.asarray(rows, dtype=int)
    cols = np.asarray(cols, dtype=int)
    assert rows.shape == cols.shape
    vals = C[rows, cols].astype(np.float64)
    return float(vals.sum()) if vals.size else 0.0


def _normalize_batch_lists(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, np.ndarray) and obj.dtype == object:
        return list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    return obj


def _to_pairs_batch(name, ret, B, N, M):
    if not isinstance(ret, (tuple, list)) or len(ret) not in (2, 3):
        raise AssertionError(f"{name}: unsupported batch return")

    if len(ret) == 2:
        costs, assignments_list = ret
        costs = np.asarray(costs, dtype=np.float64).reshape(-1)
        assert costs.shape == (B,), f"{name}: costs must be (B,)"
        assignments_list = _normalize_batch_lists(assignments_list)
        assert isinstance(assignments_list, list) and len(assignments_list) == B, f"{name}: assignments list len != B"
        rows_list, cols_list = [], []
        for ab in assignments_list:
            ab = np.asarray(ab)
            assert ab.ndim == 2 and ab.shape[1] == 2, f"{name}: each assignments must be (Kb,2)"
            rows_list.append(ab[:, 0].astype(int))
            cols_list.append(ab[:, 1].astype(int))
        return costs, rows_list, cols_list

    costs, a2, a3 = ret
    costs = np.asarray(costs, dtype=np.float64).reshape(-1)
    assert costs.shape == (B,), f"{name}: costs must be (B,)"

    a2_arr = np.asarray(a2)
    a3_arr = np.asarray(a3)
    if a2_arr.ndim == 2 and a2_arr.shape == (B, N) and a3_arr.ndim == 2 and a3_arr.shape == (B, M):
        rows_list, cols_list = [], []
        for b in range(B):
            rsol = a2_arr[b]
            rows = np.arange(N)[rsol >= 0]
            cols = rsol[rsol >= 0].astype(int)
            rows_list.append(rows.astype(int))
            cols_list.append(cols)
        return costs, rows_list, cols_list

    rows_list = _normalize_batch_lists(a2)
    cols_list = _normalize_batch_lists(a3)
    assert isinstance(rows_list, list) and isinstance(cols_list, list), f"{name}: rows/cols must be lists"
    assert len(rows_list) == len(cols_list) == B, f"{name}: list lens must equal B"
    norm_rows, norm_cols = [], []
    for rb, cb in zip(rows_list, cols_list):
        rb = np.asarray(rb)
        cb = np.asarray(cb)
        if rb.ndim == 2 and rb.shape[1] == 2:
            norm_rows.append(rb[:, 0].astype(int))
            norm_cols.append(rb[:, 1].astype(int))
        else:
            assert rb.ndim == 1 and cb.ndim == 1 and rb.shape == cb.shape, f"{name}: mismatched per-batch pair lists"
            norm_rows.append(rb.astype(int))
            norm_cols.append(cb.astype(int))
    return costs, norm_rows, norm_cols


@pytest.mark.smoke
def test_single_matrix_solvers_smoke():
    rng = np.random.default_rng(12345)
    N, M = 4, 5
    C = rng.random((N, M), dtype=np.float64)

    solver_names = ("lapjv", "lapjvx", "lapjvxa", "lapjvc", "lapjvs", "lapjvsa")
    found = [(n, getattr(lap, n)) for n in solver_names if _has_attr(n)]
    if not found:
        pytest.skip("No single-matrix solvers found")

    totals = {}
    for name, fn in found:
        ret = _call_single(fn, C)
        cost_val, rows, cols = _to_pairs_single(name, ret, N, M)
        assert len(rows) == len(cols) <= min(N, M)
        assert len(set(rows.tolist())) == len(rows)
        assert len(set(cols.tolist())) == len(cols)
        recomputed = _recompute_cost_from_pairs(C, rows, cols)
        assert np.isfinite(cost_val) and np.isfinite(recomputed)
        assert np.isclose(cost_val, recomputed, rtol=1e-8, atol=1e-10)
        totals[name] = cost_val

    baseline = next(iter(totals.values()))
    for name, val in totals.items():
        assert np.isclose(val, baseline, rtol=1e-8, atol=1e-10), f"Cost mismatch for {name}"


@pytest.mark.smoke
def test_batch_matrix_solvers_smoke():
    rng = np.random.default_rng(54321)
    B, N, M = 3, 4, 5
    Cb = rng.random((B, N, M), dtype=np.float64)

    solver_names = ("lapjvx_batch", "lapjvxa_batch", "lapjvs_batch", "lapjvsa_batch")
    found = [(n, getattr(lap, n)) for n in solver_names if _has_attr(n)]
    if not found:
        pytest.skip("No batch solvers found")

    results = {}
    for name, fn in found:
        ret = _call_batch(fn, Cb)
        costs, rows_list, cols_list = _to_pairs_batch(name, ret, B, N, M)
        assert len(rows_list) == len(cols_list) == B
        recomputed = np.empty(B, dtype=float)
        for b in range(B):
            rows = np.asarray(rows_list[b], dtype=int)
            cols = np.asarray(cols_list[b], dtype=int)
            assert len(rows) == len(cols) <= min(N, M)
            assert len(set(rows.tolist())) == len(rows)
            assert len(set(cols.tolist())) == len(cols)
            recomputed[b] = _recompute_cost_from_pairs(Cb[b], rows, cols)
        costs = np.asarray(costs, dtype=np.float64)
        assert np.all(np.isfinite(costs)) and np.all(np.isfinite(recomputed))
        assert np.allclose(costs, recomputed, rtol=1e-8, atol=1e-10), f"Recomputed mismatch for {name}"
        results[name] = costs

    base = next(iter(results.values()))
    for name, arr in results.items():
        assert np.allclose(arr, base, rtol=1e-8, atol=1e-10), f"Batch cost mismatch for {name}"
