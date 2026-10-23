# Build and packaging checks

This directory checks how LAPX is built and distributed. Solver behavior,
numerical regressions, and public API typing checks live in [tests/](../../tests/README.md).

## Build configuration tests

Run from the repository root:

```bash
python -m pip install -r .github/tests/requirements.txt
python -m pytest -q .github/tests
```

`test_setup.py` checks compiler flags, Rust target selection, build directories,
wheel contents, legacy-only editable installs, and source-archive contents.
It uses compiler probes and Python stand-ins for native solvers, so it does not
require an installed LAPX package, NumPy, or a native compiler.
Its own `pytest.ini` supplies the timeout settings; solver fixtures are not loaded.

The editable-install checks cover source edits, exports, typing files, and stale
binaries. Legacy-only editable installs use setuptools' strict link layout;
reinstall after changing package exports or adding modules.

## Installed-wheel smoke checks

After installing a built wheel, run from the repository root:

```bash
python .github/tests/check_rh_wheel.py
```

`check_rh_wheel.py` is a standalone check requiring only NumPy and the installed
package. It checks both R/H families and verifies that native exports and typing
files match the installed solver set. Invoke the script by path as shown so the
checkout's source package does not shadow the installed package.

For an intentionally legacy-only build (`LAPX_BUILD_RUST=0`), use:

```bash
python .github/tests/check_rh_wheel.py --legacy-only
```

This checks all pre-existing solvers and requires the R/H extension, exports, and
stub to be absent. The musllinux ARMv7 wheel jobs use this mode.

The source archive includes `.github/tests/check_rh_wheel.py` so cibuildwheel can
test wheels built from the archive. Other `.github/` files and the solver test
suite remain excluded. The archive always retains the full R/H sources and typing.

The two full-test workflows run build checks and solver tests in separate steps.
The [R/H integration workflow](../workflows/rh.yaml) also builds a wheel from the
source archive and checks compiled legacy-only wheels and editable installs.
Cross-platform CI results are needed before claiming platform qualification.
