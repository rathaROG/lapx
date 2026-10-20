# R/H integration checks

Packaging and API checks recorded on 2026-10-19 using Windows x64,
CPython 3.11, and Rust 1.99.1 (`stable-x86_64-pc-windows-msvc`).

## Checks completed

| Check | Result |
| --- | --- |
| Full Python suite against the wheel rebuilt from the source archive | 2,542 passed |
| Shared R/H numerical contract cases (included above) | 591 per family |
| Public coexistence/signatures and mixed-family concurrency (included above) | 9 passed |
| Rust tests | 18 passed with default features; 20 with all features |
| Clippy and Rust formatting | Passed; Clippy used `-D warnings` |
| Static return-type checks | Pyright: 0 errors, 0 warnings |
| Build options and target selection | 22 passed, including simulated targets |
| Legacy-only wheel from the same build base | 275 passed; no R/H binary or exports |
| Source archive contents | Required sources and type stub present; build artifacts excluded |
| Wheel contents | Both families, type stub, and license notices present |

## Platform coverage

This local run covered Windows x64 only. Linux/macOS, other Python versions,
and ARM execution were outside this qualification; simulated target-selection
checks do not establish native platform coverage.

The [integration workflow](../../.github/workflows/rh.yaml) checks source builds,
installed wheels, legacy-only wheels, and legacy-only editable installs on
Windows, Linux, and macOS. See [GitHub Actions](https://github.com/rathaROG/lapx/actions)
for subsequent runs.

musllinux ARMv7 wheels intentionally omit R/H and keep the existing solvers.
Their smoke check requires the R/H extension, stub, and exports to be absent;
other wheel targets require both families. Cross-built Windows ARM64 wheels
need native testing.
