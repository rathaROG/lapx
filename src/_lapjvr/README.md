# LAPJVR and LAPJVH

Two explicit solver families share one Rust core, Cython boundary, workspace
implementation, and worker cache. They coexist in one compiled extension:

| Entry points | Required-square completion |
| --- | --- |
| `lapjvr`, `lapjvr_batch` | Rust |
| `lapjvh`, `lapjvh_batch` | C++17 called once from Rust |

Both use the same Rust initialization and bounded row reduction. Rectangular
and finite-limit problems use the same Rust paths in both families. The
completion choice belongs to each call; there is no mutable global mode.

The [comparison report](https://github.com/rathaROG/lapx-benchmarks/blob/main/PORTS_RESULTS.md)
records the faithful JVX/JVS/SciPy ports, accepted changes, rejected experiments,
and remaining losses. Historical “hybrid build” results correspond to the
completion now exposed as LAPJVH. They predate the coexistence packaging and
are not fresh performance measurements of this integration. Neither family is
universally fastest. Total-cost performance tuning remains separate work.

## Build and install

Install current stable Rust/Cargo and the normal LAPX C++ build prerequisites,
then run from this checkout:

```bash
python -m pip install .
```

Standard builds include both families. Installing a wheel requires no Rust
compiler. Set `LAPX_BUILD_RUST=0` for a source build containing only the existing
solvers; `LAPX_BUILD_RUST=1` explicitly enables both. The old `LAPX_RUST_CPP` flag
emits an obsolescence warning and no longer changes `lapjvr`. Use `lapjvh` at
the call site. For existing experimental hybrid callers, replace `lapjvr` /
`lapjvr_batch` with `lapjvh` / `lapjvh_batch` to retain C++ completion.

Normal and legacy-only builds use separate output directories to prevent stale
extensions crossing into wheels. Use distinct explicit `--build-lib` directories
if overriding this layout. Legacy-only wheels also omit the R/H type stub and
typing exports; the source archive retains them for full builds.
Legacy-only editable installs (`LAPX_BUILD_RUST=0 python -m pip install -e .`)
use setuptools' strict link layout, including when another editable mode is
requested. Their installed initializer and typing files match legacy wheels;
ordinary Python modules remain linked to the checkout. Reinstall after changing
package exports or adding modules. Keep the editable install's directory under
`build/` for as long as the install is in use.
Run installed-wheel tests outside the source `lap/`
directory. The package remains named `lapx` and imported as `lap`; do not install
the unrelated `lap` distribution into the same environment.

Current local qualification uses Windows x64, CPython 3.11, and Rust 1.99.1.
Other platforms are wired into CI but need successful runs before release.
The inherited Cargo minimum is not a tested compatibility claim; only current
Rust is used here. macOS builds target one architecture at a time. Windows
Cargo targets are selected from the Python extension architecture, including
ARM64 cross builds. Cross-built wheels require a native machine for testing.
Wheel CI builds musllinux ARMv7 with `LAPX_BUILD_RUST=0` because Rust does not
supply native host tools for that environment. These wheels retain all existing
solvers and omit only `lapjvr`, `lapjvh`, and their batch variants. manylinux
ARMv7 and musllinux AArch64 wheels still include both R/H families.

`LAPX_BASEOPTS`, `LAPX_LTO`, and `LAPX_NATIVE` also configure the Rust build.
Both R/H boundaries and the hybrid kernel retain strict floating-point rules
when `LAPX_FASTMATH=1` is used for the other solvers. Runtime dependency licenses
are in `THIRD_PARTY_NOTICES`; the JVS-derived implementation retains `LICENSE`.

## Single-matrix API

```python
lap.lapjvr(cost, extend_cost=False, cost_limit=np.inf, return_cost=True,
           *, precision="native", output="indices")
lap.lapjvh(cost, extend_cost=False, cost_limit=np.inf, return_cost=True,
           *, precision="native", output="indices")
```

`cost` is a numeric array or array-like of shape `(N, M)`. Both families return:

| Output | `return_cost=False` | `return_cost=True` (default) |
| --- | --- | --- |
| `"indices"` (default) | `(rows, cols)` | `(total, rows, cols)` |
| `"pairs"` | `pairs` | `(total, pairs)` |

Indices are int64, sorted by original row. `rows[i], cols[i]` identifies one
matched pair; unmatched rows and columns are omitted. `pairs` has shape `(K, 2)`
and the same layout as the `*a` solvers, but int64 instead of int32. Empty
solutions retain these shapes and dtypes. The scalar total is a Python float
accumulated in float64 from selected original input values, not rounded working
costs. Tied optima can choose different pairs from JVX, JVS, or SciPy.

```python
import lap
import numpy as np

cost = np.array([[3., 1.], [1., 4.]], dtype=np.float32)
rows, cols = lap.lapjvr(cost, return_cost=False)
pairs = lap.lapjvh(cost, output="pairs", return_cost=False)
total, pairs = lap.lapjvh(cost, output="pairs")
```

## Batch API

```python
lap.lapjvr_batch(costs, extend_cost=False, cost_limit=np.inf, return_cost=True,
                 n_threads=0, *, precision="native", output="indices")
lap.lapjvh_batch(costs, extend_cost=False, cost_limit=np.inf, return_cost=True,
                 n_threads=0, *, precision="native", output="indices")
```

`costs` has shape `(B, N, M)`. The result is `(rows_list, cols_list)` or
`pairs_list`, in input order. With `return_cost=True`, prepend a float64 array
of `B` totals: `(totals, rows_list, cols_list)` or `(totals, pairs_list)`.
Each list has length `B`; its arrays may contain different numbers of matches.
An empty batch returns empty lists and, when requested, an empty totals array.

```python
batch = np.stack([cost, cost])
rows_list, cols_list = lap.lapjvr_batch(batch, return_cost=False, n_threads=2)
pairs_list = lap.lapjvh_batch(batch, output="pairs", return_cost=False, n_threads=2)
```

`n_threads=0` or `None` uses `os.cpu_count()` (one if unavailable), capped by `B`;
small workloads may run serially. There is no fixed eight-worker ceiling.
One or negative counts select serial execution. Positive counts request
reusable native workers, capped by `B`, even when the request exceeds the CPU count.
Both families share a cache of up to two worker-pool configurations;
concurrent calls keep their completion choices local. Avoid oversubscribing
cores with several large threaded calls. Use process spawning instead of
forking after native worker pools have initialized.

## Precision, matching, and errors

- `precision="native"` retains float32/float64 input storage; other real numeric
  input uses float64. Explicit `"float32"` and `"float64"` select working storage.
  Finite values that overflow explicit float32 conversion raise `ValueError`.
- Required squares use float64 potentials and distances even with borrowed
  float32 costs. Rectangular and optional paths use the selected precision.
- Rectangles require `extend_cost=True` unless `cost_limit` is finite. They use
  native rectangular paths without padding the matrix to a square.
- A finite limit minimizes selected costs plus half the limit for every
  unmatched row and column. The returned total sums only selected original
  costs, excluding those penalties. A finite limit can therefore choose fewer
  than `min(N, M)` pairs; it is not equivalent to filtering a required solution.
- Positive infinity forbids an edge. Inputs must exclude NaN and negative
  infinity. Infeasible required assignments and reduced-cost overflow raise
  `ValueError`. Allocation failures raise `MemoryError`.
- Invalid shape, output mode, precision, or limit raises an exception. Batch
  solver failures identify the lowest failing batch index. No partial batch
  result is returned; subsequent calls can reuse the workers normally.
- Inputs and every alias must remain immutable until a call returns. The
  boundary borrows suitable contiguous float arrays and holds their owners
  while the native solve releases the GIL. Noncontiguous inputs are normalized.

## Implementation and verification

- `src/square.rs`: shared JVS-derived initialization, reduction transfer, two
  bounded row-reduction passes, and explicit completion selection.
- `src/lib.rs`: cost scans, reusable workspaces, workers, and Rust certificates.
- `src/rectangular.rs`: native rectangular and implicit optional assignment.
- `src/ffi.rs`, `lapjvr.h`, `_lapjv_rh.pyx`: one checked boundary for all four
  public functions, direct output, original-value totals, and Rayon workers.
- `src/cpp_completion.rs`, `src/cpp_completion.cpp`, `build.rs`: the hybrid
  completion kernel. Rust owns all buffers; C++ retains no pointers, allocates
  nothing, and never throws through the boundary.
- `lap/_lapjv_rh.pyi`: signatures and return-mode overloads for the shared
  `lap._lapjv_rh` extension, covering both R/H families.
- `src/profile.rs`, `examples/profile.rs`: optional diagnostics, absent from
  normal timing builds. Modes `square` and `hybrid` profile the two completions.

The four-row initialization hint and reduction bounds are unchanged by this
family split. The hint is a performance heuristic; permutations can affect work
and timing. Experimental reference ports remain outside the production API.

```bash
cargo test --locked --manifest-path src/_lapjvr/Cargo.toml
cargo test --locked --all-features --manifest-path src/_lapjvr/Cargo.toml
cargo clippy --locked --all-targets --all-features --manifest-path src/_lapjvr/Cargo.toml -- -D warnings
python -m pytest -q tests/test_lapjvr.py tests/test_lapjv_rh.py
```

The Cargo `cpp-completion` feature adds C++ completion without replacing Rust
completion. Packaging always enables it for the shared extension. Plain Cargo
builds retain the all-Rust core for standalone development. Python contract
tests run for each family; coexistence tests mix them concurrently. Rust tests
compare exact primal/dual state and work counters when alternating completions.
The [test guide](../../tests/README.md) covers installed wheels and static checks.
The [integration qualification](INTEGRATION.md) records the verified local
wheel, test counts, and remaining platform release gates.

Build integration follows the primary documentation for
[Rust static linking](https://doc.rust-lang.org/stable/reference/linkage.html),
[foreign interfaces](https://doc.rust-lang.org/nomicon/ffi.html), and
[cibuildwheel Rust provisioning](https://cibuildwheel.pypa.io/en/stable/faq/#building-rust-wheels).
