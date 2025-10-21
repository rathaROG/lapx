<details><summary>🆕 What's new</summary><br>

- 2025/10/21: `lapx` [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) introduced **`lapjvs()`**.
- 2025/10/16: `lapx` [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) introduced **`lapjvx()`**, **`lapjvxa()`**, and **`lapjvc()`**.
- 2025/10/15: Added Python 3.14 support and [more](https://github.com/rathaROG/lapx/pull/15).
- 2024/12/01: The original [`lap`](https://github.com/gatagat/lap) and [`lapx`](https://github.com/rathaROG/lapx) have been merged.

</details>

---

[![Test Simple](https://github.com/rathaROG/lapx/actions/workflows/test_simple.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/test_simple.yaml)
[![Benchmark](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml)
[![Test PyPI Build](https://github.com/rathaROG/lapx/actions/workflows/prepublish.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/prepublish.yaml)
[![Publish to PyPI](https://github.com/rathaROG/lapx/actions/workflows/publish.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/publish.yaml)

# Linear Assignment Problem Solvers

`lapx` was initially created to maintain Tomas Kazmar's [`lap`](https://github.com/gatagat/lap), but has since evolved to offer much more.  

`lapx` features the original **`lapjv()`** and **`lapmod()`** functions, and since [**v0.6.0**](https://github.com/rathaROG/lapx/releases/tag/v0.6.0), `lapx` has introduced three additional assignment solvers:  
- **`lapjvx()`** and **`lapjvxa()`** — enhanced versions of [`lap.lapjv()`](https://github.com/gatagat/lap) with more flexible output formats  
- **`lapjvc()`** — an enhanced version of Christoph Heindl’s [`lapsolver.solve_dense()`](https://github.com/cheind/py-lapsolver) with unified output formats

`lapx` [**v0.7.0**](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) has introduced a new function: **`lapjvs()`** — an enhanced version of Vadim Markovtsev’s [`lapjv()`](https://github.com/src-d/lapjv), supporting both rectangular and square cost matrices, with flexible output styles.

<details><summary>Read more</summary><br>

All [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solvers in `lapx` are based on Jonker-Volgenant algorithm for dense LAPJV ¹ or sparse LAPMOD ² matrices. Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) implemented the core **`lapjv()`** and **`lapmod()`** from scratch based solely on the papers ¹˒² and the public domain Pascal implementation provided by A. Volgenant ³. 

<sup>¹ R. Jonker and A. Volgenant, "A Shortest Augmenting Path Algorithm for Dense and Sparse Linear Assignment Problems", Computing 38, 325-340 (1987) </sup><br>
<sup>² A. Volgenant, "Linear and Semi-Assignment Problems: A Core Oriented Approach", Computer Ops Res. 23, 917-932 (1996) </sup><br>
<sup>³ http://www.assignmentproblems.com/LAPJV.htm | [[archive.org](https://web.archive.org/web/20220221010749/http://www.assignmentproblems.com/LAPJV.htm)] </sup><br>

</details>

## 💽 Installation

### Install from [PyPI](https://pypi.org/project/lapx/):

[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Downloads](https://static.pepy.tech/badge/lapx)](https://pepy.tech/project/lapx)
[![Downloads](https://static.pepy.tech/badge/lapx/month)](https://pepy.tech/project/lapx)

```
pip install lapx
```

| **Pre-built Wheels** 🛞 | **Windows** ✅ | **Linux** ✅ | **macOS** ✅ |
|:---:|:---:|:---:|:---:|
| Python 3.7 | AMD64 | x86_64/aarch64 | x86_64 |
| Python 3.8 | AMD64 | x86_64/aarch64 | x86_64/arm64 |
| Python 3.9-3.14 ¹`² | AMD64/ARM64 ³ | x86_64/aarch64 | x86_64/arm64 |

<sup>¹ `lapx` v0.5.13+ supports numpy 1.x-2.x and Python 3.14. 🆕 </sup><br>
<sup>² Pre-built wheels for Python 3.13+ do not support free-threading.</sup><br>
<sup>³ Windows ARM64 is experimental.</sup><br>


<details><summary>Other options</summary>

### Install from GitHub repo (Require C++ compiler):

```
pip install git+https://github.com/rathaROG/lapx.git
```

### Build and install (Require C++ compiler):

```
git clone https://github.com/rathaROG/lapx.git
cd lapx
pip install "setuptools>=67.8.0"
pip install wheel build
python -m build --wheel
cd dist
```

</details>

## 🧪 Usage

### 1. The original function ``lapjv()``

The same as `lap`, use `import lap` to import; for example:

```python
import numpy as np, lap

# x, y = lap.lapjv(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, x, y = lap.lapjv(np.random.rand(4, 5), extend_cost=True, return_cost=True)
assignments = np.array([[y[i],i] for i in x if i >= 0])
```

For detailed documentation of **common parameters**, see the docstring in [`lap/__init__.py`](https://github.com/rathaROG/lapx/blob/main/lap/__init__.py).

<details><summary>Need more explanation?</summary>

The function `lapjv()` returns the assignment cost `cost` and two arrays `x` and `y`. If cost matrix `C` has shape NxM, then `x` is a size-N array specifying to which column each row is assigned, and `y` is a size-M array specifying to which row each column is assigned. For example, an output of `x = [1, 0]` indicates that row 0 is assigned to column 1 and row 1 is assigned to column 0. Similarly, an output of `x = [2, 1, 0]` indicates that row 0 is assigned to column 2, row 1 is assigned to column 1, and row 2 is assigned to column 0.

Note that this function *does not* return the assignment matrix (as done by SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) and lapsolver's [`solve dense`](https://github.com/cheind/py-lapsolver)). The assignment matrix can be constructed from `x` as follows:

```python
A = np.zeros((N, M))
for i in range(N):
    A[i, x[i]] = 1
```

Equivalently, we could construct the assignment matrix from `y`:

```python
A = np.zeros((N, M))
for j in range(M):
    A[y[j], j] = 1
```

Finally, note that the outputs are redundant: we can construct `x` from `y`, and vise versa:

```python
x = [np.where(y == i)[0][0] for i in range(N)]
y = [np.where(x == j)[0][0] for j in range(M)]
```

</details>

### 2. The new function ``lapjvx()``

`lapjvx()` basically is `lapjv()`, but it matches the return style of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) with no additional overhead. You can see how it compares to others in the Object Tracking benchmark [here](https://github.com/rathaROG/lapx/blob/main/benchmark.md#-object-tracking).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvx(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvx(np.random.rand(4, 5), extend_cost=True, return_cost=True)
assignments = np.array(list(zip(row_indices, col_indices)))
```

<details><summary>Show <code>lapjvxa()</code></summary>

### 3. The new function ``lapjvxa()``

`lapjvxa()` is essentially the same as `lapjvx()`, but it returns assignments with shape `(K, 2)` directly — no additional or manual post-processing required. `lapjvxa()` is optimized for applications that only need the final assignments and do not require control over the `cost_limit` parameter.

```python
import numpy as np, lap

# assignments = lap.lapjvxa(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, assignments = lap.lapjvxa(np.random.rand(4, 5), extend_cost=True, return_cost=True)
```

</details>

<details><summary>Show <code>lapjvc()</code></summary>

### 4. The new function ``lapjvc()``

`lapjvc()` is an enhanced version of Christoph Heindl's [py-lapsolver](https://github.com/cheind/py-lapsolver). `lapjvc()` is as fast as (if not faster than) other functions when `n=m` (the cost matrix is square), but it is much slower when `n≠m` (the cost matrix is rectangular). This function adopts the return style of `lapjvx()` — the same as SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvc(np.random.rand(4, 5), return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvc(np.random.rand(4, 5), return_cost=True)
assignments = np.array(list(zip(row_indices, col_indices)))
```

</details>

<details><summary>Show <code>lapjvs()</code></summary>

### 5. The new function ``lapjvs()``

`lapjvs()` is an enhanced version of Vadim Markovtsev's [`lapjv`](https://github.com/src-d/lapjv). While `lapjvs()` does not use CPU special instruction sets like the original implementation, it still delivers comparable performance. It natively supports both square and rectangular cost matrices and can produce output either in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) style or `(x, y)` mappings. See the [docstring here](https://github.com/rathaROG/lapx/blob/main/lap/lapjvs.py) for more details.

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvs(np.random.rand(4, 5), return_cost=False, jvx_like=True)
total_cost, row_indices, col_indices = lap.lapjvs(np.random.rand(4, 5), return_cost=True, jvx_like=True)
assignments = np.array(list(zip(row_indices, col_indices)))
```

</details>

<details><summary>Show <code>lapmod()</code></summary>

### 6. The original function ``lapmod()``

For see the [docstring](https://github.com/rathaROG/lapx/blob/8d56b42265a23c3b5a290b1039dacaac70dfe60d/lap/lapmod.py#L275) for details.

```python
import numpy as np, lap, time

n, m = 5000, 5000
cm = np.random.rand(n, m)

t0 = time.time()
c1, x1, y1 = lap.lapjv(cm, return_cost=True)
print(f"lapjv:  cost={c1:.6f}, time={time.time()-t0:.4f}s")

cc, kk, ii = cm.ravel(), np.tile(np.arange(m), n), np.arange(0, n*m+1, m)
t1 = time.time()
c2, x2, y2 = lap.lapmod(n, cc, ii, kk, return_cost=True)
print(f"lapmod: cost={c2:.6f}, time={time.time()-t1:.4f}s")
print("Assignments identical?", (np.all(x1 == x2) and np.all(y1 == y2)))
```

</details>

## 🏆 Quick Benchmark

To run a quick benchmark or see some interesting results, please check [benchmark.md](https://github.com/rathaROG/lapx/blob/main/benchmark.md).

## 📝 License

Please refer to [NOTICE](https://github.com/rathaROG/lapx/blob/main/NOTICE) & [LICENSE](https://github.com/rathaROG/lapx/blob/main/LICENSE).
