<details><summary>🆕 What's new</summary><hr>

> <sup>- 2026/09/07: [v0.10.0rc1](https://github.com/rathaROG/lapx/releases/tag/v0.10.0rc1) added Python 3.15 support and `lapmod_batch`. It improved type hints, stability, and performance. </sup><br>
> <sup>- 2025/10/31: [v0.9.0](https://github.com/rathaROG/lapx/releases/tag/v0.9.0) improved stability and performance across all solvers. </sup><br>
> <sup>- 2025/10/27: [v0.8.0](https://github.com/rathaROG/lapx/releases/tag/v0.8.0) added **`lapjvx_batch`**, **`lapjvxa_batch`**, **`lapjvs_batch`**, **`lapjvsa_batch`** and **`lapjvsa`**. </sup><br>
> <sup>- 2025/10/21: [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) added **`lapjvs`**. </sup><br>
> <sup>- 2025/10/16: [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) added **`lapjvx`**, **`lapjvxa`**, and **`lapjvc`**. </sup><br>
> <sup>- See [GitHub releases](https://github.com/rathaROG/lapx/releases) for all release notes. </sup><br>

</details>

---

<div align="center">

[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg?logo=github&logoColor=lightgray)](https://github.com/rathaROG/lapx/releases)
[![Platforms](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-gold?logo=pypi&logoColor=deepskyblue)](https://pypi.org/project/lapx/#files)
[![Python Versions](https://img.shields.io/pypi/pyversions/lapx.svg?logo=python&logoColor=gold)](https://pypi.org/project/lapx/)

# Linear Assignment Problem Solvers · 𝕏

**Single ✓ Batch ✓ Square ✓ Rectangular ✓**

</div>

[`lapx`](https://github.com/rathaROG/lapx) started as a project to maintain Tomas Kazmar's [`lap`](https://github.com/gatagat/lap), a Jonker-Volgenant solver package.
It now provides additional solver functions. See the [usage section](https://github.com/rathaROG/lapx#-usage) for all available functions.

<details><summary>Read the algorithm background</summary><br>

All [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solvers in `lapx` use the Jonker-Volgenant algorithm for dense matrices (LAPJV ¹) or sparse matrices (LAPMOD ²).
Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) project wrote the core `lapjv` and `lapmod` implementations from the beginning.
The project used only papers ¹˒² and A. Volgenant's public domain Pascal implementation ³ as sources.

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

The available wheels cover most platforms and architectures. See the [package files](https://pypi.org/project/lapx/#files) for details.

<details><summary>🛠️ Other installation options</summary>

### Install from GitHub (requires a C++ compiler):

```
pip install git+https://github.com/rathaROG/lapx.git
```

### Build and install (requires a C++ compiler):

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

> Since [v0.9.1](https://github.com/rathaROG/lapx/releases/tag/v0.9.1), `lapx` enables safe base optimizations by default.
> For source builds, environment variables control these optimizations and optional compiler flags. The optional flags might improve performance:
>
> - `LAPX_BASEOPTS=0` disables the base optimization flags that LAPX adds and link-time optimization (LTO).
>   Other compiler defaults may still apply. This switch is available since [v0.9.2](https://github.com/rathaROG/lapx/releases/tag/v0.9.2).
> - `LAPX_FASTMATH=1` enables fast-math. This option may change numerical results and the treatment of NaN or infinity.
> - `LAPX_NATIVE=1` tunes GCC or Clang output for the CPU of the build machine. Do not distribute these builds.
> - `LAPX_LTO=0` disables LTO, including inherited LTO defaults.
>
> The build enables LTO by default when the compiler and linker support it.
> `LAPX_BASEOPTS=0` does not guarantee an unoptimized or debug build.
> Fast-math and native tuning are independent options. Both options are disabled by default.
> Keep both options disabled for portable release wheels.

> See [setup.py](https://github.com/rathaROG/lapx/blob/main/setup.py) for more details.

</details>

## 🧪 Usage

[`lapx`](https://github.com/rathaROG/lapx) started as a compatible replacement to preserve the distribution of the original [`lap`](https://github.com/gatagat/lap).
The package name is `lapx`. The import name remains `lap` for compatibility with existing code.
Use `import lap` to import `lapx`.

<details><summary>Show additional notes</summary><br>

> ***Notes:***
> - Do not install both `lap` and `lapx` at the same time. Both packages provide the import name `lap`.
>   The package that you install last replaces the other package's files.
> - If you only need `lapjv` and `lapmod`, the original `lap` is sufficient.
>   Choose `lapx` for additional fixes, batch processing, output formats, and solvers. It also improves stability and performance.

</details>

<a id="cost-values"></a>

### ℹ️ Cost values

The caller must check cost values for `lapjv`, `lapjvx`, `lapjvxa`, `lapjvs`, `lapjvsa`, and their batch variants.
These solvers omit this check to reduce overhead for repeated calls.
Before you call these solvers, prepare costs without NaN (not a number) or negative infinity.
Results with these values are undefined. Positive infinity (`np.inf`) can represent a forbidden assignment.

`lapjvc` treats NaN and either infinity as forbidden assignments.
`lapmod` checks its sparse arrays. Stored costs must be finite, non-negative, and less than `lap.LARGE`.

With `return_cost=True`, the solvers sum total costs in float64 from the original costs, even when they solve in float32.
Set `return_cost=False` when you need only assignments. This skips the total-cost calculation.

<details><summary>Cost limits and filtering after solving</summary>

`lapjv`, `lapjvx`, and `lapjvxa` accept `cost_limit`, as do `lapjvx_batch` and `lapjvxa_batch`.
The value must be finite or positive infinity. The default `np.inf` applies no finite cost limit.
With a finite limit, the solver considers leaving items unmatched during optimization.
For each nonempty `(N, M)` problem, this expands the working matrix to shape `(N+M, N+M)`.
The larger matrix requires more memory and can slow the solve.

Some workflows, such as object tracking, apply a cost threshold after solving.
For this approach, leave `cost_limit=np.inf`. Then remove assignment pairs whose costs exceed the threshold.
This avoids the matrix expansion for a finite limit.
Filtering after the solve can produce different assignments from using `cost_limit`.
It removes pairs without solving again, so it cannot replace discarded matches.

</details>

<details><summary>Terms used in the examples</summary>

- A cost matrix contains the cost of each possible assignment from a row to a column.
- A mapping array gives the assigned index for each row or column.
- An assignment pair contains a row index and its assigned column index.
- `B` is the batch size. `N` and `M` are the matrix dimensions. `K` is the number of assignment pairs.
- A dtype is an array's data type, such as float32 or float64.
- The global interpreter lock (GIL) limits concurrent execution of Python code within one interpreter.

</details>

### 🅰️ Single-matrix Solvers 📄

#### 1. The original function ``lapjv``

`lapjv` supports square and rectangular cost matrices.
It returns optimal assignments as mapping arrays `x` (size N) and `y` (size M).
If `return_cost=True`, it also returns the total cost. See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjv_wp.py) for details.

```python
import numpy as np, lap

# x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, x, y = lap.lapjv(np.random.rand(100, 150), extend_cost=True, return_cost=True)
valid = x >= 0
assignments = np.column_stack((np.arange(len(x))[valid], x[valid]))
# assignments = np.array([[y[i],i] for i in x if i >= 0])  # slower
```

<details><summary>Read about mapping arrays</summary><br>

`lapjv(C)` returns the arrays `x` and `y`. If `return_cost=True`, it also returns the total assignment cost.
For a cost matrix `C` with shape `(N, M)`, `x` has N entries and `y` has M entries.
`x[i]` gives the assigned column for row i. `y[j]` gives the assigned row for column j.

For example, `x = [1, 0]` describes these assignments:

- Row 0 uses column 1.
- Row 1 uses column 0.

For `x = [2, 1, 0]`, the assignments are:

- Row 0 uses column 2.
- Row 1 uses column 1.
- Row 2 uses column 0.

> ***Notes:*** 
> - This function returns mapping arrays. SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) returns two aligned index arrays.
>   Use the example above to convert mapping arrays to assignment pairs.
>   Use [`lapjvx`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) for the SciPy output format.
> - See the original documentation of `lapjv` at [gatagat/lap](https://github.com/gatagat/lap).

</details>

#### 2. The new function ``lapjvx``

`lapjvx` uses the same algorithm as `lapjv`. It returns the output format of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) with no additional overhead.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_wp.py) for details.

```python
import numpy as np, lap

# row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvx(np.random.rand(100, 150), extend_cost=True, return_cost=True)
assignments = np.column_stack((row_indices, col_indices))
# assignments = np.array(list(zip(row_indices, col_indices)))  # slower
```

See the [object tracking benchmark](https://github.com/rathaROG/lapx/blob/main/benchmark.md#-object-tracking) to compare `lapjvx` with other solvers.

<details><summary>Show <code>lapjvxa</code></summary>

#### 3. The new function ``lapjvxa``

`lapjvxa` provides the same solver behavior as `lapjvx`. It returns assignment pairs with shape `(K, 2)`.
The caller does not need to convert the output.
The pair format also suits tracking workflows that apply a cost threshold after solving, as described in [Cost values](#cost-values).
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_wp.py) for details.

```python
import numpy as np, lap

# assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=False)
total_cost, assignments = lap.lapjvxa(np.random.rand(100, 150), extend_cost=True, return_cost=True)
```

</details>

<details><summary>Show <code>lapjvc</code></summary>

#### 4. The new function ``lapjvc``

`lapjvc` extends Christoph Heindl's [py-lapsolver](https://github.com/cheind/py-lapsolver).
For square cost matrices, `lapjvc` is as fast as other functions or faster. For rectangular cost matrices, it is much slower.
It returns the same output format as `lapjvx` and SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvc_wp.py) for details.

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

`lapjvs` extends Vadim Markovtsev's [`lapjv`](https://github.com/src-d/lapjv).
It provides comparable performance without the special CPU instruction sets that the original implementation uses.
It supports square and rectangular cost matrices. It can return either of these output formats:

- Aligned index arrays, as in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
- Mapping arrays `x` and `y`, as in [`lapjv`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv).

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py) for details.

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

`lapjvsa` provides the same solver behavior as `lapjvs`. It returns assignment pairs with shape `(K, 2)`.
The caller does not need to convert the output.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py) for details.

```python
import numpy as np, lap

# assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=False)
total_cost, assignments = lap.lapjvsa(np.random.rand(100, 150), return_cost=True)
```

</details>

<details><summary>Show <code>lapmod</code></summary>

#### 7. The original function ``lapmod``

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_wp.py) for details.

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

All batch solvers use the same `n_threads` rules:

- `0` (the default) or `None` selects the CPU count from `os.cpu_count()`.
  If the CPU count is unavailable, the solver uses one worker.
- `1` or a negative value runs sequentially.
- Positive values select the worker count. The number of workers cannot exceed the batch size.
- Empty and single-item batches do not create a thread pool.

#### 1. The new function ``lapjvx_batch``

`lapjvx_batch` runs [`lapjvx`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py) for details.

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

`lapjvxa_batch` runs [`lapjvxa`](https://github.com/rathaROG/lapx#3-the-new-function-lapjvxa) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py) for details.

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

`lapjvs_batch` runs [`lapjvs`](https://github.com/rathaROG/lapx#5-the-new-function-lapjvs) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py) for details.

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

`lapjvsa_batch` runs [`lapjvsa`](https://github.com/rathaROG/lapx#6-the-new-function-lapjvsa) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py) for details.

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

`lapmod_batch` solves a sequence of sparse `(n, cc, ii, kk)` problems.
It uses the same inputs and checks as `lapmod`. Each problem must be square.
Problem sizes and numbers of stored entries can differ.

Results keep the input order. For problem `b`, `x_list[b]` maps rows to columns and `y_list[b]` maps columns to rows.
Both lists contain the same int32 arrays as the single solver.

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

With the default `fast=True`, the native solver releases the GIL. Independent problems can then run concurrently.
Python code that checks inputs and calculates total costs can limit speedup.
With `fast=False`, the Python solver's performance depends largely on the GIL.
`fp_version` selects the native path-search version, as in `lapmod`.

Do not change input arrays while the solver runs.
If a problem raises an exception, the caller receives it after the thread pool stops.

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_batch_wp.py)
for the full signature and return types.

</details>

## 🏆 Benchmark and Test

[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)
[![Full Tests (Plus)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml)

See the [benchmark guide](https://github.com/rathaROG/lapx/blob/main/benchmark.md) for commands and results.

See the [test guide](https://github.com/rathaROG/lapx/tree/main/tests) to run the full test suite.

## 📝 License

[![NOTICE](https://img.shields.io/badge/NOTICE-Present-blue)](https://github.com/rathaROG/lapx/blob/main/NOTICE)
[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)](https://github.com/rathaROG/lapx/blob/main/LICENSE)
