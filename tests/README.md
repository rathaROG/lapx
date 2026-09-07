[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)
[![Full Tests (Plus)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests_plus.yaml)

# Running test suite for `lapx`

These tests are powered by [`pytest`](https://github.com/pytest-dev/pytest) and configured via [`pytest.ini`](https://github.com/rathaROG/lapx/blob/main/tests/pytest.ini).

## Running tests

From [this current directory](https://github.com/rathaROG/lapx/tree/main/tests), you can do as follows:

- Install test dependencies:
  ```bash
  python -m pip install -r test_requirements.txt
  ```

- Run the full test suite:
  ```bash
  python -m pytest -v
  ```

- Run a specific test file; for example, [`test_smoke.py`](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  python -m pytest -v test_smoke.py
  ```

- Run a single test within a test file; for example, [`test_single_matrix_solvers_smoke`](https://github.com/rathaROG/lapx/blob/v0.9.1/tests/test_smoke.py#L137) inside [`test_smoke.py`](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  python -m pytest -v test_smoke.py::test_single_matrix_solvers_smoke
  ```

**Notes**:

- To test a locally built checkout, run `python -m pytest -c tests/pytest.ini -q tests` from the repository root. This uses the local `lap/` package and the same timeout and marker settings as CI. Running from `tests/` can import the installed package instead; it must contain the features being tested.
- Test data such as [`cost_eps.csv.gz`](https://github.com/rathaROG/lapx/blob/main/tests/cost_eps.csv.gz) is included and used by relevant tests; no additional setup is required.
- `test_large_cost_consistency.py` covers billion-scale costs across dense single and batch solvers, both return modes, square and rectangular inputs, JVS precision modes, and threaded batches. It also checks larger deterministic matrices against SciPy and verifies `lapmod`'s existing cost range. The fixed regressions run without SciPy; only the SciPy comparisons require it.
- Run `pytest --help` to see all arguments in `pytest`.

## Test organization

| Area | Files |
| --- | --- |
| Basic API sanity checks | `test_smoke.py` |
| Individual solver behavior | `test_lapjv.py`, `test_lapjvx.py`, `test_lapjvxa_sa.py`, `test_lapmod.py` |
| Shared dense and batch behavior | `test_single_solvers*.py`, `test_batch_solvers*.py` |
| Sparse batches, varying sizes, ordering, and worker errors | `test_lapmod_batch.py` |
| Invalid inputs, precision, empty inputs, and thread reuse | `test_input_contracts.py`, `test_wrapper_stability.py`, `test_native_stability.py` |
| Cost-range and reported-bug regressions | `test_large_cost_consistency.py`, `test_arr_loop.py`, `test_*issue_*.py` |
| Build-option checks without a native compiler | `test_setup.py` |
| Shared test data and conversions | `conftest.py`, `test_utils.py`, `cost_eps.csv.gz` |
| Static return-type checks | `typing/return_cost.py` |

Put new cases in the relevant existing file; use a separate regression file when
it covers a distinct problem across several solvers. Keep shared pytest fixtures
in `conftest.py` and data-generation helpers in `test_utils.py`. Matrix fixtures
have function scope because some tests modify their inputs. The generators use
local random state so they preserve the fixed test data without affecting other
tests.

## Coverage and CI checks

Keep CI checks deterministic and small. `test_input_contracts.py` checks invalid
dimensions, worker-error propagation and recovery, and sparse size limits using
broadcast views. Sparse path-search cases in `test_lapmod.py` exercise the Python
fallback and each native path version against an exhaustive oracle on at most
4x4 matrices (24 permutations). Empty-input tests fail on unexpected exceptions.
Sparse batch tests use similarly small problems and cover both return modes,
native and Python paths, thread counts, shared inputs, and error recovery. The
ordering test coordinates workers with events rather than timing assertions.
Use `pytest -q --durations=10` to spot tests that become expensive; solver speed
benchmarks belong in `benchmarks/`, without timing assertions in the test suite.

Both GitHub test workflows run the full pytest suite.

## Static type checks

This optional developer check validates return-type annotations separately from
the runtime tests. It requires two additional packages, `pyright` and
`typing_extensions`, which are not installed by `test_requirements.txt`.
Install them once per Python environment:

```bash
python -m pip install pyright typing_extensions
```

After changing public type annotations or the static check itself, run this
command from the `tests/` directory:

```bash
pyright typing/return_cost.py
```

From the repository root, use `pyright tests/typing/return_cost.py` instead.
The check covers all public solvers with default, keyword, positional, and
dynamic `return_cost` values. Expected-error cases ensure invalid arguments and
incorrect tuple unpacking remain rejected.

Neither `pytest` nor the current GitHub test workflows run this check
automatically. These tools are not required to use `lapx` or run its pytest
suite. The static check does not execute the solvers or affect their runtime
performance.
