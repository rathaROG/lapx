# LAPJVR and LAPJVH

`lapjvr` and `lapjvh` share a Rust Jonker-Volgenant implementation. For square
problems with infinite `cost_limit`, completion uses Rust (`lapjvr`) or C++
(`lapjvh`). Rectangular and finite-limit problems use the same Rust paths
without square padding. Both families provide single and batch functions.

If you don't need the other LAPX solvers, you can use the dedicated
[laprust](https://github.com/rathaROG/laprust) (Rust, from `lapjvr`) or
[lapcpp](https://github.com/rathaROG/lapcpp) (C++) package instead; each provides
the same options through `lapjv` and `lapjv_batch`.

## Build and install

Prebuilt wheels require no Rust compiler. To build from source, install stable
Rust/Cargo and the normal LAPX C++ build prerequisites, then run from the
repository root:

```bash
python -m pip install .
```

Standard builds include both families. Set `LAPX_BUILD_RUST=0` for a legacy-only
build, or `LAPX_BUILD_RUST=1` to enable R/H explicitly. Legacy-only wheels omit
the R/H extension, type stub, and exports; source archives retain the full
sources. musllinux ARMv7 wheels are legacy-only; manylinux ARMv7 and musllinux
AArch64 wheels include R/H.

Legacy-only editable installs use setuptools' strict link layout under
`build/`. Keep that directory while the install is in use, and reinstall after
changing package exports or adding modules. If overriding `--build-lib`, use
separate directories for full and legacy-only builds.

`LAPX_BASEOPTS`, `LAPX_LTO`, and `LAPX_NATIVE` also configure the Rust build.
Both R/H boundaries and the hybrid kernel retain strict floating-point rules
when `LAPX_FASTMATH=1` is used for the other solvers.

## Single-matrix API

```text
lap.lapjvr(cost, extend_cost=False, cost_limit=np.inf, return_cost=True,
           *, precision="native", output="indices")
lap.lapjvh(cost, extend_cost=False, cost_limit=np.inf, return_cost=True,
           *, precision="native", output="indices")
```

`cost` is a real numeric array-like of shape `(N, M)`. The return value depends
on `output` and `return_cost`:

| Output | `return_cost=False` | `return_cost=True` (default) |
| --- | --- | --- |
| `"indices"` (default) | `(rows, cols)` | `(total, rows, cols)` |
| `"pairs"` | `pairs` | `(total, pairs)` |

Indices use int64 and are sorted by row. Each `rows[i], cols[i]`
is a matched pair in the original matrix; unmatched rows and columns are
omitted. `pairs` has shape `(K, 2)`, including `(0, 2)` for empty results.
`total` is a Python float, summed in float64 from selected original input
costs before any float32 conversion.

```python
import lap
import numpy as np

cost = np.random.rand(100, 150)
total, rows, cols = lap.lapjvr(cost, extend_cost=True)
total, pairs = lap.lapjvh(cost, extend_cost=True, output="pairs")

pairs = lap.lapjvh(cost, extend_cost=True, output="pairs", return_cost=False)
```

## Batch API

```text
lap.lapjvr_batch(costs, extend_cost=False, cost_limit=np.inf, return_cost=True,
                 n_threads=0, *, precision="native", output="indices")
lap.lapjvh_batch(costs, extend_cost=False, cost_limit=np.inf, return_cost=True,
                 n_threads=0, *, precision="native", output="indices")
```

`costs` is a real numeric array-like of shape `(B, N, M)`. Results keep input
order: `(rows, cols)` or, with `output="pairs"`, `pairs`. Each
list has length `B`; its arrays may contain different numbers of matches.
If `return_cost` is True, return a float64 array of `B` totals first:
`(totals, rows, cols)` or `(totals, pairs)`. An empty batch returns
empty lists and, when requested, empty totals. Empty matrix dimensions give
empty assignments and zero totals. Totals follow the single-matrix rules.

```python
import lap
import numpy as np

batch_costs = np.random.rand(500, 100, 150)  # (B, N, M)
totals, rows, cols = lap.lapjvr_batch(batch_costs, extend_cost=True, n_threads=2)
totals, pairs = lap.lapjvh_batch(
    batch_costs, extend_cost=True, output="pairs", n_threads=2
)
```

`n_threads` sets the number of worker threads:

- `0` or `None`: Use `os.cpu_count()` (or 1 if unavailable), capped by `B`.
- `1` or a negative value: Run serially.
- Positive values: Use at most this many workers, capped by `B`, not the CPU count.

Empty and single-item batches run serially. Automatic mode may also run small
workloads serially. Both families share reusable native worker pools;
concurrent calls keep their completion choices local. Use process spawning
instead of forking after native worker pools have initialized.

## Precision, matching, and errors

- `precision="native"` preserves float32/float64 input storage; other real numeric
  inputs use float64. Explicit `"float32"` and `"float64"` select the working cost
  precision. Finite costs and limits must fit the float32 range when float32 is
  used; values that overflow conversion raise `ValueError`.
- Required square problems use float64 potentials and distances even with
  float32 costs. Rectangular and finite-limit paths use the selected working
  precision.
- Rectangular inputs require `extend_cost=True` unless `cost_limit` is finite.
  Rectangular and finite-limit problems use native Rust paths without padding
  the matrix to a square.
- A finite limit minimizes selected costs plus half the limit for every
  unmatched row and column. The returned total sums only selected original
  costs, excluding those penalties. A finite limit can therefore choose fewer
  than `min(N, M)` pairs; it is not equivalent to filtering a required solution.
  Negative finite limits are allowed; NaN and negative infinity are invalid.
  With `cost_limit=np.inf`, each problem requires `min(N, M)` matches.
- The solver does not check for NaN (not a number) or negative infinity.
  Check or remove these values before you call the solver. Results with these
  values are undefined. Positive infinity can represent a forbidden assignment.
  Infeasible required assignments and reduced-cost overflow raise `ValueError`.
  Allocation failures raise `MemoryError`.
- Invalid shape, output mode, precision, or limit raises an exception. Batch
  solver failures identify the lowest failing batch index. No partial batch
  result is returned. Equal-cost optima may differ across solvers or precisions.
- Suitable contiguous arrays are borrowed, and the native solve releases
  the GIL. Other inputs may be copied for layout or precision conversion.
  Do not mutate or resize the input or any alias until the call returns.

## Implementation and verification

All four functions are native exports from `lap._lapjv_rh`, with signatures
and documentation in [the type stub](../../lap/_lapjv_rh.pyi). Run Rust checks
from the repository root:

```bash
cargo test --locked --manifest-path src/_lapjvr/Cargo.toml
cargo test --locked --all-features --manifest-path src/_lapjvr/Cargo.toml
cargo clippy --locked --all-targets --all-features --manifest-path src/_lapjvr/Cargo.toml -- -D warnings
```

Python builds enable Cargo's `cpp-completion` feature for the shared extension.
See the [test guide](../../tests/README.md) for installed-wheel and typing checks,
and [INTEGRATION.md](INTEGRATION.md) for the dated integration results.
License notices are in [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
