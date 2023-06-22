# Linear Assignment Problem Solver

* `lapx` is a customized edition of Tomas Kazmar's [`gatagat/lap`](https://github.com/gatagat/lap).
* License: BSD-2-Clause, see [`LICENSE`](LICENSE).
* Source credit: Tomas Kazmar @[`gatagat`](https://github.com/gatagat).
* `pypi.org` source code: [lap05-0.5.1.tar.gz](https://files.pythonhosted.org/packages/05/71/5531017a60f5028c87ce34514f2b55d35a2999f6c6e587d1f56e6ee78b10/lap05-0.5.1.tar.gz)


## Windows ✅ | Linux ✅ | macOS ✅

* Build passed on all Windows/Linux/macOS with Python 3.9/3.10/3.11 ✅

* Clone and build directly on your machine:

  ```
  git clone https://github.com/rathaROG/lapx.git
  cd lapx
  python -m pip install --upgrade pip
  pip install "setuptools>=67.2.0"
  pip install wheel build
  python -m build --wheel --no-isolation
  cd dist
  ```

* Or install from GitHub directly:

  ```
  python -m pip install --upgrade pip
  pip install "setuptools>=67.2.0"
  pip install wheel build
  pip install git+https://github.com/rathaROG/lapx.git
  ```

<br />

<details><summary><ins>Click here to show more ...</ins></summary>

<br />

lap: Linear Assignment Problem solver
=====================================

**lap** is a [linear assignment
problem](https://en.wikipedia.org/wiki/Assignment_problem) solver using
Jonker-Volgenant algorithm for dense (LAPJV [1]) or sparse (LAPMOD [2])
matrices.

Both algorithms are implemented from scratch based solely on the papers [1,2]
and the public domain Pascal implementation provided by A. Volgenant [3].

In my tests the LAPMOD implementation seems to be faster than the LAPJV
implementation for matrices with a side of more than ~5000 and with less than
50% finite coefficients.

[1] R. Jonker and A. Volgenant, "A Shortest Augmenting Path Algorithm for Dense
and Sparse Linear Assignment Problems", Computing 38, 325-340 (1987)<br>
[2] A. Volgenant, "Linear and Semi-Assignment Problems: A Core Oriented
Approach", Computer Ops Res. 23, 917-932 (1996)<br>
[3] http://www.assignmentproblems.com/LAPJV.htm


### Usage

```
cost, x, y = lap.lapjv(C)
```

The function `lapjv(C)` returns the assignment cost (`cost`) and two arrays, `x, y`. If cost matrix `C` has shape N x M, then `x` is a size-N array specifying to which column is row is assigned, and `y` is a size-M array specifying to which row each column is assigned. For example, an output of `x = [1, 0]` indicates that row 0 is assigned to column 1 and row 1 is assigned to column 0. Similarly, an output of `x = [2, 1, 0]` indicates that row 0 is assigned to column 2, row 1 is assigned to column 1, and row 2 is assigned to column 0.

Note that this function *does not* return the assignment matrix (as done by scipy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linear_sum_assignment.html) and lapsolver's [`solve dense`](https://github.com/cheind/py-lapsolver)). The assignment matrix can be constructed from `x` as follows:
```
A = np.zeros((N, M))
for i in range(N):
    A[i, x[i]] = 1
```
Equivalently, we could construct the assignment matrix from `y`:
```
A = np.zeros((N, M))
for j in range(M):
    A[y[j], j] = 1
```

Finally, note that the outputs are redundant: we can construct `x` from `y`, and vise versa:
```
x = [np.where(y == i)[0][0] for i in range(N)]
y = [np.where(x == j)[0][0] for j in range(M)]
```

</details>