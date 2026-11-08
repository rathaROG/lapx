# LAPX benchmarks

This directory contains the maintained single, batch, and tracking benchmark
scripts: `benchmark_single.py`, `benchmark_batch.py`, and `benchmark_tracking.py`.
Use each script's `--help` for its options.

See the [benchmark guide](../benchmark.md) for installation commands, timing
settings, result checks, and historical results.
Current installation commands use the published `lapx>=0.13.0` package.
The scripts compare LAPX solver families with SciPy.

| Script | Comparisons |
| --- | --- |
| `benchmark_single.py` | JV, JVC, JVX, JVXA, JVS, JVSA, R, H, and SciPy assignment pairs |
| `benchmark_batch.py` | Dense batch solvers, sequential loops, SciPy, and sparse `lapmod` comparisons |
| `benchmark_tracking.py` | JV, JVC, JVX, JVS, R, H, and SciPy tracking outputs, plus JV with a threshold applied during optimization |

R/H rows are skipped when those solvers are unavailable.
The sparse batch section is skipped when `lapmod_batch` is unavailable.
The scripts retain JVS's default float32 precision.
The batch `jvsa64` row uses float64.

These package benchmarks do not reproduce the paper's full protocol.
The [paper benchmark guide](https://github.com/rathaROG/lap-paper/blob/main/benchmark/README.md)
covers assignment, cached tracking/replay, and LSAPE experiments.
Use the paper's protocol, pinned dependencies, and recorded evidence to
reproduce its tables and figures.
Production implementations and numerical regression tests remain in LAPX.
