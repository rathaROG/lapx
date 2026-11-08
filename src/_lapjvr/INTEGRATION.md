# R/H integration checks

These packaging and API checks were recorded on 2026-10-19.
The run used Windows x64, CPython 3.11, and Rust 1.99.1 (`stable-x86_64-pc-windows-msvc`).
The counts below describe that historical run, not the current test inventory.

## Checks completed

| Check | Result |
| --- | --- |
| Full Python suite against the wheel rebuilt from the source archive | 2,542 passed |
| Shared R/H numerical contract cases (included above) | 591 per family |
| Public coexistence/signatures and mixed-family concurrency (included above) | 9 passed |
| Rust tests | 18 passed with default features. 20 passed with all features. |
| Clippy and Rust formatting | Passed. Clippy used `-D warnings`. |
| Static return-type checks | Pyright: 0 errors, 0 warnings |
| Build options and target selection | 22 passed, including simulated targets |
| Legacy-only wheel from the same build base | 275 passed. No R/H binary or exports. |
| Source archive contents | Required sources and type stub present. Build artifacts excluded. |
| Wheel contents | Both families, type stub, and license notices present |

## Platform coverage

This local run covered Windows x64 only. It did not test Linux/macOS, other
Python versions, or ARM execution. Simulated target-selection checks do not
establish native platform coverage.

The [integration workflow](../../.github/workflows/rh.yaml) checks source builds,
installed wheels, legacy-only wheels, and legacy-only editable installs on
Windows, Linux, and macOS. See [GitHub Actions](https://github.com/rathaROG/lapx/actions)
for subsequent runs.

musllinux ARMv7 wheels intentionally omit R/H and keep the existing solvers.
Their smoke check requires the R/H extension, stub, and exports to be absent.
Other wheel targets require both families. Cross-built Windows ARM64 wheels
need native testing.
