<details><summary>🆕 What's new</summary><hr>

<sup>- 2025/10/31: [v0.9.0](https://github.com/rathaROG/lapx/releases/tag/v0.9.0) delivered a major stability and performance upgrade accross most solvers. 🚀 </sup><br>
<sup>- 2025/10/27: [v0.8.0](https://github.com/rathaROG/lapx/releases/tag/v0.8.0) added **`lapjvx_batch()`**, **`lapjvxa_batch()`**, **`lapjvs_batch()`**, **`lapjvsa_batch()`** and **`lapjvsa()`**. </sup><br>
<sup>- 2025/10/21: [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) added **`lapjvs()`**. </sup><br>
<sup>- 2025/10/16: [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) added **`lapjvx()`**, **`lapjvxa()`**, and **`lapjvc()`**. </sup><br>
<sup>- 2025/10/15: [v0.5.13](https://github.com/rathaROG/lapx/releases/tag/v0.5.13) added Python 3.14 support. </sup><br>
<sup>- Looking for more? See [GitHub releases](https://github.com/rathaROG/lapx/releases). </sup><br>

</details>

---

<div align="center">

[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg?v0.9.1)](https://github.com/rathaROG/lapx/releases)
[![Platforms](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-gold)](https://pypi.org/project/lapx/#files)
[![Python Versions](https://img.shields.io/pypi/pyversions/lapx.svg?v0.9.1)](https://pypi.org/project/lapx/)

[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# Linear Assignment Problem Solvers · 𝕏

**Single ✓ Batch ✓ Square ✓ Rectangular ✓**

</div>

[`lapx`](https://github.com/rathaROG/lapx) was initially created to maintain Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) — a ***Jonker-Volgenant*** solver, but has since evolved to offer much more -> See the [usage section](https://github.com/rathaROG/lapx#-usage) for details on all available solver functions.

<details><summary>Click to read more ...</summary><br>

All [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solvers in `lapx` are based on ***Jonker-Volgenant*** algorithm for dense LAPJV ¹ or sparse LAPMOD ² matrices. Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) implemented the core **`lapjv()`** and **`lapmod()`** from scratch based solely on the papers ¹˒² and the public domain Pascal implementation ³ provided by A. Volgenant. 

<sup>¹ R. Jonker and A. Volgenant, "A Shortest Augmenting Path Algorithm for Dense and Sparse Linear Assignment Problems", Computing 38, 325-340 (1987) </sup><br>
<sup>² A. Volgenant, "Linear and Semi-Assignment Problems: A Core Oriented Approach", Computer Ops Res. 23, 917-932 (1996) </sup><br>
<sup>³ http://www.assignmentproblems.com/LAPJV.htm | [[archive.org](https://web.archive.org/web/20220221010749/http://www.assignmentproblems.com/LAPJV.htm)] </sup><br>

</details>

## 💽 Installation

### Install from [PyPI](https://pypi.org/project/lapx/):

[![Wheels](https://img.shields.io/pypi/wheel/lapx)](https://pypi.org/project/lapx/)
[![PyPI version](https://badge.fury.io/py/lapx.svg?v0.9.1)](https://badge.fury.io/py/lapx)
[![Downloads](https://static.pepy.tech/badge/lapx)](https://pepy.tech/project/lapx)
[![Downloads](https://static.pepy.tech/badge/lapx/month)](https://pepy.tech/project/lapx)

```
pip install lapx
```

*The pre-built wheels cover most platforms and architectures, see [details](https://pypi.org/project/lapx/#files).*

<details><summary>🛠️ Other installation options</summary>

### Install from GitHub repo (Requires C++ compiler):

```
pip install git+https://github.com/rathaROG/lapx.git
```

### Build and install (Requires C++ compiler):

```
git clone https://github.com/rathaROG/lapx.git
cd lapx
pip install "setuptools>=67.8.0"
pip install wheel build
python -m build --wheel
cd dist
```

</details>

<details><summary>⚡ Extra performance</summary><br>

Since [v0.9.1](https://github.com/rathaROG/lapx/releases/tag/v0.9.1), `lapx` enables safe optimizations by default. For source build, you can opt into extra flags via environment variables:
- `LAPX_FASTMATH=1` — enable fast-math (may change floating‑point semantics)
- `LAPX_NATIVE=1` — GCC/Clang only; tune for the CPU of build machine (not suitable for sharing)
- `LAPX_LTO=0` — disable link-time optimization if link time/memory is an issue

See the [setup.py](https://github.com/rathaumons/lapx-test/blob/main/setup.py) for details.
</details>

## 🧪 Usage

[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)

### 🅰️ Single-matrix Solvers 📄

#### 1. The original function ``lapjv()``

The same as `lap`, use `import lap` to import; for example:

```python
import numpy as np, lap

# x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=True)
valid = x >= 0
assignments = np.column_stack((np.arange(len(x))[valid], x[valid]))
# assignments = np.array([[y[i],i] for i in x if i >= 0])  # slower
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

#### 2. The new function ``lapjvx()``

`lapjvx()` basically is `lapjv()`, but it matches the return style of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) with no additional overhead. You can see how it compares to others in the Object Tracking benchmark [here](https://github.com/rathaROG/lapx/blob/main/benchmark.md#-object-tracking).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

<details><summary>Show <code>lapjvxa()</code></summary>

#### 3. The new function ``lapjvxa()``

`lapjvxa()` is essentially the same as `lapjvx()`, but it returns assignments with shape `(K, 2)` directly — no additional or manual post-processing required. `lapjvxa()` is optimized for applications that only need the final assignments and do not require control over the `cost_limit` parameter.

```python
import numpy as np, lap

# assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=True)
```

</details>

<details><summary>Show <code>lapjvc()</code></summary>

#### 4. The new function ``lapjvc()``

`lapjvc()` is an enhanced version of Christoph Heindl's [py-lapsolver](https://github.com/cheind/py-lapsolver). `lapjvc()` is as fast as (if not faster than) other functions when `n=m` (the cost matrix is square), but it is much slower when `n≠m` (the cost matrix is rectangular). This function adopts the return style of `lapjvx()` — the same as SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvc(np.random.rand(100, 150), return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvc(np.random.rand(100, 150), return_cost=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

</details>

<details><summary>Show <code>lapjvs()</code></summary>

#### 5. The new function ``lapjvs()``

`lapjvs()` is an enhanced version of Vadim Markovtsev's [`lapjv`](https://github.com/src-d/lapjv). While `lapjvs()` does not use CPU special instruction sets like the original implementation, it still delivers comparable performance. It natively supports both square and rectangular cost matrices and can produce output either in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) style or `(x, y)` mappings. See the [docstring here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py) for more details.

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvs(np.random.rand(100, 150), return_cost=False, jvx_like=True)
total_cost, row_indices, col_indices = lap.lapjvs(np.random.rand(100, 150), return_cost=True, jvx_like=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

</details>

<details><summary>Show <code>lapjvsa()</code></summary>

#### 6. The new function ``lapjvsa()``

`lapjvsa()` is essentially the same as `lapjvs()`, but it returns assignments with shape `(K, 2)` directly — no additional or manual post-processing required.

```python
import numpy as np, lap

# assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=False)
total_cost, assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=True)
```

</details>

<details><summary>Show <code>lapmod()</code></summary>

#### 7. The original function ``lapmod()``

For see the [`lap/_lapmod_wp.py`](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_wp.py) for details.

```python
import numpy as np, lap, time

n, m = 1000, 1000
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

### 🅱️ Batch Solvers 🗂️

#### 1. The new function ``lapjvx_batch()``

`lapjvx_batch()` is the batch version of [`lapjvx()`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx), accepting costs with shape `(B, N, M)`. See **common parameters** and **return** in [`lap/__init__.py`](https://github.com/rathaROG/lapx/blob/main/lap/__init__.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, rows, cols = lap.lapjvx_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
# access the assignments @ batch b = 7
assignments_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"assignments_7.shape = {assignments_7.shape}")
```

<details><summary>Show <code>lapjvxa_batch()</code></summary>

#### 2. The new function ``lapjvxa_batch()``

`lapjvxa_batch()` is the batch version of [`lapjvxa()`](https://github.com/rathaROG/lapx#3-the-new-function-lapjvxa), accepting costs with shape `(B, N, M)`. See **common parameters** and **return** in [`lap/__init__.py`](https://github.com/rathaROG/lapx/blob/main/lap/__init__.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, assignments = lap.lapjvxa_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
print(f"assignments[7].shape = {assignments[7].shape}")  # assignments @ batch b = 7
```

</details>

<details><summary>Show <code>lapjvs_batch()</code></summary>

#### 3. The new function ``lapjvs_batch()``

`lapjvs_batch()` is the batch version of [`lapjvs()`](https://github.com/rathaROG/lapx#5-the-new-function-lapjvs), accepting costs with shape `(B, N, M)`. See **common parameters** and **return** in [`lap/__init__.py`](https://github.com/rathaROG/lapx/blob/main/lap/__init__.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, rows, cols = lap.lapjvs_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
# access the assignments @ batch b = 7
assignments_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"assignments_7.shape = {assignments_7.shape}")
```

</details>

<details><summary>Show <code>lapjvsa_batch()</code></summary>

#### 4. The new function ``lapjvsa_batch()``

`lapjvsa_batch()` is the batch version of [`lapjvsa()`](https://github.com/rathaROG/lapx#6-the-new-function-lapjvxa), accepting costs with shape `(B, N, M)`. See **common parameters** and **return** in [`lap/__init__.py`](https://github.com/rathaROG/lapx/blob/main/lap/__init__.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, assignments = lap.lapjvsa_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
print(f"assignments[7].shape = {assignments[7].shape}")  # assignments @ batch b = 7
```

</details>

## 🏆 Quick Benchmark

To run a quick benchmark or see some interesting results, please check [benchmark.md](https://github.com/rathaROG/lapx/blob/main/benchmark.md).

## 📝 License

[![NOTICE](https://img.shields.io/badge/NOTICE-Present-blue)](https://github.com/rathaROG/lapx/blob/main/NOTICE)
[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)](https://github.com/rathaROG/lapx/blob/main/LICENSE)
