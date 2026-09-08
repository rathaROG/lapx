[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)
[![Full Tests (Plus)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml)

# Run the test suite for `lapx`

The tests use [`pytest`](https://github.com/pytest-dev/pytest). The [pytest.ini file](https://github.com/rathaROG/lapx/blob/main/tests/pytest.ini) sets the test options.

## Run tests

Run these commands from the [tests directory](https://github.com/rathaROG/lapx/tree/main/tests):

- Install test dependencies:
  ```bash
  python -m pip install -r test_requirements.txt
  ```

- Run the full test suite:
  ```bash
  python -m pytest -v
  ```

- To run one test file, use its name. This example runs [test_smoke.py](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  python -m pytest -v test_smoke.py
  ```

- To run one test function, use the file name and function name.
  This example runs [test_single_matrix_solvers_smoke](https://github.com/rathaROG/lapx/blob/v0.9.1/tests/test_smoke.py#L137) in [test_smoke.py](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  python -m pytest -v test_smoke.py::test_single_matrix_solvers_smoke
  ```

**Notes**:

- To test a local build, run `python -m pytest -c tests/pytest.ini -q tests` from the repository root.
  This command uses the local `lap/` package. It uses the same timeout and marker settings as continuous integration (CI).
  Tests that run from `tests/` can import the installed package instead. That package must contain the features under test.
- The repository includes test data such as [cost_eps.csv.gz](https://github.com/rathaROG/lapx/blob/main/tests/cost_eps.csv.gz).
  Tests use these files without additional setup.
- `test_large_cost_consistency.py` checks costs in the billions. Its cases cover:

  - Dense single and batch solvers, with both return modes.
  - Square and rectangular inputs.
  - JVS precision modes and batches that use threads.
  - Larger deterministic matrices, with SciPy as the reference.
  - The existing cost range of `lapmod`.

  Only the SciPy comparisons require SciPy. The fixed regression cases run without it.
- Run `pytest --help` to see all arguments in `pytest`.

## Test organization

| Area | Files |
| --- | --- |
| Basic API sanity checks | `test_smoke.py` |
| Individual solver behavior | `test_lapjv.py`, `test_lapjvx.py`, `test_lapjvxa_sa.py`, `test_lapmod.py` |
| Shared dense and batch behavior | `test_single_solvers*.py`, `test_batch_solvers*.py` |
| Thread-count normalization and pool usage across all batch solvers | `test_batch_threads.py` |
| Sparse batches, varying sizes, ordering, and worker errors | `test_lapmod_batch.py` |
| Invalid inputs, precision, empty inputs, and thread reuse | `test_input_contracts.py`, `test_wrapper_stability.py`, `test_native_stability.py` |
| Cost-range and reported-bug regressions | `test_large_cost_consistency.py`, `test_arr_loop.py`, `test_*issue_*.py` |
| Build-option checks without a native compiler | `test_setup.py` |
| Shared test data and conversions | `conftest.py`, `test_utils.py`, `cost_eps.csv.gz` |
| Static return-type checks | `typing/return_cost.py` |

Add new cases to the relevant existing file.
Use a separate regression file for a distinct problem that affects several solvers.
Keep shared pytest fixtures in `conftest.py`. Keep helpers that generate data in `test_utils.py`.

Matrix fixtures have function scope because some tests change their inputs.
The generators use local random state. This preserves the fixed test data without changes to other tests.

## Coverage and CI checks

Keep CI checks deterministic and small.
`test_input_contracts.py` checks invalid dimensions, exceptions from workers, and recovery after errors.
It uses broadcast views to check sparse size limits.
Empty-input tests fail if they encounter unexpected exceptions.

The sparse path-search cases in `test_lapmod.py` check the Python solver and each native path version.
They compare results with every possible assignment on matrices no larger than 4x4 (24 permutations).

Sparse batch tests use similarly small problems. They cover both return modes, native and Python solvers, thread counts, shared inputs, and error recovery.
The test for result order coordinates workers with events. It does not use timing assertions.

Use `pytest -q --durations=10` to find slow tests.
Keep solver speed benchmarks in `benchmarks/`. Do not add timing assertions to the test suite.

Both GitHub test workflows run the full pytest suite.

## Static type checks

This optional developer tool checks return-type annotations separately from the runtime tests.
It requires two additional packages: `pyright` and `typing_extensions`.
The `test_requirements.txt` file does not install these packages.
Install them once per Python environment:

```bash
python -m pip install pyright typing_extensions
```

After you change public type annotations or the static check, run this command from the `tests/` directory:

```bash
pyright typing/return_cost.py
```

From the repository root, use `pyright tests/typing/return_cost.py` instead.
The check covers all public solvers with default, keyword, positional, and dynamic `return_cost` values.
Cases that expect errors check that the type checker still rejects invalid arguments and incorrect tuple unpacking.

Neither `pytest` nor the current GitHub test workflows run this check automatically.
You do not need these additional packages to use `lapx` or run its pytest suite.
The static check does not execute the solvers or affect their runtime performance.
