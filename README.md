<details><summary>🆕 What's new</summary><hr>

> <sup>- 2026/09/07: [v0.10.0rc1](https://github.com/rathaROG/lapx/releases/tag/v0.10.0rc1) added Python 3.15 support and `lapmod_batch`, with improved type hints, stability, and performance. 🚀 </sup><br>
> <sup>- 2025/10/31: [v0.9.0](https://github.com/rathaROG/lapx/releases/tag/v0.9.0) delivered a major stability and performance upgrade across ~~most~~ all solvers. </sup><br>
> <sup>- 2025/10/27: [v0.8.0](https://github.com/rathaROG/lapx/releases/tag/v0.8.0) added **`lapjvx_batch`**, **`lapjvxa_batch`**, **`lapjvs_batch`**, **`lapjvsa_batch`** and **`lapjvsa`**. </sup><br>
> <sup>- 2025/10/21: [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) added **`lapjvs`**. </sup><br>
> <sup>- 2025/10/16: [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) added **`lapjvx`**, **`lapjvxa`**, and **`lapjvc`**. </sup><br>
> <sup>- Looking for more? See [GitHub releases](https://github.com/rathaROG/lapx/releases). </sup><br>

</details>

---

<div align="center">

[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg?logo=github&logoColor=lightgray)](https://github.com/rathaROG/lapx/releases)
[![Platforms](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-gold?logo=pypi&logoColor=deepskyblue)](https://pypi.org/project/lapx/#files)
[![Python Versions](https://img.shields.io/pypi/pyversions/lapx.svg?logo=python&logoColor=gold)](https://pypi.org/project/lapx/)

# Linear Assignment Problem Solvers · 𝕏

**Single ✓ Batch ✓ Square ✓ Rectangular ✓**

</div>

[`lapx`](https://github.com/rathaROG/lapx) was initially created to maintain Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) — a ***Jonker-Volgenant*** solver package, but has since evolved to offer much more; for details on all available solver functions, refer to the [usage section](https://github.com/rathaROG/lapx#-usage).

<details><summary>Click to read more ...</summary><br>

All [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solvers in `lapx` are based on ***Jonker-Volgenant*** algorithm for dense LAPJV ¹ or sparse LAPMOD ² matrices. Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) implemented the core **`lapjv`** and **`lapmod`** from scratch based solely on the papers ¹˒² and the public domain Pascal implementation ³ provided by A. Volgenant.

<sup>¹ R. Jonker and A. Volgenant, "A Shortest Augmenting Path Algorithm for Dense and Sparse Linear Assignment Problems", Computing 38, 325-340 (1987) </sup><br>
<sup>² A. Volgenant, "Linear and Semi-Assignment Problems: A Core Oriented Approach", Computer Ops Res. 23, 917-932 (1996) </sup><br>
<sup>³ http://www.assignmentproblems.com/LAPJV.htm | [[archive.org](https://web.archive.org/web/20220221010749/http://www.assignmentproblems.com/LAPJV.htm)] </sup><br>

</details>

## 💽 Installation

### Install from [PyPI](https://pypi.org/project/lapx/):

[![Wheels](https://img.shields.io/pypi/wheel/lapx)](https://pypi.org/project/lapx/)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
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

> Since [v0.9.1](https://github.com/rathaROG/lapx/releases/tag/v0.9.1), `lapx` enables safe (base) optimizations by default. For source builds, you can disable LAPX-added base optimizations or opt into extra flags via environment variables which might boost performance further:
> - `LAPX_BASEOPTS=0` — disables LAPX-added base optimization flags and LTO; other compiler defaults may still apply (switch available since [v0.9.2](https://github.com/rathaROG/lapx/releases/tag/v0.9.2))
> - `LAPX_FASTMATH=1` — enables fast-math (may change numerical results and handling of NaN/infinity)
> - `LAPX_NATIVE=1` — GCC/Clang only; tune for the CPU of the build machine (not suitable for sharing)
> - `LAPX_LTO=0` — disables link-time optimization, including inherited LTO defaults
>
> LTO is enabled by default when compilation and linking support it. `LAPX_BASEOPTS=0` does not guarantee an unoptimized or debug build. Fast-math and native tuning are independent opt-ins, disabled by default; keep both disabled for portable release wheels.

> See the [setup.py](https://github.com/rathaROG/lapx/blob/main/setup.py) for more details.

</details>

## 🧪 Usage

[`lapx`](https://github.com/rathaROG/lapx) was initially created as a drop‑in replacement to preserve the distribution of the original [`lap`](https://github.com/gatagat/lap). While the package you install is `lapx`, the import name remains `lap` to avoid breaking existing code; use `import lap` to import `lapx`.

<details><summary>Show additional notes</summary><br>

> ***Notes:***
> - Do not install both `lap` and `lapx` at the same time; since both provide the same import name (`lap`), the one installed last will override the other.
> - If you only need `lapjv` and `lapmod`, the original `lap` is sufficient; choose `lapx` if you want additional fixes, extended features (batch processing, flexible outputs, extra solvers), and—most importantly—improved stability and performance.

</details>

### ℹ️ Cost values

`lapjv`, `lapjvx`, `lapjvxa`, `lapjvs`, `lapjvsa`, and their batch variants leave cost-value validation to the caller to keep repeated assignment calls lightweight. Prepare costs without NaN or negative infinity before calling these solvers; results with those values are undefined. Positive infinity (`np.inf`) can represent a forbidden assignment.

`lapjvc` treats NaN and either infinity as forbidden assignments. `lapmod` validates its sparse arrays and requires the stored costs to be finite, non-negative, and less than `lap.LARGE`.

Where available, `cost_limit` accepts a finite number or positive infinity. Returned total costs are accumulated in float64 from the original costs, including when the solver works in float32.

### 🅰️ Single-matrix Solvers 📄

#### 1. The original function ``lapjv``

`lapjv` supports both square and rectangular cost matrices. It returns the optimal assignments as mapping arrays `x` (size N) and `y` (size M) and optionally total cost if `return_cost=True`. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjv_wp.py).

```python
import numpy as np, lap

# x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=True)
valid = x >= 0
assignments = np.column_stack((np.arange(len(x))[valid], x[valid]))
# assignments = np.array([[y[i],i] for i in x if i >= 0])  # slower
```

<details><summary>Still need more explanation?</summary><br>

`lapjv(C)` returns two arrays `x` and `y` (also the total assignment cost if `return_cost=True`). If cost matrix `C` has shape NxM, then `x` is a size-N array specifying to which column each row is assigned, and `y` is a size-M array specifying to which row each column is assigned. For example, an output of `x = [1, 0]` indicates that row 0 is assigned to column 1 and row 1 is assigned to column 0. Similarly, an output of `x = [2, 1, 0]` indicates that row 0 is assigned to column 2, row 1 is assigned to column 1, and row 2 is assigned to column 0.

> ***Notes:*** 
> - This function *does not* return two aligned index arrays as SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) does; the final assignments can be done as shown in the example above; use [`lapjvx`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) for SciPy-style output.
> - See the original documentation of `lapjv` at [gatagat/lap](https://github.com/gatagat/lap).

</details>

#### 2. The new function ``lapjvx``

`lapjvx` basically is `lapjv`, but it matches the output style of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) with no additional overhead. See more details of `lapjvx` [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_wp.py).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

See how `lapjvx` compares to others in ***Object Tracking benchmark*** [here](https://github.com/rathaROG/lapx/blob/main/benchmark.md#-object-tracking).

<details><summary>Show <code>lapjvxa</code></summary>

#### 3. The new function ``lapjvxa``

`lapjvxa` is essentially the same as `lapjvx`, but it returns assignments with shape `(K, 2)` directly — no additional/manual post-processing required. `lapjvxa` is optimized for applications that only need the final assignments and do not require control over the `cost_limit` parameter. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_wp.py).

```python
import numpy as np, lap

# assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=True)
```

</details>

<details><summary>Show <code>lapjvc</code></summary>

#### 4. The new function ``lapjvc``

`lapjvc` is an enhanced version of Christoph Heindl's [py-lapsolver](https://github.com/cheind/py-lapsolver). `lapjvc` is as fast as (if not faster than) other functions when the cost matrix is square, but it is much slower when the cost matrix is rectangular. This function adopts the output style of `lapjvx` — the same as SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html). See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvc_wp.py).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvc(np.random.rand(100, 150), return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvc(np.random.rand(100, 150), return_cost=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

</details>

<details><summary>Show <code>lapjvs</code></summary>

#### 5. The new function ``lapjvs``

`lapjvs` is an enhanced version of Vadim Markovtsev's [`lapjv`](https://github.com/src-d/lapjv). While `lapjvs` does not use CPU special instruction sets like the original implementation, it still delivers comparable performance. It natively supports both square and rectangular cost matrices and can produce output either in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) style or mapping arrays `x` and `y` like [`lapjv`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv). See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py).

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvs(np.random.rand(100, 150), return_cost=False, jvx_like=True)
total_cost, row_indices, col_indices = lap.lapjvs(np.random.rand(100, 150), return_cost=True, jvx_like=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

</details>

<details><summary>Show <code>lapjvsa</code></summary>

#### 6. The new function ``lapjvsa``

`lapjvsa` is essentially the same as `lapjvs`, but it returns assignments with shape `(K, 2)` directly — no additional/manual post-processing required. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py).

```python
import numpy as np, lap

# assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=False)
total_cost, assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=True)
```

</details>

<details><summary>Show <code>lapmod</code></summary>

#### 7. The original function ``lapmod``

See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_wp.py).

```python
import numpy as np, lap, time

n, m = 1000, 1000
cm = np.random.rand(n, m)

t0 = time.time()
c1, x1, y1 = lap.lapjv(cm, return_cost=True)
print(f"lapjv: cost={c1:.6f}, time={time.time()-t0:.4f}s")

cc, kk, ii = cm.ravel(), np.tile(np.arange(m), n), np.arange(0, n*m+1, m)
t1 = time.time()
c2, x2, y2 = lap.lapmod(n, cc, ii, kk, return_cost=True)
print(f"lapmod: cost={c2:.6f}, time={time.time()-t1:.4f}s")
print("Assignments identical?", (np.all(x1 == x2) and np.all(y1 == y2)))
```

</details>

### 🅱️ Batch Solvers 🗂️

#### 1. The new function ``lapjvx_batch``

`lapjvx_batch` is the batch version of [`lapjvx`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx), accepting costs with shape `(B, N, M)`. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, rows, cols = lap.lapjvx_batch(batch_costs, extend_cost=True, return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
# access the assignments @ batch b = 7
assignments_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"assignments_7.shape = {assignments_7.shape}")
```

<details><summary>Show <code>lapjvxa_batch</code></summary>

#### 2. The new function ``lapjvxa_batch``

`lapjvxa_batch` is the batch version of [`lapjvxa`](https://github.com/rathaROG/lapx#3-the-new-function-lapjvxa), accepting costs with shape `(B, N, M)`. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, assignments = lap.lapjvxa_batch(batch_costs, extend_cost=True, return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
print(f"assignments[7].shape = {assignments[7].shape}")  # assignments @ batch b = 7
```

</details>

<details><summary>Show <code>lapjvs_batch</code></summary>

#### 3. The new function ``lapjvs_batch``

`lapjvs_batch` is the batch version of [`lapjvs`](https://github.com/rathaROG/lapx#5-the-new-function-lapjvs), accepting costs with shape `(B, N, M)`. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, rows, cols = lap.lapjvs_batch(batch_costs, extend_cost=True, return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
# access the assignments @ batch b = 7
assignments_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"assignments_7.shape = {assignments_7.shape}")
```

</details>

<details><summary>Show <code>lapjvsa_batch</code></summary>

#### 4. The new function ``lapjvsa_batch``

`lapjvsa_batch` is the batch version of [`lapjvsa`](https://github.com/rathaROG/lapx#6-the-new-function-lapjvsa), accepting costs with shape `(B, N, M)`. See more details [here](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py).

```python
import numpy as np, lap, os

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M) # B is batch size
costs, assignments = lap.lapjvsa_batch(batch_costs, extend_cost=True, return_cost=True, n_threads=os.cpu_count())
print(f"total costs = {costs.sum()}")
print(f"assignments[7].shape = {assignments[7].shape}")  # assignments @ batch b = 7
```

</details>

<details><summary>Show <code>lapmod_batch</code></summary>

#### 5. The new function ``lapmod_batch``

`lapmod_batch` solves a sequence of sparse `(n, cc, ii, kk)` problems using the
same inputs and validation as `lapmod`. Each problem must be square, but sizes
and numbers of stored entries can differ. Results retain input order:
`x_list[b]` maps rows to columns and `y_list[b]` maps columns to rows for problem
`b`, with the same int32 arrays as the single solver.

```python
import numpy as np
import lap

problems = [
    (2, np.array([1., 4., 3., 2.]),
     np.array([0, 2, 4]), np.array([0, 1, 0, 1])),
    (3, np.array([4., 1., 3.]),
     np.array([0, 1, 2, 3]), np.array([2, 0, 1])),
]
totals, x_list, y_list = lap.lapmod_batch(problems, n_threads=2)
print(totals)     # [3. 8.]
print(x_list[1])  # [2 0 1]

# Skip total-cost calculation when only the assignments are needed.
x_list, y_list = lap.lapmod_batch(problems, return_cost=False, n_threads=2)
```

`n_threads=0` or `None` uses the CPU count, capped to the batch size; `n_threads=1`
runs sequentially. Empty and single-item batches do not create a thread pool.
The default `fast=True` releases the GIL in the native solver so independent
problems can run concurrently. Python-side validation and total-cost calculation
can limit speedup; the `fast=False` Python fallback is largely GIL-bound.
`fp_version` selects the native path-search version, as in `lapmod`.
Keep input arrays unchanged while solving. Errors from an individual problem
propagate to the caller after the pool shuts down.

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_batch_wp.py)
for the full signature and return types.

</details>

## 🏆 Benchmark and Test

[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)
[![Full Tests (Plus)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml)

To run a quick benchmark or see some interesting results, please check [here](https://github.com/rathaROG/lapx/blob/main/benchmark.md).

To run a full test suite, please check [here](https://github.com/rathaROG/lapx/tree/main/tests).

## 📝 License

[![NOTICE](https://img.shields.io/badge/NOTICE-Present-blue)](https://github.com/rathaROG/lapx/blob/main/NOTICE)
[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)](https://github.com/rathaROG/lapx/blob/main/LICENSE)
