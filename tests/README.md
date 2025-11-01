[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg?v0.9.1)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg?v0.9.1)](https://badge.fury.io/py/lapx)
[![Full Tests](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/tests.yaml)

# Running test suite for `lapx`

These tests are powered by [`pytest`](https://github.com/pytest-dev/pytest) and configured via [`pytest.ini`](https://github.com/rathaROG/lapx/blob/main/tests/pytest.ini).

From [this current directory](https://github.com/rathaROG/lapx/tree/main/tests), you can do as follows:

- Install test dependencies:
  ```bash
  pip install -r test_requirements.txt
  ```

- Run the full test suite:
  ```bash
  pytest -v
  ```

- Run a specific test file; for example, [`test_smoke.py`](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  pytest -v test_smoke.py
  ```

- Run a single test within a test file; for example, [`test_single_matrix_solvers_smoke`](https://github.com/rathaROG/lapx/blob/v0.9.1/tests/test_smoke.py#L137) inside [`test_smoke.py`](https://github.com/rathaROG/lapx/blob/main/tests/test_smoke.py):
  ```bash
  pytest -v test_smoke.py::test_single_matrix_solvers_smoke
  ```

**Notes**:
- Test data such as [`cost_eps.csv.gz`](https://github.com/rathaROG/lapx/blob/main/tests/cost_eps.csv.gz) is included and used by relevant tests; no additional setup is required.
- Run `pytest --help` to see all arguments in `pytest`.
