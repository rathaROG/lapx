# Running test suite for `lapx`

These tests are powered by `pytest` and configured via `pytest.ini`. 

- Install test dependencies from this directory:
  ```bash
  pip install -r test_requirements.txt
  ```

- Run the full test suite from this directory:
  ```bash
  pytest -v
  ```

- Run a specific test file from this directory:
  ```bash
  pytest -v test_smoke.py
  ```

- Run a single test within a file from this directory:
  ```bash
  pytest -v test_smoke.py::test_single_matrix_solvers_smoke
  ```

Notes:
- Test data such as `tests/cost_eps.csv.gz` is included and used by relevant tests; no additional setup is required.
- Run `pytest --help` to see all arguments in `pytest`.
