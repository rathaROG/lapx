<details><summary>🆕 What's new</summary><br>

- 2025/10/16: `lapx` [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) introduced **`lapjvx()`**, **`lapjvxa()`**, and **`lapjvc()`**.
- 2025/10/15: Added Python 3.14 support and [more](https://github.com/rathaROG/lapx/pull/15).
- 2024/12/01: The original [`lap`](https://github.com/gatagat/lap) and [`lapx`](https://github.com/rathaROG/lapx) have been merged.

</details>

---

[![Test Simple](https://github.com/rathaROG/lapx/actions/workflows/test_simple.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/test_simple.yaml)
[![Benchmark](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml)
[![Test PyPI Build](https://github.com/rathaROG/lapx/actions/workflows/prepublish.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/prepublish.yaml)
[![Publish to PyPI](https://github.com/rathaROG/lapx/actions/workflows/publish.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/publish.yaml)

# Linear Assignment Problem Solver

`lapx` is an enhanced Tomas Kazmar's [`gatagat/lap`](https://github.com/gatagat/lap) **`lapjv()`** with three additional functions — **`lapjvx()`**, **`lapjvxa()`**, and **`lapjvc()`** — introduced in [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0).

<details><summary>Read more</code></summary><br>

Tomas Kazmar's [`lap`](https://github.com/gatagat/lap) is a [linear assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) solver using Jonker-Volgenant algorithm for dense LAPJV ¹ or sparse LAPMOD ² matrices. Both algorithms are implemented from scratch based solely on the papers ¹˒² and the public domain Pascal implementation provided by A. Volgenant ³. The LAPMOD implementation seems to be faster than the LAPJV implementation for matrices with a side of more than ~5000 and with less than 50% finite coefficients.

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

### 1. The original function ``lap.lapjv(C)``

The same as `lap`, use `import lap` to import; for example:

```python
import lap
import numpy as np

# x, y = lap.lapjv(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, x, y = lap.lapjv(np.random.rand(4, 5), extend_cost=True, return_cost=True)
assignments = np.array([[y[i],i] for i in x if i >= 0])
```

For detailed documentation of **common parameters**, see the docstring in [`lap/__init__.py`](lap/__init__.py).

<details><summary>Need more explanation?</summary>

The function `lapjv(C)` returns the assignment cost `cost` and two arrays `x` and `y`. If cost matrix `C` has shape NxM, then `x` is a size-N array specifying to which column each row is assigned, and `y` is a size-M array specifying to which row each column is assigned. For example, an output of `x = [1, 0]` indicates that row 0 is assigned to column 1 and row 1 is assigned to column 0. Similarly, an output of `x = [2, 1, 0]` indicates that row 0 is assigned to column 2, row 1 is assigned to column 1, and row 2 is assigned to column 0.

Note that this function *does not* return the assignment matrix (as done by scipy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) and lapsolver's [`solve dense`](https://github.com/cheind/py-lapsolver)). The assignment matrix can be constructed from `x` as follows:

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

### 2. The new function ``lap.lapjvx(C)``

This function `lap.lapjvx(C)` basically is `lap.lapjv(C)`, but it matches the return style of [`scipy.optimize.linear_sum_assignment()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

```python
import lap
import numpy as np

# row_indices, col_indices = lap.lapjvx(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvx(np.random.rand(4, 5), extend_cost=True, return_cost=True)
assignments = np.array(list(zip(row_indices, col_indices)))
```

### 3. The new function ``lap.lapjvxa(C)``

This function `lap.lapjvxa(C)` is essentially the same as `lap.lapjvx(C)`, but it returns assignments with shape `(K, 2)` directly — no additional or manual post-processing required. `lap.lapjvxa(C)` is designed for applications like object tracking and similar use cases.

```python
import lap
import numpy as np

# assignments = lap.lapjvxa(np.random.rand(4, 5), extend_cost=True, return_cost=False)
total_cost, assignments = lap.lapjvxa(np.random.rand(4, 5), extend_cost=True, return_cost=True)
```

### 4. The new function ``lap.lapjvc(C)``

This function `lap.lapjvc(C)`, which is the classical implementation of Jonker-Volgenant — [py-lapsolver](https://github.com/cheind/py-lapsolver), is as fast as (if not faster than) other functions when `n=m` (the cost matrix is square), but it is much slower when `n≠m` (the cost matrix is not square). This function adopts the return style of `lap.lapjvx(C)` — the same as [`scipy.optimize.linear_sum_assignment()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

```python
import lap
import numpy as np

# row_indices, col_indices = lap.lapjvc(np.random.rand(4, 5), return_cost=False)
total_cost, row_indices, col_indices = lap.lapjvc(np.random.rand(4, 5), return_cost=True)
assignments = np.array(list(zip(row_indices, col_indices)))
```

## 🏆 Quick Benchmark

To run a quick benchmark or see some interesting results, please check [benchmark.md](benchmark.md).

## 📝 License

Please refer to [NOTICE](NOTICE) & [LICENSE](LICENSE).
