# R/H family integration qualification

Local qualification on 2026-10-19: Windows x64, CPython 3.11, Rust 1.99.1
(`58cf8f9c3`, LLVM 23.1.1), `stable-x86_64-pc-windows-msvc`. No older Rust build
was tested. This record covers packaging/API integration, not new timings.

## Result

Standard builds now expose `lapjvr`, `lapjvh`, `lapjvr_batch`, and
`lapjvh_batch` together. They share one extension, conversion/output code,
workspace implementation, and native worker pools. Completion is chosen per
call: R always uses Rust; H uses C++ for required squares. Rectangular and
finite-limit paths are shared Rust. No runtime global mode or Python forwarding
wrapper was introduced.

`return_cost=True` remains the default with its existing semantics. Total-cost
optimization was deferred. Both output layouts retain int64 indices, and the
two families have matching signatures, errors, precision, and worker options.

The initialization/reduction body, Rust completion loop, C++ completion kernel,
and rectangular implementation were checked against the prior commit. Their
algorithm code is unchanged; the family selection and public wiring are new.
Existing JVX/JVS source is unchanged. Historical variants in the separate
[benchmark repository](https://github.com/rathaROG/lapx-benchmarks) use
their archived measured sources so they cannot silently acquire a different
completion when rebuilt. Earlier performance tables remain historical evidence.

## Checks completed

| Check | Result |
| --- | --- |
| Full Python suite against the wheel rebuilt from the source archive | 2,542 passed |
| Shared R/H numerical contract cases (included above) | 591 per family |
| Public coexistence/signatures and mixed-family concurrency (included above) | 9 passed |
| Rust tests, all features | 20 passed |
| Rust tests, default features | 18 passed |
| Strict Clippy, all targets/features | Passed with `-D warnings` |
| Rust formatting | Passed |
| Static return-type checks | Pyright: 0 errors, 0 warnings |
| Final build-option/target-selection checks | 22 passed, including four additional simulated macOS target cases |
| Legacy-only wheel from the same build base | 275 passed; no R/H binary or exports |
| Source archive contents | Cargo lockfile, C++ kernel, header, and type stub present; no target/build/benchmark trees or generated Cython C++ |
| Workflow configuration | YAML parsed; native cross-platform execution pending |

The wheel contains both families and their license notices. Its size is
**427,639 bytes**, below the 5 MB goal. It was installed into an isolated target
directory, leaving the existing Python LAP namespace untouched.

Local artifacts, relative to the repository root:

- Wheel: `build/lapjv-rh-from-source/lapx-0.10.0-cp311-cp311-win_amd64.whl`
- Source: `build/lapjv-rh-source/lapx-0.10.0.tar.gz`
- Installed package: `build/lapjv-rh-release/`
- Detailed hashes/environment: `build/lapjv-rh-qualification.json`
- Test results: `build/lapjv-rh-full.xml`, `build/lapjv-rh-legacy.xml`

The wheel SHA-256 is
`22ad837ce15c49387d1d4346fc2485267d384ffde46915090beb425b6cc4abb7`.

The final macOS cross-target helper and CI configuration were checked after
that Windows wheel was built; its solver binary is unchanged. These simulated
target checks do not substitute for native macOS qualification.

## Remaining release gates

Linux/macOS, other Python versions, and ARM wheel builds need successful native
CI runs. The new integration workflow builds a source archive, rebuilds its
wheel, checks exports, runs the full suite, and checks a legacy-only build.
Existing test workflows now restore the checkout's wheel before their suite;
wheel workflows provision current Rust and run an R/H smoke check. Cross-built
Windows ARM64 wheels still need native testing. musllinux ARMv7 wheels use
`LAPX_BUILD_RUST=0` because Rust does not supply native host tools there. Their
separate smoke check requires all pre-existing solvers and the absence of the
R/H extension, stub, and runtime/typing exports. Other wheel targets continue to
require both families and their typing sources; source archives retain them too.

The version remains the development branch's 0.10.0; no release was published.
Optimization of the two explicit families can proceed from this shared code,
using the same installed wheel for comparisons. New performance claims require
new measurements; this integration pass did not repeat the broad survey.
