# Usage

Use this guide for solver examples, cost rules, return formats, and batch processing.
See the [README](https://github.com/rathaROG/lapx/blob/main/README.md#-installation) for installation instructions.

- [Cost values](https://github.com/rathaROG/lapx/blob/main/USAGE.md#cost-values)
- [Numerical precision limits](https://github.com/rathaROG/lapx/blob/main/USAGE.md#numerical-precision-limits)
- [Single-matrix solvers](https://github.com/rathaROG/lapx/blob/main/USAGE.md#single-matrix-solvers)
- [Batch solvers](https://github.com/rathaROG/lapx/blob/main/USAGE.md#batch-solvers)

Install the package as `lapx` and use `import lap`.

<details><summary>Show additional notes</summary><br>

> - Do not install both `lap` and `lapx` at the same time. Both packages provide the import name `lap`.
>   The package that you install last replaces the other package's files.
> - If you only need `lapjv` and `lapmod`, the original `lap` is sufficient.
>   Choose `lapx` for additional fixes, batch processing, output formats, and solvers. It also improves stability and performance.

</details>

<a id="cost-values"></a>

## Cost values

The caller must check cost values for `lapjv`, `lapjvx`, `lapjvxa`, `lapjvs`, `lapjvsa`, `lapjvr`, `lapjvh`, and their batch variants.
These solvers omit this check to reduce overhead for repeated calls.
Before you call these solvers, prepare costs without NaN (not a number) or negative infinity.
Results with these values are undefined. Positive infinity (`np.inf`) can represent a forbidden assignment.

`lapjvc` treats `NaN` and either infinity as forbidden assignments.
`lapmod` checks its sparse arrays. Stored costs must be finite, non-negative, and less than `lap.LARGE`.

With `return_cost=True` (the default), the solvers sum total costs in float64 from the original costs.
This rule also applies when working costs use float32 storage.
Set `return_cost=False` when you need only assignments. This skips the total-cost calculation.

<details><summary>Cost limits and filtering after solving</summary>

`lapjv`, `lapjvx`, `lapjvxa`, `lapjvr`, and `lapjvh` accept `cost_limit`.
The JVX and R/H batch solvers support it too.
The value must be finite or positive infinity. The default `np.inf` applies no finite cost limit.
With a finite limit, the solver considers leaving items unmatched during optimization.
Unmatched rows and columns each incur half the limit during optimization.
Returned totals exclude those penalties.
JV/JVX solvers expand each nonempty `(N, M)` problem to shape `(N+M, N+M)`,
which requires more memory and can slow the solve. R/H handles finite limits without square padding.

Some workflows, such as object tracking, apply a cost threshold after solving.
For this approach, leave `cost_limit=np.inf`. Then remove assignment pairs whose costs exceed the threshold.
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

### Numerical precision limits

Large finite penalties can hide small cost differences during optimization.
Some such inputs give suboptimal assignments in the JV/JVX/JVC/JVS families, even with float64 costs.
The R/H families pass the reproduced cases. Their floating-point arithmetic still cannot guarantee exact assignments for arbitrary cost ranges.

See the [precision regression guide](https://github.com/rathaROG/lapx/blob/main/tests/README.md#precision-cases-from-src-dlapjv-issue-94)
for reproduced cases and solver coverage.

<a id="single-matrix-solvers"></a>

## Single-matrix solvers

### 1. The original function ``lapjv``

`lapjv` supports square and rectangular cost matrices.
It returns optimal assignments as mapping arrays `x` (size N) and `y` (size M).
If `return_cost=True`, it also returns the total cost. See the [API documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjv.pyi) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, x, y = lap.lapjv(cost, extend_cost=True)
valid = x >= 0
pairs = np.column_stack((np.arange(len(x))[valid], x[valid]))
```

`lapjv` returns `(total, x, y)` by default, or `(x, y)` with `return_cost=False`.
For a cost matrix `cost` with shape `(N, M)`, `x` has N entries and `y` has M entries.
`x[i]` gives the assigned column for row i. `y[j]` gives the assigned row for column j.
Unmatched entries are `-1`.

For example, `x = [1, 0]` means row 0 uses column 1 and row 1 uses column 0.
The example above converts mapping arrays to pairs. Use
[`lapjvx`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#2-the-new-function-lapjvx)
for aligned row and column indices, as in SciPy.
See the original `lapjv` documentation at [gatagat/lap](https://github.com/gatagat/lap).

<details><summary>Show <code>lapjvx</code></summary>

### 2. The new function ``lapjvx``

`lapjvx` uses the same algorithm as `lapjv`. It returns aligned row and column indices, as in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
See the [API documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx.pyi) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, rows, cols = lap.lapjvx(cost, extend_cost=True)
pairs = np.column_stack((rows, cols))
```

See the [object tracking benchmark](https://github.com/rathaROG/lapx/blob/main/benchmark.md#-object-tracking) to compare `lapjvx` with other solvers.

</details>

<details><summary>Show <code>lapjvxa</code></summary>

### 3. The new function ``lapjvxa``

`lapjvxa` provides the same solver behavior as `lapjvx`. It returns assignment pairs with shape `(K, 2)`.
The caller does not need to convert the output.
The pair format also suits tracking workflows that apply a cost threshold after solving, as described in [Cost values](https://github.com/rathaROG/lapx/blob/main/USAGE.md#cost-values).
See the [API documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx.pyi) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, pairs = lap.lapjvxa(cost, extend_cost=True)
```

</details>

<details><summary>Show <code>lapjvc</code></summary>

### 4. The new function ``lapjvc``

`lapjvc` extends Christoph Heindl's [py-lapsolver](https://github.com/cheind/py-lapsolver).
It returns the same output format as `lapjvx` and SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
See the [API documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvc.pyi) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, rows, cols = lap.lapjvc(cost)
pairs = np.column_stack((rows, cols))
```

</details>

<details><summary>Show <code>lapjvs</code></summary>

### 5. The new function ``lapjvs``

`lapjvs` extends Vadim Markovtsev's [`lapjv`](https://github.com/src-d/lapjv).
Its scalar kernel does not require AVX2 instructions.
Working costs use float32 by default. Potentials, distances, and reduced-cost
arithmetic use float64. To preserve float64 input costs, pass
`prefer_float32=False` with a float64 array.
It supports square and rectangular cost matrices. It can return either of these output formats:

- Aligned index arrays, as in SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
- Mapping arrays `x` and `y`, as in [`lapjv`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#1-the-original-function-lapjv).

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, rows, cols = lap.lapjvs(cost, jvx_like=True)
pairs = np.column_stack((rows, cols))
```

</details>

<details><summary>Show <code>lapjvsa</code></summary>

### 6. The new function ``lapjvsa``

`lapjvsa` provides the same solver behavior as `lapjvs`. It returns assignment pairs with shape `(K, 2)`.
The caller does not need to convert the output.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_wp.py) for details.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, pairs = lap.lapjvsa(cost)
```

</details>

<details><summary>Show <code>lapmod</code></summary>

### 7. The original function ``lapmod``

See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapmod_wp.py) for details.

```python
import lap
import numpy as np

n = 3
cc = np.array([3.0, 1.0, 1.0, 4.0, 2.0, 1.0])  # Costs grouped by row
ii = np.array([0, 2, 4, 6])  # Row offsets into cc
kk = np.array([0, 1, 0, 2, 1, 2])  # Column indices for each cost
total, x, y = lap.lapmod(n, cc, ii, kk)
```

</details>

### 8. Rust and hybrid functions `lapjvr` and `lapjvh`

Compare R/H with SciPy in the
[recorded LAPX 0.13.0 results](https://github.com/rathaROG/lapx/blob/main/benchmark.md#historical-results-lapx-0130).
These measurements apply to the recorded environment and workloads. Performance depends on the input and solver options.

`lapjvr` and `lapjvh` share a Rust Jonker-Volgenant implementation. For square
problems with infinite `cost_limit`, `lapjvh` uses C++ completion. Both return
aligned row and column indices, like `lapjvx`. Use `output="pairs"` for the
pair layout of `lapjvxa`.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, rows, cols = lap.lapjvr(cost, extend_cost=True)
total, pairs = lap.lapjvh(cost, extend_cost=True, output="pairs")
```

Both support rectangular inputs (`extend_cost=True`), finite `cost_limit`, and
`precision="native"`, `"float32"`, or `"float64"`. Rectangular and finite-limit
problems are solved without square padding. See the
[API guide](https://github.com/rathaROG/lapx/blob/main/src/_lapjvr/README.md)
for full signatures, return types, and precision rules.

All paths use float64 potentials and distances while retaining the selected
cost storage. Finite-limit penalties retain their rounding in the selected
cost precision.
Wider working arithmetic reduces cancellation. Extreme cost ranges can still
hide small objective differences. Cost conversion can also round input values.

If you do not need the other LAPX solvers, you can use the dedicated
[laprust](https://github.com/rathaROG/laprust) (Rust, from `lapjvr`) or
[lapcpp](https://github.com/rathaROG/lapcpp) (C++) package instead. Each provides
the same options through `lapjv` and `lapjv_batch`.

---

<a id="batch-solvers"></a>

## Batch solvers

All batch solvers use the same `n_threads` rules:

- `0` (the default) or `None` selects the CPU count from `os.cpu_count()`, capped by the batch size.
  If the CPU count is unavailable, the solver uses one worker.
- `1` or a negative value runs sequentially.
- Positive values select the worker count. The number of workers cannot exceed the batch size.
- Explicit positive values are not capped by the detected CPU count.
- Empty and single-item batches do not create a thread pool.

### 1. The new function ``lapjvx_batch``

`lapjvx_batch` runs [`lapjvx`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#2-the-new-function-lapjvx) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py) for details.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, rows, cols = lap.lapjvx_batch(batch_costs, extend_cost=True, n_threads=2)
print(f"total costs = {totals.sum()}")
pairs_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"pairs_7.shape = {pairs_7.shape}")
```

<details><summary>Show <code>lapjvxa_batch</code></summary>

### 2. The new function ``lapjvxa_batch``

`lapjvxa_batch` runs [`lapjvxa`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#3-the-new-function-lapjvxa) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvx_batch_wp.py) for details.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, pairs = lap.lapjvxa_batch(batch_costs, extend_cost=True, n_threads=2)
print(f"total costs = {totals.sum()}")
print(f"pairs[7].shape = {pairs[7].shape}")
```

</details>

<details><summary>Show <code>lapjvs_batch</code></summary>

### 3. The new function ``lapjvs_batch``

`lapjvs_batch` runs [`lapjvs`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#5-the-new-function-lapjvs) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py) for details.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, rows, cols = lap.lapjvs_batch(batch_costs, extend_cost=True, n_threads=2)
print(f"total costs = {totals.sum()}")
pairs_7 = np.column_stack((rows[7], cols[7]))  # (K_b, 2)
print(f"pairs_7.shape = {pairs_7.shape}")
```

</details>

<details><summary>Show <code>lapjvsa_batch</code></summary>

### 4. The new function ``lapjvsa_batch``

`lapjvsa_batch` runs [`lapjvsa`](https://github.com/rathaROG/lapx/blob/main/USAGE.md#6-the-new-function-lapjvsa) on a batch of cost matrices with shape `(B, N, M)`.
See the [wrapper documentation](https://github.com/rathaROG/lapx/blob/main/lap/_lapjvs_batch_wp.py) for details.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, pairs = lap.lapjvsa_batch(batch_costs, extend_cost=True, n_threads=2)
print(f"total costs = {totals.sum()}")
print(f"pairs[7].shape = {pairs[7].shape}")
```

</details>

<details><summary>Show <code>lapmod_batch</code></summary>

### 5. The new function ``lapmod_batch``

`lapmod_batch` solves a sequence of sparse `(n, cc, ii, kk)` problems.
It uses the same inputs and checks as `lapmod`. Each problem must be square.
Problem sizes and numbers of stored entries can differ.

Results keep the input order. For problem `b`, `x_list[b]` maps rows to columns and `y_list[b]` maps columns to rows.
Both lists contain the same int32 arrays as the single solver.

```python
import lap
import numpy as np

problems = [
    (2, np.array([1.0, 4.0, 3.0, 2.0]),
     np.array([0, 2, 4]), np.array([0, 1, 0, 1])),
    (3, np.array([4.0, 1.0, 3.0]),
     np.array([0, 1, 2, 3]), np.array([2, 0, 1])),
]
totals, x_list, y_list = lap.lapmod_batch(problems, n_threads=2)
print(totals)  # [3. 8.]
print(x_list[1])  # [2 0 1]

# Skip total-cost calculation when only the mappings are needed.
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

### 6. `lapjvr_batch` and `lapjvh_batch`

`lapjvr_batch` and `lapjvh_batch` run their single-matrix solvers on a batch of
cost matrices with shape `(B, N, M)`. Results keep the input order and use the
same output and precision options as the single-matrix calls.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, rows, cols = lap.lapjvr_batch(batch_costs, extend_cost=True, n_threads=2)
totals, pairs = lap.lapjvh_batch(batch_costs, extend_cost=True, output="pairs", n_threads=2)
```

The `n_threads` rules above apply. Automatic mode may run small workloads
serially. See the [batch API guide](https://github.com/rathaROG/lapx/blob/main/src/_lapjvr/README.md#batch-api)
for return types and native worker details.

## Algorithm background

`lapx` provides [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solvers for dense (LAPJV ¹) and sparse (LAPMOD ²) matrices.
The original `lapjv` and `lapmod` implementations come from Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) project,
based on papers ¹˒² and A. Volgenant's public domain Pascal implementation ³.

<sup>¹ R. Jonker and A. Volgenant, "A Shortest Augmenting Path Algorithm for Dense and Sparse Linear Assignment Problems", Computing 38, 325-340 (1987) </sup><br>
<sup>² A. Volgenant, "Linear and Semi-Assignment Problems: A Core Oriented Approach", Computer Ops Res. 23, 917-932 (1996) </sup><br>
<sup>³ http://www.assignmentproblems.com/LAPJV.htm | [[archive.org](https://web.archive.org/web/20220221010749/http://www.assignmentproblems.com/LAPJV.htm)] </sup><br>
