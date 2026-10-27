[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# 🏆 Quick Benchmark

The [single-matrix](benchmarks/benchmark_single.py), [batch](benchmarks/benchmark_batch.py),
and [tracking](benchmarks/benchmark_tracking.py) scripts compare assignment workflows with SciPy on your machine.
The recorded results below include the test environment and per-case settings.

## 💡 Run the benchmarks

```bash
python -m pip install -U lapx scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/benchmarks
python benchmark_single.py --quick
python benchmark_batch.py --quick
python benchmark_tracking.py --quick
```

For a local build, install and run from the repository root:

```bash
python -m pip install . scipy
python -m benchmarks.benchmark_single --quick
python -m benchmarks.benchmark_batch --quick --threads 2
python -m benchmarks.benchmark_tracking --quick
```

### Repeats and timing

All three scripts accept `--repeats N` and `--seed N` (default **2026**).
Batch defaults to **2 shuffled rounds**, using seeds **2026 and 2027**; single and tracking default to **3 rounds**.
Each round generates a fresh input using `seed + round_index`, with the matrix dimensions included in the seed.
Every solver receives the same input, warms up on it, and runs in a shuffled order.
Input generation, sparse preparation, warmup, and independent result checks are outside timing.

Single and batch tables are sorted by time and show milliseconds, correctness, and speed relative to SciPy.
Tracking keeps sizes as rows and groups four solvers per table, with times in seconds, followed by an overall ranking in milliseconds.
The reported time is the median across rounds. For two rounds, this is the average of the two timings.
With `--repeats 1`, it is the single timed round.

| Script | `--quick` selection | Forced one-round cases |
| --- | --- | --- |
| Single | Sizes through 2500x5000 | Either dimension ≥5000 |
| Batch | Skips only the 10 × 4000x4000 dense batch | Either dimension ≥3000 |
| Tracking | Sizes through 2000x2500; thresholds 0.05 and 0.5 | Either dimension ≥5000 |

The one-round limits apply per case, even when `--repeats` is larger. Smaller cases retain the requested count.
For single and tracking matrices no larger than 64x64, each round averages **25 calls** per solver.
Larger matrices use one call per round. Batch rounds measure one call over the entire batch.

```bash
python benchmark_batch.py --quick --repeats 2 --seed 2026 --threads 2
python benchmark_tracking.py --quick --repeats 1
```

### Assignment outputs

Single and tracking benchmarks use `return_cost=False` and include pair construction where needed.
R/H request `output='pairs'` directly with `precision='native'` on float64 inputs.
The other solvers keep their default precision settings: JVS uses float32, while the batch `jvsa64` row uses float64.
Unavailable R/H solvers are skipped.

Single checks compare assignment pairs with SciPy in every round. Tracking also compares unmatched row and column sets.
A mismatch in any round remains visible in the final table.

<details><summary>Batch benchmark methods</summary>

### Costs and threads

Batch solvers and sequential loops use `return_cost=False` by default.
Add `--cost` to include total-cost calculation in the timed calls.
The optional `Cost (last round)` column shows the total across the final round's batch; the time remains the median across rounds.
SciPy's loop sums selected costs with NumPy when `--cost` is enabled.

`--threads N` controls batch solvers; **0** uses the CPU count, capped by batch size.
R/H may run small workloads serially. Explicit positive requests are capped by batch size, with no fixed eight-thread ceiling.
The loop rows remain sequential. R/H batch and loop rows use direct pairs.

```bash
python benchmark_batch.py --quick --threads 2 --cost
python benchmark_batch.py --sparse-only --threads 8
```

### Sparse comparisons

Sparse cases compare dense solvers with a `lapmod` loop and `lapmod_batch`.
Each round uses the same costs and allowed assignments: dense arrays mark missing edges with `np.inf`,
while `lapmod` receives finite entries in `(n, cc, ii, kk)` form.
Preparing these sparse arrays is excluded from solver times.

The generator keeps a finite diagonal so every problem has a full assignment.
Headers show the **target density**; the diagonal can increase the actual density.
The default sparse cases are **100 × 1000x1000 at 1%** and **50 × 2000x2000 at 5%**.
`--quick` keeps both sparse cases and all dense cases except 4000x4000.

The sparse rows include `lapmod_batch` with one worker and, when a larger or automatic thread count is selected, a second batch row.
With `--threads 1`, only the one-worker batch row appears.
The sparse section is skipped if `lapmod_batch` is unavailable.

### Result checks

Every timed result is checked for valid assignments and per-problem costs matching SciPy within floating-point tolerances.
With `--cost`, returned totals must also match costs calculated from the original input.
Passing rows show `PASS`; a mismatch raises an error. All checks run outside timing.

</details>

The [single](.github/workflows/benchmark_single.yaml) and [tracking](.github/workflows/benchmark_tracking.yaml)
workflows use `--quick --repeats 3`. The [batch](.github/workflows/benchmark_batch.yaml) workflow uses
`--quick --repeats 2 --seed 2026`.
They build the checkout and check R/H availability before benchmarking.

### Historical results (LAPX 0.12.0)

R/H single and batch results use float64 costs and `return_cost=False`.
See each case for matrix sizes, thread counts, and timing settings.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.12.0
scipy==1.17.1
numpy==2.4.6
```

<details><summary>📄 Historical single results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new8\lapx\benchmarks>python benchmark_single.py


Note: R/H native float64, JVS default float32.


### Matrix 4 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000464  🥇 3.59x faster
lapjvh   ✅ PASS   0.000488  🥈 3.42x faster
scipy    ⭐ BASE   0.001668  ⭐ baseline
lapjvc   ✅ PASS   0.003700  🐌 2.22x slower
lapjvxa  ✅ PASS   0.004788  🐌 2.87x slower
lapjvx   ✅ PASS   0.005468  🐌 3.28x slower
lapjv    ✅ PASS   0.005760  🐌 3.45x slower
lapjvs   ✅ PASS   0.005936  🐌 3.56x slower
lapjvsa  ✅ PASS   0.007644  🐌 4.58x slower
--------------------------------------------

### Matrix 5 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000520  🥇 3.45x faster
lapjvh   ✅ PASS   0.000564  🥈 3.18x faster
lapjvsa  ✅ PASS   0.001296  🥉 1.38x faster
scipy    ⭐ BASE   0.001792  ⭐ baseline
lapjvxa  ✅ PASS   0.002944  🐌 1.64x slower
lapjvc   ✅ PASS   0.003764  🐌 2.10x slower
lapjvx   ✅ PASS   0.003776  🐌 2.11x slower
lapjv    ✅ PASS   0.003860  🐌 2.15x slower
lapjvs   ✅ PASS   0.004508  🐌 2.52x slower
--------------------------------------------

### Matrix 5 x 6 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000476  🥇 3.58x faster
lapjvh   ✅ PASS   0.000480  🥈 3.55x faster
scipy    ⭐ BASE   0.001704  ⭐ baseline
lapjvc   ✅ PASS   0.003796  🐌 2.23x slower
lapjvxa  ✅ PASS   0.004856  🐌 2.85x slower
lapjvx   ✅ PASS   0.005640  🐌 3.31x slower
lapjvs   ✅ PASS   0.005908  🐌 3.47x slower
lapjv    ✅ PASS   0.006000  🐌 3.52x slower
lapjvsa  ✅ PASS   0.007716  🐌 4.53x slower
--------------------------------------------

### Matrix 45 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.002736  🥇 6.31x faster
lapjvh   ✅ PASS   0.002804  🥈 6.16x faster
lapjvxa  ✅ PASS   0.010520  🥉 1.64x faster
lapjvx   ✅ PASS   0.011484  🏆 1.50x faster
lapjvs   ✅ PASS   0.011920  🏆 1.45x faster
lapjv    ✅ PASS   0.012216  🏆 1.41x faster
lapjvsa  ✅ PASS   0.014112  🏆 1.22x faster
scipy    ⭐ BASE   0.017264  ⭐ baseline
lapjvc   ✅ PASS   0.039792  🐌 2.30x slower
--------------------------------------------

### Matrix 50 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.005808  🥇 4.11x faster
lapjvr   ✅ PASS   0.006028  🥈 3.96x faster
lapjvsa  ✅ PASS   0.010332  🥉 2.31x faster
lapjvxa  ✅ PASS   0.010516  🏆 2.27x faster
lapjvx   ✅ PASS   0.010652  🏆 2.24x faster
lapjv    ✅ PASS   0.011552  🏆 2.06x faster
lapjvs   ✅ PASS   0.013792  🏆 1.73x faster
scipy    ⭐ BASE   0.023844  ⭐ baseline
lapjvc   ✅ PASS   0.027968  🐌 1.17x slower
--------------------------------------------

### Matrix 50 x 55 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.003324  🥇 6.07x faster
lapjvh   ✅ PASS   0.003332  🥈 6.05x faster
lapjvx   ✅ PASS   0.012924  🥉 1.56x faster
lapjvxa  ✅ PASS   0.013052  🏆 1.54x faster
lapjv    ✅ PASS   0.015800  🏆 1.28x faster
lapjvs   ✅ PASS   0.015852  🏆 1.27x faster
lapjvsa  ✅ PASS   0.017240  🏆 1.17x faster
scipy    ⭐ BASE   0.020164  ⭐ baseline
lapjvc   ✅ PASS   0.057760  🐌 2.86x slower
--------------------------------------------

### Matrix 450 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.311100  🥇 7.45x faster
lapjvh   ✅ PASS   0.339900  🥈 6.81x faster
lapjvs   ✅ PASS   0.527000  🥉 4.40x faster
lapjvsa  ✅ PASS   0.547000  🏆 4.23x faster
lapjv    ✅ PASS   0.792500  🏆 2.92x faster
lapjvx   ✅ PASS   0.800900  🏆 2.89x faster
lapjvxa  ✅ PASS   0.816900  🏆 2.84x faster
scipy    ⭐ BASE   2.316200  ⭐ baseline
lapjvc   ✅ PASS  11.027700  🐌 4.76x slower
--------------------------------------------

### Matrix 500 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.849600  🥇 5.36x faster
lapjvh   ✅ PASS   0.878300  🥈 5.18x faster
lapjvxa  ✅ PASS   2.091200  🥉 2.18x faster
lapjvsa  ✅ PASS   2.096900  🏆 2.17x faster
lapjvx   ✅ PASS   2.109500  🏆 2.16x faster
lapjvs   ✅ PASS   2.128600  🏆 2.14x faster
lapjv    ✅ PASS   2.167900  🏆 2.10x faster
scipy    ⭐ BASE   4.552400  ⭐ baseline
lapjvc   ✅ PASS   4.967600  🐌 1.09x slower
--------------------------------------------

### Matrix 500 x 550 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.386300  🥇 7.15x faster
lapjvr   ✅ PASS   0.394800  🥈 6.99x faster
lapjvsa  ✅ PASS   0.773600  🥉 3.57x faster
lapjvs   ✅ PASS   0.792000  🏆 3.49x faster
lapjv    ✅ PASS   0.962200  🏆 2.87x faster
lapjvx   ✅ PASS   0.969900  🏆 2.85x faster
lapjvxa  ✅ PASS   0.972700  🏆 2.84x faster
scipy    ⭐ BASE   2.761200  ⭐ baseline
lapjvc   ✅ PASS  14.250900  🐌 5.16x slower
--------------------------------------------

### Matrix 2500 x 5000 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS      7.488900  🥇 7.62x faster
lapjvh   ✅ PASS      7.672400  🥈 7.44x faster
scipy    ⭐ BASE     57.068500  ⭐ baseline
lapjvsa  ✅ PASS     61.402300  🐌 1.08x slower
lapjvs   ✅ PASS     64.135200  🐌 1.12x slower
lapjv    ✅ PASS     90.870200  🐌 1.59x slower
lapjvx   ✅ PASS     91.691700  🐌 1.61x slower
lapjvxa  ✅ PASS     93.963900  🐌 1.65x slower
lapjvc   ✅ PASS  12436.738400  🐌 217.93x slower
-------------------------------------------------

### Matrix 5000 x 5000 | float64 | return_cost=False

Solver   Check      Time (ms)  vs SciPy
----------------------------------------------
lapjvh   ✅ PASS   265.474500  🥇 4.38x faster
lapjvr   ✅ PASS   285.463200  🥈 4.07x faster
lapjvs   ✅ PASS   380.051000  🥉 3.06x faster
lapjvsa  ✅ PASS   380.505500  🏆 3.06x faster
lapjvx   ✅ PASS   630.670100  🏆 1.84x faster
lapjvxa  ✅ PASS   644.182100  🏆 1.80x faster
lapjv    ✅ PASS   659.658700  🏆 1.76x faster
scipy    ⭐ BASE  1162.609500  ⭐ baseline
lapjvc   ✅ PASS  1271.397500  🐌 1.09x slower
----------------------------------------------

### Matrix 5000 x 7500 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS     24.575300  🥇 8.53x faster
lapjvh   ✅ PASS     29.799900  🥈 7.03x faster
lapjvs   ✅ PASS    115.619800  🥉 1.81x faster
lapjvsa  ✅ PASS    119.006600  🏆 1.76x faster
lapjv    ✅ PASS    173.282900  🏆 1.21x faster
lapjvxa  ✅ PASS    173.797400  🏆 1.21x faster
lapjvx   ✅ PASS    178.428900  🏆 1.17x faster
scipy    ⭐ BASE    209.624900  ⭐ baseline
lapjvc   ✅ PASS  55516.489500  🐌 264.84x slower
-------------------------------------------------
```

</details>

<details><summary>🗂️ Historical batch results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new8\lapx\benchmarks>python benchmark_batch.py


Note: R/H native float64, JVS default float32, jvsa64 float64.


### Dense 10 x (4000x4000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvr     ✅ PASS   307.353600  🥇 21.86x faster
lapx-batch-jvh     ✅ PASS   316.996600  🥈 21.20x faster
lapx-batch-jvs     ✅ PASS   427.384500  🥉 15.72x faster
lapx-batch-jvsa    ✅ PASS   444.459300  🏆 15.12x faster
lapx-batch-jvsa64  ✅ PASS  1092.512100  🏆 6.15x faster
lapx-batch-jvxa    ✅ PASS  1108.823900  🏆 6.06x faster
lapx-batch-jvx     ✅ PASS  1184.534500  🏆 5.67x faster
lapx-loop-jvh      ✅ PASS  1624.774100  🏆 4.14x faster
lapx-loop-jvr      ✅ PASS  1632.752100  🏆 4.12x faster
lapx-loop-jvs      ✅ PASS  2550.632200  🏆 2.63x faster
lapx-loop-jvx      ✅ PASS  5239.937400  🏆 1.28x faster
scipy-loop         ⭐ BASE  6718.868900  ⭐ baseline
---------------------------------------------------------

### Dense 20 x (3000x2000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvr     ✅ PASS    73.078500  🥇 13.95x faster
lapx-batch-jvsa    ✅ PASS    83.876600  🥈 12.15x faster
lapx-batch-jvh     ✅ PASS    87.411100  🥉 11.66x faster
lapx-batch-jvs     ✅ PASS   113.126300  🏆 9.01x faster
lapx-batch-jvxa    ✅ PASS   137.854700  🏆 7.39x faster
lapx-batch-jvsa64  ✅ PASS   140.959000  🏆 7.23x faster
lapx-batch-jvx     ✅ PASS   150.424800  🏆 6.78x faster
lapx-loop-jvh      ✅ PASS   315.563200  🏆 3.23x faster
lapx-loop-jvr      ✅ PASS   318.953500  🏆 3.20x faster
lapx-loop-jvs      ✅ PASS   800.489700  🏆 1.27x faster
lapx-loop-jvx      ✅ PASS   985.005800  🏆 1.03x faster
scipy-loop         ⭐ BASE  1019.349700  ⭐ baseline
---------------------------------------------------------

### Dense 50 x (2000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   215.168500  🥇 27.23x faster
lapx-batch-jvr     ✅ PASS   218.626900  🥈 26.80x faster
lapx-batch-jvsa    ✅ PASS   297.980550  🥉 19.66x faster
lapx-batch-jvs     ✅ PASS   299.438200  🏆 19.57x faster
lapx-batch-jvx     ✅ PASS   443.284750  🏆 13.22x faster
lapx-batch-jvxa    ✅ PASS   444.665750  🏆 13.18x faster
lapx-batch-jvsa64  ✅ PASS   449.626800  🏆 13.03x faster
lapx-loop-jvr      ✅ PASS  1115.534750  🏆 5.25x faster
lapx-loop-jvh      ✅ PASS  1134.490800  🏆 5.16x faster
lapx-loop-jvs      ✅ PASS  2867.858550  🏆 2.04x faster
lapx-loop-jvx      ✅ PASS  3768.201650  🏆 1.55x faster
scipy-loop         ⭐ BASE  5858.669250  ⭐ baseline
---------------------------------------------------------

### Dense 100 x (1000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvr     ✅ PASS    25.218650  🥇 35.57x faster
lapx-batch-jvh     ✅ PASS    25.499350  🥈 35.18x faster
lapx-loop-jvr      ✅ PASS   111.338950  🥉 8.06x faster
lapx-loop-jvh      ✅ PASS   121.086400  🏆 7.41x faster
lapx-batch-jvsa    ✅ PASS   131.322850  🏆 6.83x faster
lapx-batch-jvs     ✅ PASS   134.910900  🏆 6.65x faster
lapx-batch-jvx     ✅ PASS   215.003150  🏆 4.17x faster
lapx-batch-jvsa64  ✅ PASS   232.570900  🏆 3.86x faster
lapx-batch-jvxa    ✅ PASS   233.609950  🏆 3.84x faster
lapx-loop-jvs      ✅ PASS   803.500950  🏆 1.12x faster
scipy-loop         ⭐ BASE   897.139500  ⭐ baseline
lapx-loop-jvx      ✅ PASS  1253.359900  🐌 1.40x slower
---------------------------------------------------------

### Dense 500 x (1000x1000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check       Time (ms)  vs SciPy
----------------------------------------------------------
lapx-batch-jvh     ✅ PASS    308.250850  🥇 36.81x faster
lapx-batch-jvr     ✅ PASS    312.508200  🥈 36.30x faster
lapx-batch-jvsa    ✅ PASS    527.266000  🥉 21.52x faster
lapx-batch-jvs     ✅ PASS    532.703100  🏆 21.30x faster
lapx-batch-jvxa    ✅ PASS    583.972250  🏆 19.43x faster
lapx-batch-jvsa64  ✅ PASS    584.074900  🏆 19.42x faster
lapx-batch-jvx     ✅ PASS    591.317750  🏆 19.19x faster
lapx-loop-jvh      ✅ PASS   2149.361000  🏆 5.28x faster
lapx-loop-jvr      ✅ PASS   2193.909800  🏆 5.17x faster
lapx-loop-jvs      ✅ PASS   6532.112150  🏆 1.74x faster
lapx-loop-jvx      ✅ PASS   6829.801350  🏆 1.66x faster
scipy-loop         ⭐ BASE  11345.609150  ⭐ baseline
----------------------------------------------------------

### Sparse 100 x (1000x1000) | target density=1.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    17.753350  🥇 94.59x faster
lapx-batch-jvh     ✅ PASS    60.404700  🥈 27.80x faster
lapx-batch-jvr     ✅ PASS    60.995500  🥉 27.53x faster
lapx-batch-mod-1t  ✅ PASS    98.545250  🏆 17.04x faster
lapx-loop-mod      ✅ PASS    98.666800  🏆 17.02x faster
lapx-batch-jvsa    ✅ PASS   111.622800  🏆 15.05x faster
lapx-batch-jvs     ✅ PASS   118.303250  🏆 14.20x faster
lapx-batch-jvxa    ✅ PASS   124.171600  🏆 13.52x faster
lapx-batch-jvsa64  ✅ PASS   124.519600  🏆 13.49x faster
lapx-batch-jvx     ✅ PASS   127.550300  🏆 13.17x faster
lapx-loop-jvh      ✅ PASS   350.773700  🏆 4.79x faster
lapx-loop-jvr      ✅ PASS   365.248250  🏆 4.60x faster
lapx-loop-jvs      ✅ PASS  1198.076800  🏆 1.40x faster
lapx-loop-jvx      ✅ PASS  1274.857650  🏆 1.32x faster
scipy-loop         ⭐ BASE  1679.376050  ⭐ baseline
---------------------------------------------------------

### Sparse 50 x (2000x2000) | target density=5.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    62.702850  🥇 82.62x faster
lapx-batch-jvr     ✅ PASS   218.108550  🥈 23.75x faster
lapx-batch-jvh     ✅ PASS   219.264850  🥉 23.63x faster
lapx-batch-jvsa    ✅ PASS   288.537500  🏆 17.95x faster
lapx-batch-jvs     ✅ PASS   298.977250  🏆 17.33x faster
lapx-batch-jvx     ✅ PASS   473.174750  🏆 10.95x faster
lapx-batch-jvxa    ✅ PASS   476.260250  🏆 10.88x faster
lapx-batch-jvsa64  ✅ PASS   492.263900  🏆 10.52x faster
lapx-batch-mod-1t  ✅ PASS   533.677250  🏆 9.71x faster
lapx-loop-mod      ✅ PASS   534.825200  🏆 9.69x faster
lapx-loop-jvr      ✅ PASS  1106.036300  🏆 4.68x faster
lapx-loop-jvh      ✅ PASS  1121.147850  🏆 4.62x faster
lapx-loop-jvs      ✅ PASS  2814.397850  🏆 1.84x faster
lapx-loop-jvx      ✅ PASS  3673.368250  🏆 1.41x faster
scipy-loop         ⭐ BASE  5180.332100  ⭐ baseline
---------------------------------------------------------
```

</details>

See the [single-matrix workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
and [batch workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml) for newer results across platforms.

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

The [tracking benchmark](benchmarks/benchmark_tracking.py) measures matched pairs and unmatched row and column indices.
Times include solving, pair construction where needed, threshold filtering, and unmatched-index creation.
All solvers use `return_cost=False`.

- `LAPX LAPJV-IFT` passes `cost_limit=thresh` to `lapjv` during optimization.
- The other rows, including SciPy, remove pairs above `thresh` after solving.

Each threshold produces two tables with up to four solvers each and a repeated Size column, followed by the overall ranking across all solvers.
`✓` means matched pairs and unmatched indices equal SciPy in every round; `✗` marks a difference in any round.
`LAPX LAPJV-IFT` can differ because its threshold is applied during optimization.
The overall ranking sums median times across sizes and counts each solver's placements with 🥇, 🥈, 🥉, 🚩, 🏳️, 🥴, 🗿, and 🙅‍♂️.
See [Cost values in the README](README.md#cost-values) for the distinction between the threshold methods.

The full run uses thresholds **0.05, 0.1, 0.5, 1.0, and 1e9**.
`--quick` uses **0.05 and 0.5** and omits 5000x5000.

```bash
python benchmark_tracking.py --quick --repeats 3 --seed 2026
```

<details><summary>📊 Historical tracking results (LAPX 0.12.0):</summary><br>

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.12.0
scipy==1.17.1
numpy==2.4.6
```

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new8\lapx\benchmarks>;python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 3rd  | 0.000037s ✗ 8th | 0.000034s ✓ 7th | 0.000034s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000040s ✗ 8th | 0.000037s ✓ 5th | 0.000037s ✓ 4th
50x50     | 0.000057s 6th  | 0.000069s ✗ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000143s 6th  | 0.000488s ✓ 7th | 0.000105s ✓ 4th | 0.000104s ✓ 3rd
250x250   | 0.001122s 7th  | 0.001061s ✗ 6th | 0.000373s ✓ 3rd | 0.000373s ✓ 4th
550x500   | 0.003433s 6th  | 0.011330s ✓ 7th | 0.001165s ✓ 5th | 0.001111s ✓ 4th
1000x1000 | 0.022538s 6th  | 0.041268s ✓ 8th | 0.016779s ✓ 5th | 0.015458s ✓ 3rd
2000x2500 | 0.037307s 6th  | 2.198385s ✓ 8th | 0.018181s ✓ 5th | 0.017995s ✓ 4th
5000x5000 | 1.194059s 6th  | 1.687990s ✓ 8th | 0.644453s ✓ 5th | 0.639976s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000032s ✓ 4th | 0.000033s ✓ 5th | 0.000029s ✓ 2nd | 0.000028s ✓ 1st
25x20     | 0.000038s ✓ 7th | 0.000037s ✓ 6th | 0.000030s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000063s ✓ 7th | 0.000047s ✓ 5th | 0.000038s ✓ 1st | 0.000038s ✓ 2nd
100x150   | 0.000643s ✓ 8th | 0.000106s ✓ 5th | 0.000064s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001170s ✓ 8th | 0.000406s ✓ 5th | 0.000260s ✓ 1st | 0.000270s ✓ 2nd
550x500   | 0.016613s ✓ 8th | 0.000890s ✓ 3rd | 0.000567s ✓ 1st | 0.000607s ✓ 2nd
1000x1000 | 0.025137s ✓ 7th | 0.015840s ✓ 4th | 0.004331s ✓ 2nd | 0.003881s ✓ 1st
2000x2500 | 1.744996s ✓ 7th | 0.012352s ✓ 3rd | 0.004122s ✓ 1st | 0.004746s ✓ 2nd
5000x5000 | 1.260760s ✓ 7th | 0.359101s ✓ 3rd | 0.283823s ✓ 2nd | 0.255105s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   264.7685 ms | ✅ | 🥇x4 🥈x5
     2. LAPX LAPJVR    :   293.2629 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJVS    :   388.8101 ms | ✅ | 🥉x3 🚩x1 🏳️x4 🥴x1
     4. LAPX LAPJVX    :   675.1331 ms | ✅ | 🥉x3 🚩x5 🥴x1
     5. LAPX LAPJV     :   681.1729 ms | ✅ | 🥉x1 🚩x2 🏳️x5 🗿x1
     6. BASELINE SciPy :  1258.7230 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3049.4534 ms | ✅ | 🚩x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3940.6672 ms | ⚠️ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000036s 5th  | 0.000037s ✗ 6th | 0.000037s ✓ 7th | 0.000036s ✓ 3rd
25x20     | 0.000036s 3rd  | 0.000044s ✗ 7th | 0.000041s ✓ 5th | 0.000045s ✓ 8th
50x50     | 0.000058s 6th  | 0.000068s ✗ 8th | 0.000048s ✓ 5th | 0.000046s ✓ 3rd
100x150   | 0.000139s 6th  | 0.000555s ✓ 7th | 0.000106s ✓ 3rd | 0.000106s ✓ 4th
250x250   | 0.001110s 6th  | 0.001115s ✓ 7th | 0.000368s ✓ 3rd | 0.000370s ✓ 4th
550x500   | 0.003480s 6th  | 0.011583s ✓ 7th | 0.001118s ✓ 5th | 0.001103s ✓ 4th
1000x1000 | 0.022875s 6th  | 0.040949s ✓ 8th | 0.015933s ✓ 5th | 0.015377s ✓ 3rd
2000x2500 | 0.037249s 6th  | 2.215920s ✓ 8th | 0.018344s ✓ 5th | 0.017868s ✓ 4th
5000x5000 | 1.193729s 6th  | 1.671245s ✓ 8th | 0.648547s ✓ 4th | 0.659007s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 4th | 0.000039s ✓ 8th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
25x20     | 0.000043s ✓ 6th | 0.000040s ✓ 4th | 0.000034s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000046s ✓ 4th | 0.000039s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000643s ✓ 8th | 0.000111s ✓ 5th | 0.000067s ✓ 1st | 0.000067s ✓ 2nd
250x250   | 0.001171s ✓ 8th | 0.000377s ✓ 5th | 0.000263s ✓ 2nd | 0.000259s ✓ 1st
550x500   | 0.016100s ✓ 8th | 0.000969s ✓ 3rd | 0.000562s ✓ 1st | 0.000610s ✓ 2nd
1000x1000 | 0.024523s ✓ 7th | 0.015900s ✓ 4th | 0.004093s ✓ 2nd | 0.004066s ✓ 1st
2000x2500 | 1.735488s ✓ 7th | 0.012393s ✓ 3rd | 0.004982s ✓ 2nd | 0.004198s ✓ 1st
5000x5000 | 1.270824s ✓ 7th | 0.382568s ✓ 3rd | 0.286228s ✓ 1st | 0.294470s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   296.2976 ms | ✅ | 🥇x4 🥈x5
     2. LAPX LAPJVH    :   303.7720 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJVS    :   412.4426 ms | ✅ | 🥉x3 🚩x3 🏳️x2 🙅‍♂️x1
     4. LAPX LAPJV     :   684.5437 ms | ✅ | 🥉x2 🚩x1 🏳️x5 🗿x1
     5. LAPX LAPJVX    :   693.9577 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🙅‍♂️x1
     6. BASELINE SciPy :  1258.7116 ms | ⭐ | 🥉x1 🏳️x1 🥴x7
     7. LAPX LAPJVC    :  3048.8910 ms | ✅ | 🚩x1 🥴x1 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3941.5162 ms | ⚠️ | 🥴x1 🗿x4 🙅‍♂️x4
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 3rd  | 0.000034s ✗ 7th | 0.000034s ✓ 5th | 0.000034s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000041s ✓ 8th | 0.000037s ✓ 6th | 0.000037s ✓ 5th
50x50     | 0.000057s 6th  | 0.000065s ✓ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000140s 6th  | 0.000585s ✓ 7th | 0.000108s ✓ 5th | 0.000104s ✓ 4th
250x250   | 0.001131s 7th  | 0.001112s ✓ 6th | 0.000377s ✓ 3rd | 0.000380s ✓ 4th
550x500   | 0.003780s 6th  | 0.011491s ✓ 7th | 0.001208s ✓ 5th | 0.001170s ✓ 4th
1000x1000 | 0.022703s 6th  | 0.041340s ✓ 8th | 0.016011s ✓ 5th | 0.015389s ✓ 3rd
2000x2500 | 0.037164s 6th  | 2.156848s ✓ 8th | 0.018247s ✓ 5th | 0.017835s ✓ 4th
5000x5000 | 1.190651s 6th  | 1.626757s ✓ 8th | 0.652195s ✓ 4th | 0.653386s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000039s ✓ 8th | 0.000032s ✓ 4th | 0.000028s ✓ 1st | 0.000029s ✓ 2nd
25x20     | 0.000038s ✓ 7th | 0.000037s ✓ 4th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000063s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000646s ✓ 8th | 0.000100s ✓ 3rd | 0.000066s ✓ 2nd | 0.000061s ✓ 1st
250x250   | 0.001195s ✓ 8th | 0.000398s ✓ 5th | 0.000271s ✓ 2nd | 0.000261s ✓ 1st
550x500   | 0.016237s ✓ 8th | 0.000994s ✓ 3rd | 0.000594s ✓ 1st | 0.000658s ✓ 2nd
1000x1000 | 0.024668s ✓ 7th | 0.015798s ✓ 4th | 0.004331s ✓ 2nd | 0.004053s ✓ 1st
2000x2500 | 1.747332s ✓ 7th | 0.012437s ✓ 3rd | 0.004752s ✓ 2nd | 0.004733s ✓ 1st
5000x5000 | 1.227156s ✓ 7th | 0.380197s ✓ 3rd | 0.285496s ✓ 2nd | 0.282938s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   292.8003 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   295.6088 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVS    :   410.0387 ms | ✅ | 🥉x4 🚩x3 🏳️x2
     4. LAPX LAPJV     :   688.2636 ms | ✅ | 🥉x1 🚩x2 🏳️x5 🥴x1
     5. LAPX LAPJVX    :   688.3793 ms | ✅ | 🥉x2 🚩x4 🏳️x2 🥴x1
     6. BASELINE SciPy :  1255.6901 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3017.3743 ms | ✅ | 🗿x5 🙅‍♂️x4
     8. LAPX LAPJV-IFT :  3838.2731 ms | ⚠️ | 🥴x1 🗿x3 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 3rd  | 0.000036s ✓ 8th | 0.000034s ✓ 7th | 0.000033s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000047s ✓ 8th | 0.000038s ✓ 5th | 0.000038s ✓ 4th
50x50     | 0.000057s 6th  | 0.000065s ✓ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000137s 6th  | 0.000586s ✓ 7th | 0.000103s ✓ 4th | 0.000103s ✓ 5th
250x250   | 0.001117s 6th  | 0.001248s ✓ 8th | 0.000387s ✓ 4th | 0.000387s ✓ 3rd
550x500   | 0.003456s 6th  | 0.011404s ✓ 7th | 0.001107s ✓ 4th | 0.001120s ✓ 5th
1000x1000 | 0.022746s 6th  | 0.041436s ✓ 8th | 0.015965s ✓ 5th | 0.015516s ✓ 3rd
2000x2500 | 0.037295s 6th  | 2.235364s ✓ 8th | 0.018305s ✓ 5th | 0.018269s ✓ 4th
5000x5000 | 1.200903s 7th  | 1.767934s ✓ 8th | 0.660634s ✓ 5th | 0.639486s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000033s ✓ 5th | 0.000032s ✓ 4th | 0.000028s ✓ 1st | 0.000028s ✓ 2nd
25x20     | 0.000039s ✓ 7th | 0.000038s ✓ 6th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000062s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 1st | 0.000038s ✓ 2nd
100x150   | 0.000643s ✓ 8th | 0.000101s ✓ 3rd | 0.000063s ✓ 2nd | 0.000061s ✓ 1st
250x250   | 0.001191s ✓ 7th | 0.000401s ✓ 5th | 0.000260s ✓ 1st | 0.000263s ✓ 2nd
550x500   | 0.016150s ✓ 8th | 0.000930s ✓ 3rd | 0.000556s ✓ 1st | 0.000604s ✓ 2nd
1000x1000 | 0.025347s ✓ 7th | 0.015906s ✓ 4th | 0.004081s ✓ 1st | 0.004307s ✓ 2nd
2000x2500 | 1.755673s ✓ 7th | 0.012671s ✓ 3rd | 0.004796s ✓ 1st | 0.005239s ✓ 2nd
5000x5000 | 1.198716s ✓ 6th | 0.366353s ✓ 3rd | 0.286645s ✓ 2nd | 0.270806s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   281.3768 ms | ✅ | 🥇x2 🥈x7
     2. LAPX LAPJVR    :   296.4990 ms | ✅ | 🥇x7 🥈x2
     3. LAPX LAPJVS    :   396.4773 ms | ✅ | 🥉x4 🚩x2 🏳️x2 🥴x1
     4. LAPX LAPJVX    :   674.9970 ms | ✅ | 🥉x3 🚩x3 🏳️x2 🥴x1
     5. LAPX LAPJV     :   696.6178 ms | ✅ | 🚩x4 🏳️x4 🗿x1
     6. BASELINE SciPy :  1265.7744 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  2997.8541 ms | ✅ | 🏳️x1 🥴x1 🗿x5 🙅‍♂️x2
     8. LAPX LAPJV-IFT :  4058.1205 ms | ✅ | 🗿x2 🙅‍♂️x7
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000031s 2nd  | 0.000043s ✓ 8th | 0.000035s ✓ 7th | 0.000035s ✓ 6th
25x20     | 0.000035s 3rd  | 0.000042s ✓ 8th | 0.000040s ✓ 6th | 0.000039s ✓ 4th
50x50     | 0.000057s 6th  | 0.000065s ✓ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000139s 6th  | 0.000565s ✓ 7th | 0.000108s ✓ 5th | 0.000106s ✓ 4th
250x250   | 0.001121s 7th  | 0.001096s ✓ 6th | 0.000369s ✓ 4th | 0.000368s ✓ 3rd
550x500   | 0.003380s 6th  | 0.010552s ✓ 7th | 0.001034s ✓ 5th | 0.001030s ✓ 4th
1000x1000 | 0.023839s 6th  | 0.040457s ✓ 8th | 0.015511s ✓ 4th | 0.014911s ✓ 3rd
2000x2500 | 0.037135s 6th  | 2.182798s ✓ 8th | 0.018318s ✓ 4th | 0.018369s ✓ 5th
5000x5000 | 1.191931s 6th  | 1.767331s ✓ 8th | 0.654660s ✓ 5th | 0.643363s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000035s ✓ 5th | 0.000034s ✓ 4th | 0.000034s ✓ 3rd | 0.000030s ✓ 1st
25x20     | 0.000040s ✓ 5th | 0.000040s ✓ 7th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000047s ✓ 5th | 0.000038s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000636s ✓ 8th | 0.000104s ✓ 3rd | 0.000063s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001157s ✓ 8th | 0.000377s ✓ 5th | 0.000265s ✓ 2nd | 0.000261s ✓ 1st
550x500   | 0.016074s ✓ 8th | 0.000883s ✓ 3rd | 0.000557s ✓ 1st | 0.000600s ✓ 2nd
1000x1000 | 0.024278s ✓ 7th | 0.015701s ✓ 5th | 0.004071s ✓ 2nd | 0.004025s ✓ 1st
2000x2500 | 1.688586s ✓ 7th | 0.012470s ✓ 3rd | 0.004930s ✓ 2nd | 0.004742s ✓ 1st
5000x5000 | 1.276012s ✓ 7th | 0.381172s ✓ 3rd | 0.280801s ✓ 1st | 0.283706s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   290.7931 ms | ✅ | 🥇x3 🥈x5 🥉x1
     2. LAPX LAPJVH    :   293.4980 ms | ✅ | 🥇x6 🥈x3
     3. LAPX LAPJVS    :   410.8287 ms | ✅ | 🥉x4 🚩x1 🏳️x3 🗿x1
     4. LAPX LAPJVX    :   678.2651 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🥴x1
     5. LAPX LAPJV     :   690.1214 ms | ✅ | 🚩x4 🏳️x3 🥴x1 🗿x1
     6. BASELINE SciPy :  1257.6678 ms | ⭐ | 🥈x1 🥉x1 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3006.8808 ms | ✅ | 🏳️x2 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  4002.9470 ms | ✅ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these historical runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. R/H have the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
