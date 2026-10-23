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

### Historical results (LAPX 0.11.0)

R/H single and batch results use float64 costs and `return_cost=False`.
See each case for matrix sizes, thread counts, and timing settings.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.14.9.

```
lapx==0.11.0
scipy==1.18.1
numpy==2.5.4
```

<details><summary>📄 Historical single results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new7\lapx\benchmarks>python benchmark_single.py


Note: R/H native float64, JVS default float32.


### Matrix 4 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.000488  🥇 3.52x faster
lapjvr   ✅ PASS   0.000500  🥈 3.43x faster
scipy    ⭐ BASE   0.001716  ⭐ baseline
lapjvc   ✅ PASS   0.003896  🐌 2.27x slower
lapjvxa  ✅ PASS   0.005112  🐌 2.98x slower
lapjvs   ✅ PASS   0.005696  🐌 3.32x slower
lapjvx   ✅ PASS   0.006024  🐌 3.51x slower
lapjv    ✅ PASS   0.006200  🐌 3.61x slower
lapjvsa  ✅ PASS   0.006964  🐌 4.06x slower
--------------------------------------------

### Matrix 5 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000536  🥇 3.31x faster
lapjvh   ✅ PASS   0.000548  🥈 3.24x faster
lapjvsa  ✅ PASS   0.001364  🥉 1.30x faster
scipy    ⭐ BASE   0.001776  ⭐ baseline
lapjvxa  ✅ PASS   0.003120  🐌 1.76x slower
lapjvx   ✅ PASS   0.003824  🐌 2.15x slower
lapjvc   ✅ PASS   0.003988  🐌 2.25x slower
lapjvs   ✅ PASS   0.004096  🐌 2.31x slower
lapjv    ✅ PASS   0.004212  🐌 2.37x slower
--------------------------------------------

### Matrix 5 x 6 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.000528  🥇 3.36x faster
lapjvr   ✅ PASS   0.000532  🥈 3.33x faster
scipy    ⭐ BASE   0.001772  ⭐ baseline
lapjvc   ✅ PASS   0.004008  🐌 2.26x slower
lapjvxa  ✅ PASS   0.005200  🐌 2.93x slower
lapjvs   ✅ PASS   0.005764  🐌 3.25x slower
lapjvx   ✅ PASS   0.005880  🐌 3.32x slower
lapjv    ✅ PASS   0.006248  🐌 3.53x slower
lapjvsa  ✅ PASS   0.007280  🐌 4.11x slower
--------------------------------------------

### Matrix 45 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.002760  🥇 5.54x faster
lapjvh   ✅ PASS   0.003576  🥈 4.28x faster
lapjvxa  ✅ PASS   0.011260  🥉 1.36x faster
lapjvs   ✅ PASS   0.011776  🏆 1.30x faster
lapjvx   ✅ PASS   0.012048  🏆 1.27x faster
lapjv    ✅ PASS   0.012324  🏆 1.24x faster
lapjvsa  ✅ PASS   0.013368  🏆 1.14x faster
scipy    ⭐ BASE   0.015292  ⭐ baseline
lapjvc   ✅ PASS   0.038472  🐌 2.52x slower
--------------------------------------------

### Matrix 50 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.005412  🥇 4.00x faster
lapjvr   ✅ PASS   0.005716  🥈 3.79x faster
lapjvsa  ✅ PASS   0.009676  🥉 2.24x faster
lapjvx   ✅ PASS   0.010284  🏆 2.10x faster
lapjvxa  ✅ PASS   0.010480  🏆 2.07x faster
lapjv    ✅ PASS   0.010852  🏆 1.99x faster
lapjvs   ✅ PASS   0.013816  🏆 1.57x faster
scipy    ⭐ BASE   0.021644  ⭐ baseline
lapjvc   ✅ PASS   0.030884  🐌 1.43x slower
--------------------------------------------

### Matrix 50 x 55 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.003044  🥇 6.44x faster
lapjvh   ✅ PASS   0.003352  🥈 5.85x faster
lapjvs   ✅ PASS   0.011796  🥉 1.66x faster
lapjvx   ✅ PASS   0.012740  🏆 1.54x faster
lapjvxa  ✅ PASS   0.013424  🏆 1.46x faster
lapjv    ✅ PASS   0.014484  🏆 1.35x faster
lapjvsa  ✅ PASS   0.015524  🏆 1.26x faster
scipy    ⭐ BASE   0.019600  ⭐ baseline
lapjvc   ✅ PASS   0.052436  🐌 2.68x slower
--------------------------------------------

### Matrix 450 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.324700  🥇 6.69x faster
lapjvr   ✅ PASS   0.329300  🥈 6.60x faster
lapjvs   ✅ PASS   0.545600  🥉 3.98x faster
lapjvsa  ✅ PASS   0.573300  🏆 3.79x faster
lapjvxa  ✅ PASS   0.783300  🏆 2.77x faster
lapjvx   ✅ PASS   0.788800  🏆 2.75x faster
lapjv    ✅ PASS   0.811600  🏆 2.68x faster
scipy    ⭐ BASE   2.172800  ⭐ baseline
lapjvc   ✅ PASS  10.694800  🐌 4.92x slower
--------------------------------------------

### Matrix 500 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.894300  🥇 5.75x faster
lapjvh   ✅ PASS   0.989000  🥈 5.20x faster
lapjvxa  ✅ PASS   2.081700  🥉 2.47x faster
lapjvx   ✅ PASS   2.108700  🏆 2.44x faster
lapjv    ✅ PASS   2.147700  🏆 2.40x faster
lapjvsa  ✅ PASS   2.157800  🏆 2.38x faster
lapjvs   ✅ PASS   2.162500  🏆 2.38x faster
lapjvc   ✅ PASS   4.752600  🏆 1.08x faster
scipy    ⭐ BASE   5.144600  ⭐ baseline
--------------------------------------------

### Matrix 500 x 550 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.385900  🥇 6.92x faster
lapjvr   ✅ PASS   0.389000  🥈 6.86x faster
lapjvs   ✅ PASS   0.805000  🥉 3.31x faster
lapjvsa  ✅ PASS   0.809500  🏆 3.30x faster
lapjv    ✅ PASS   0.959300  🏆 2.78x faster
lapjvxa  ✅ PASS   0.978900  🏆 2.73x faster
lapjvx   ✅ PASS   1.077800  🏆 2.48x faster
scipy    ⭐ BASE   2.668500  ⭐ baseline
lapjvc   ✅ PASS  14.085000  🐌 5.28x slower
--------------------------------------------

### Matrix 2500 x 5000 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS      6.983100  🥇 7.52x faster
lapjvh   ✅ PASS      7.138900  🥈 7.36x faster
scipy    ⭐ BASE     52.539300  ⭐ baseline
lapjvs   ✅ PASS     60.962500  🐌 1.16x slower
lapjvsa  ✅ PASS     61.274900  🐌 1.17x slower
lapjvx   ✅ PASS     85.649500  🐌 1.63x slower
lapjv    ✅ PASS     87.046500  🐌 1.66x slower
lapjvxa  ✅ PASS     91.306800  🐌 1.74x slower
lapjvc   ✅ PASS  12517.109400  🐌 238.24x slower
-------------------------------------------------

### Matrix 5000 x 5000 | float64 | return_cost=False

Solver   Check      Time (ms)  vs SciPy
----------------------------------------------
lapjvh   ✅ PASS   235.464900  🥇 4.35x faster
lapjvr   ✅ PASS   239.323500  🥈 4.28x faster
lapjvsa  ✅ PASS   359.248200  🥉 2.85x faster
lapjvs   ✅ PASS   364.733500  🏆 2.81x faster
lapjvx   ✅ PASS   543.909700  🏆 1.88x faster
lapjvxa  ✅ PASS   565.998200  🏆 1.81x faster
lapjv    ✅ PASS   598.592800  🏆 1.71x faster
scipy    ⭐ BASE  1023.112300  ⭐ baseline
lapjvc   ✅ PASS  1249.847500  🐌 1.22x slower
----------------------------------------------

### Matrix 5000 x 7500 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS     23.695700  🥇 8.05x faster
lapjvh   ✅ PASS     29.466100  🥈 6.47x faster
lapjvsa  ✅ PASS    112.201000  🥉 1.70x faster
lapjvs   ✅ PASS    121.401900  🏆 1.57x faster
lapjvx   ✅ PASS    167.805400  🏆 1.14x faster
lapjv    ✅ PASS    168.619800  🏆 1.13x faster
lapjvxa  ✅ PASS    171.351900  🏆 1.11x faster
scipy    ⭐ BASE    190.639600  ⭐ baseline
lapjvc   ✅ PASS  54863.495300  🐌 287.79x slower
-------------------------------------------------
```

</details>

<details><summary>🗂️ Historical batch results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new7\lapx\benchmarks>python benchmark_batch.py


Note: R/H native float64, JVS default float32, jvsa64 float64.


### Dense 10 x (4000x4000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   304.373900  🥇 21.05x faster
lapx-batch-jvr     ✅ PASS   306.779700  🥈 20.88x faster
lapx-batch-jvsa    ✅ PASS   412.044300  🥉 15.55x faster
lapx-batch-jvs     ✅ PASS   418.882600  🏆 15.29x faster
lapx-batch-jvx     ✅ PASS  1057.962900  🏆 6.06x faster
lapx-batch-jvxa    ✅ PASS  1067.470000  🏆 6.00x faster
lapx-batch-jvsa64  ✅ PASS  1135.725900  🏆 5.64x faster
lapx-loop-jvh      ✅ PASS  1583.873000  🏆 4.04x faster
lapx-loop-jvr      ✅ PASS  1592.022500  🏆 4.02x faster
lapx-loop-jvs      ✅ PASS  2630.187800  🏆 2.44x faster
lapx-loop-jvx      ✅ PASS  5215.012000  🏆 1.23x faster
scipy-loop         ⭐ BASE  6406.714800  ⭐ baseline
---------------------------------------------------------

### Dense 20 x (3000x2000) | n_threads=0 | return_cost=False

Solver             Check     Time (ms)  vs SciPy
--------------------------------------------------------
lapx-batch-jvh     ✅ PASS   81.211000  🥇 12.09x faster
lapx-batch-jvsa    ✅ PASS   84.556500  🥈 11.61x faster
lapx-batch-jvr     ✅ PASS   85.890000  🥉 11.43x faster
lapx-batch-jvs     ✅ PASS   91.441600  🏆 10.73x faster
lapx-batch-jvxa    ✅ PASS  137.755600  🏆 7.13x faster
lapx-batch-jvsa64  ✅ PASS  138.859300  🏆 7.07x faster
lapx-batch-jvx     ✅ PASS  140.613500  🏆 6.98x faster
lapx-loop-jvh      ✅ PASS  304.508100  🏆 3.22x faster
lapx-loop-jvr      ✅ PASS  318.334400  🏆 3.08x faster
lapx-loop-jvs      ✅ PASS  816.990100  🏆 1.20x faster
lapx-loop-jvx      ✅ PASS  981.166300  🏆 1.00x faster
scipy-loop         ⭐ BASE  981.617400  ⭐ baseline
--------------------------------------------------------

### Dense 50 x (2000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   216.664050  🥇 26.64x faster
lapx-batch-jvr     ✅ PASS   223.283500  🥈 25.85x faster
lapx-batch-jvsa    ✅ PASS   310.737850  🥉 18.57x faster
lapx-batch-jvs     ✅ PASS   317.789550  🏆 18.16x faster
lapx-batch-jvx     ✅ PASS   450.444450  🏆 12.81x faster
lapx-batch-jvsa64  ✅ PASS   463.391400  🏆 12.45x faster
lapx-batch-jvxa    ✅ PASS   466.151250  🏆 12.38x faster
lapx-loop-jvr      ✅ PASS  1187.665500  🏆 4.86x faster
lapx-loop-jvh      ✅ PASS  1196.546400  🏆 4.82x faster
lapx-loop-jvs      ✅ PASS  2951.465500  🏆 1.96x faster
lapx-loop-jvx      ✅ PASS  3769.312100  🏆 1.53x faster
scipy-loop         ⭐ BASE  5771.276800  ⭐ baseline
---------------------------------------------------------

### Dense 100 x (1000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvr     ✅ PASS    20.475000  🥇 41.55x faster
lapx-batch-jvh     ✅ PASS    20.880550  🥈 40.75x faster
lapx-loop-jvr      ✅ PASS   101.692050  🥉 8.37x faster
lapx-loop-jvh      ✅ PASS   116.548300  🏆 7.30x faster
lapx-batch-jvs     ✅ PASS   131.421600  🏆 6.47x faster
lapx-batch-jvsa    ✅ PASS   140.168250  🏆 6.07x faster
lapx-batch-jvx     ✅ PASS   232.292800  🏆 3.66x faster
lapx-batch-jvsa64  ✅ PASS   236.849150  🏆 3.59x faster
lapx-batch-jvxa    ✅ PASS   244.396350  🏆 3.48x faster
lapx-loop-jvs      ✅ PASS   817.702400  🏆 1.04x faster
scipy-loop         ⭐ BASE   850.819200  ⭐ baseline
lapx-loop-jvx      ✅ PASS  1317.432500  🐌 1.55x slower
---------------------------------------------------------

### Dense 500 x (1000x1000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check       Time (ms)  vs SciPy
----------------------------------------------------------
lapx-batch-jvh     ✅ PASS    308.471100  🥇 36.16x faster
lapx-batch-jvr     ✅ PASS    311.741500  🥈 35.78x faster
lapx-batch-jvsa    ✅ PASS    532.438650  🥉 20.95x faster
lapx-batch-jvs     ✅ PASS    538.589650  🏆 20.71x faster
lapx-batch-jvxa    ✅ PASS    582.558100  🏆 19.15x faster
lapx-batch-jvsa64  ✅ PASS    583.035200  🏆 19.13x faster
lapx-batch-jvx     ✅ PASS    590.473200  🏆 18.89x faster
lapx-loop-jvh      ✅ PASS   2150.498500  🏆 5.19x faster
lapx-loop-jvr      ✅ PASS   2178.718250  🏆 5.12x faster
lapx-loop-jvs      ✅ PASS   6592.866350  🏆 1.69x faster
lapx-loop-jvx      ✅ PASS   6809.711100  🏆 1.64x faster
scipy-loop         ⭐ BASE  11154.971100  ⭐ baseline
----------------------------------------------------------

### Sparse 100 x (1000x1000) | target density=1.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    17.754200  🥇 93.88x faster
lapx-batch-jvh     ✅ PASS    60.306900  🥈 27.64x faster
lapx-batch-jvr     ✅ PASS    61.104550  🥉 27.28x faster
lapx-batch-mod-1t  ✅ PASS    98.382100  🏆 16.94x faster
lapx-loop-mod      ✅ PASS    99.308150  🏆 16.78x faster
lapx-batch-jvsa    ✅ PASS   110.353850  🏆 15.10x faster
lapx-batch-jvs     ✅ PASS   118.678200  🏆 14.04x faster
lapx-batch-jvsa64  ✅ PASS   123.169300  🏆 13.53x faster
lapx-batch-jvxa    ✅ PASS   124.200700  🏆 13.42x faster
lapx-batch-jvx     ✅ PASS   126.765050  🏆 13.15x faster
lapx-loop-jvh      ✅ PASS   340.511150  🏆 4.89x faster
lapx-loop-jvr      ✅ PASS   362.495800  🏆 4.60x faster
lapx-loop-jvs      ✅ PASS  1186.090950  🏆 1.41x faster
lapx-loop-jvx      ✅ PASS  1267.239600  🏆 1.32x faster
scipy-loop         ⭐ BASE  1666.677550  ⭐ baseline
---------------------------------------------------------

### Sparse 50 x (2000x2000) | target density=5.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    58.790100  🥇 86.00x faster
lapx-batch-jvr     ✅ PASS   211.135250  🥈 23.95x faster
lapx-batch-jvh     ✅ PASS   216.405900  🥉 23.36x faster
lapx-batch-jvs     ✅ PASS   279.922600  🏆 18.06x faster
lapx-batch-jvsa    ✅ PASS   286.573600  🏆 17.64x faster
lapx-batch-jvx     ✅ PASS   471.404800  🏆 10.73x faster
lapx-batch-jvsa64  ✅ PASS   475.835200  🏆 10.63x faster
lapx-batch-jvxa    ✅ PASS   476.329050  🏆 10.61x faster
lapx-batch-mod-1t  ✅ PASS   538.098350  🏆 9.40x faster
lapx-loop-mod      ✅ PASS   540.663300  🏆 9.35x faster
lapx-loop-jvh      ✅ PASS  1084.536200  🏆 4.66x faster
lapx-loop-jvr      ✅ PASS  1105.791450  🏆 4.57x faster
lapx-loop-jvs      ✅ PASS  2831.622850  🏆 1.79x faster
lapx-loop-jvx      ✅ PASS  3679.481800  🏆 1.37x faster
scipy-loop         ⭐ BASE  5056.133650  ⭐ baseline
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

<details><summary>📊 Historical tracking results (LAPX 0.11.0):</summary><br>

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.14.9.

```
lapx==0.11.0
scipy==1.18.1
numpy==2.5.4
```

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new7\lapx\benchmarks>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000032s 3rd  | 0.000037s ✗ 7th | 0.000037s ✓ 6th | 0.000041s ✓ 8th
25x20     | 0.000036s 3rd  | 0.000043s ✗ 8th | 0.000041s ✓ 6th | 0.000041s ✓ 4th
50x50     | 0.000057s 6th  | 0.000069s ✗ 7th | 0.000049s ✓ 4th | 0.000048s ✓ 3rd
100x150   | 0.000135s 6th  | 0.000484s ✓ 7th | 0.000111s ✓ 4th | 0.000115s ✓ 5th
250x250   | 0.001084s 7th  | 0.000983s ✗ 6th | 0.000372s ✓ 4th | 0.000372s ✓ 3rd
550x500   | 0.003534s 6th  | 0.010435s ✓ 7th | 0.001052s ✓ 4th | 0.001269s ✓ 5th
1000x1000 | 0.022508s 6th  | 0.039511s ✓ 8th | 0.015355s ✓ 4th | 0.014907s ✓ 3rd
2000x2500 | 0.035372s 6th  | 2.196133s ✓ 8th | 0.017676s ✓ 4th | 0.017732s ✓ 5th
5000x5000 | 1.046945s 6th  | 1.606948s ✓ 8th | 0.594579s ✓ 4th | 0.611765s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 4th | 0.000036s ✓ 5th | 0.000032s ✓ 2nd | 0.000031s ✓ 1st
25x20     | 0.000042s ✓ 7th | 0.000041s ✓ 5th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000071s ✓ 8th | 0.000049s ✓ 5th | 0.000040s ✓ 1st | 0.000041s ✓ 2nd
100x150   | 0.000635s ✓ 8th | 0.000102s ✓ 3rd | 0.000067s ✓ 2nd | 0.000064s ✓ 1st
250x250   | 0.001165s ✓ 8th | 0.000419s ✓ 5th | 0.000271s ✓ 2nd | 0.000266s ✓ 1st
550x500   | 0.016811s ✓ 8th | 0.000907s ✓ 3rd | 0.000596s ✓ 1st | 0.000599s ✓ 2nd
1000x1000 | 0.024380s ✓ 7th | 0.015788s ✓ 5th | 0.003965s ✓ 1st | 0.004103s ✓ 2nd
2000x2500 | 1.711926s ✓ 7th | 0.012207s ✓ 3rd | 0.004667s ✓ 2nd | 0.004632s ✓ 1st
5000x5000 | 1.290043s ✓ 7th | 0.381001s ✓ 3rd | 0.275467s ✓ 2nd | 0.275259s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   285.0273 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   285.1385 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVS    :   410.5493 ms | ✅ | 🥉x4 🏳️x5
     4. LAPX LAPJV     :   629.2728 ms | ✅ | 🚩x7 🥴x2
     5. LAPX LAPJVX    :   646.2896 ms | ✅ | 🥉x3 🚩x1 🏳️x4 🙅‍♂️x1
     6. BASELINE SciPy :  1109.7030 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3045.1094 ms | ✅ | 🚩x1 🗿x4 🙅‍♂️x4
     8. LAPX LAPJV-IFT :  3854.6450 ms | ⚠️ | 🥴x1 🗿x4 🙅‍♂️x4
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000034s 3rd  | 0.000037s ✗ 6th | 0.000037s ✓ 7th | 0.000038s ✓ 8th
25x20     | 0.000036s 3rd  | 0.000044s ✗ 8th | 0.000040s ✓ 5th | 0.000040s ✓ 4th
50x50     | 0.000058s 6th  | 0.000071s ✗ 8th | 0.000052s ✓ 5th | 0.000050s ✓ 4th
100x150   | 0.000137s 6th  | 0.000556s ✓ 7th | 0.000106s ✓ 4th | 0.000109s ✓ 5th
250x250   | 0.001102s 6th  | 0.001137s ✓ 7th | 0.000379s ✓ 4th | 0.000378s ✓ 3rd
550x500   | 0.003374s 6th  | 0.011250s ✓ 7th | 0.001098s ✓ 4th | 0.001105s ✓ 5th
1000x1000 | 0.022485s 6th  | 0.041315s ✓ 8th | 0.017454s ✓ 5th | 0.015380s ✓ 3rd
2000x2500 | 0.035627s 6th  | 2.121254s ✓ 8th | 0.017993s ✓ 5th | 0.017760s ✓ 4th
5000x5000 | 1.145999s 6th  | 1.734274s ✓ 8th | 0.660984s ✓ 5th | 0.651273s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 4th | 0.000036s ✓ 5th | 0.000032s ✓ 2nd | 0.000031s ✓ 1st
25x20     | 0.000042s ✓ 7th | 0.000041s ✓ 6th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000068s ✓ 7th | 0.000050s ✓ 3rd | 0.000040s ✓ 1st | 0.000040s ✓ 2nd
100x150   | 0.000750s ✓ 8th | 0.000105s ✓ 3rd | 0.000066s ✓ 2nd | 0.000066s ✓ 1st
250x250   | 0.001184s ✓ 8th | 0.000423s ✓ 5th | 0.000264s ✓ 1st | 0.000268s ✓ 2nd
550x500   | 0.016513s ✓ 8th | 0.000932s ✓ 3rd | 0.000569s ✓ 1st | 0.000596s ✓ 2nd
1000x1000 | 0.025038s ✓ 7th | 0.016192s ✓ 4th | 0.004081s ✓ 2nd | 0.004028s ✓ 1st
2000x2500 | 1.712588s ✓ 7th | 0.012513s ✓ 3rd | 0.004677s ✓ 2nd | 0.004672s ✓ 1st
5000x5000 | 1.324406s ✓ 7th | 0.382083s ✓ 3rd | 0.281953s ✓ 2nd | 0.280742s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   290.4740 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   291.7147 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVS    :   412.3745 ms | ✅ | 🥉x5 🚩x1 🏳️x2 🥴x1
     4. LAPX LAPJVX    :   686.1327 ms | ✅ | 🥉x2 🚩x4 🏳️x2 🙅‍♂️x1
     5. LAPX LAPJV     :   698.1436 ms | ✅ | 🚩x3 🏳️x5 🗿x1
     6. BASELINE SciPy :  1208.8507 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3080.6249 ms | ✅ | 🚩x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3909.9385 ms | ⚠️ | 🥴x1 🗿x3 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000032s 3rd  | 0.000036s ✗ 7th | 0.000035s ✓ 6th | 0.000039s ✓ 8th
25x20     | 0.000035s 2nd  | 0.000044s ✓ 8th | 0.000040s ✓ 6th | 0.000040s ✓ 5th
50x50     | 0.000058s 6th  | 0.000074s ✓ 8th | 0.000050s ✓ 5th | 0.000048s ✓ 3rd
100x150   | 0.000140s 6th  | 0.000593s ✓ 7th | 0.000107s ✓ 4th | 0.000111s ✓ 5th
250x250   | 0.001098s 6th  | 0.001249s ✓ 8th | 0.000429s ✓ 4th | 0.000370s ✓ 3rd
550x500   | 0.003409s 6th  | 0.011595s ✓ 7th | 0.001141s ✓ 5th | 0.001106s ✓ 4th
1000x1000 | 0.022501s 6th  | 0.041240s ✓ 8th | 0.015979s ✓ 4th | 0.015414s ✓ 3rd
2000x2500 | 0.033845s 6th  | 1.929752s ✓ 8th | 0.016452s ✓ 4th | 0.018432s ✓ 5th
5000x5000 | 1.087981s 6th  | 1.580324s ✓ 8th | 0.556389s ✓ 5th | 0.546557s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000035s ✓ 4th | 0.000035s ✓ 5th | 0.000030s ✓ 1st | 0.000030s ✓ 2nd
25x20     | 0.000041s ✓ 7th | 0.000039s ✓ 4th | 0.000033s ✓ 1st | 0.000036s ✓ 3rd
50x50     | 0.000064s ✓ 7th | 0.000049s ✓ 4th | 0.000039s ✓ 1st | 0.000040s ✓ 2nd
100x150   | 0.000636s ✓ 8th | 0.000105s ✓ 3rd | 0.000069s ✓ 2nd | 0.000063s ✓ 1st
250x250   | 0.001184s ✓ 7th | 0.000502s ✓ 5th | 0.000262s ✓ 1st | 0.000295s ✓ 2nd
550x500   | 0.016453s ✓ 8th | 0.000923s ✓ 3rd | 0.000592s ✓ 1st | 0.000675s ✓ 2nd
1000x1000 | 0.024943s ✓ 7th | 0.016259s ✓ 5th | 0.004075s ✓ 1st | 0.004079s ✓ 2nd
2000x2500 | 1.639204s ✓ 7th | 0.011577s ✓ 3rd | 0.004113s ✓ 2nd | 0.004088s ✓ 1st
5000x5000 | 1.277633s ✓ 7th | 0.363599s ✓ 3rd | 0.255808s ✓ 2nd | 0.249738s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   259.0425 ms | ✅ | 🥇x3 🥈x5 🥉x1
     2. LAPX LAPJVR    :   265.0206 ms | ✅ | 🥇x6 🥈x3
     3. LAPX LAPJVS    :   393.0881 ms | ✅ | 🥉x4 🚩x2 🏳️x3
     4. LAPX LAPJVX    :   582.1161 ms | ✅ | 🥉x3 🚩x2 🏳️x3 🙅‍♂️x1
     5. LAPX LAPJV     :   590.6223 ms | ✅ | 🚩x4 🏳️x3 🥴x2
     6. BASELINE SciPy :  1149.0976 ms | ⭐ | 🥈x1 🥉x1 🥴x7
     7. LAPX LAPJVC    :  2960.1915 ms | ✅ | 🚩x1 🗿x6 🙅‍♂️x2
     8. LAPX LAPJV-IFT :  3564.9076 ms | ⚠️ | 🗿x3 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000032s 3rd  | 0.000036s ✓ 7th | 0.000036s ✓ 6th | 0.000036s ✓ 5th
25x20     | 0.000035s 3rd  | 0.000044s ✓ 8th | 0.000041s ✓ 5th | 0.000041s ✓ 6th
50x50     | 0.000055s 6th  | 0.000067s ✓ 8th | 0.000048s ✓ 4th | 0.000047s ✓ 3rd
100x150   | 0.000144s 6th  | 0.000597s ✓ 7th | 0.000109s ✓ 4th | 0.000110s ✓ 5th
250x250   | 0.001092s 6th  | 0.001135s ✓ 7th | 0.000367s ✓ 3rd | 0.000379s ✓ 4th
550x500   | 0.003347s 6th  | 0.010704s ✓ 7th | 0.001120s ✓ 5th | 0.001118s ✓ 4th
1000x1000 | 0.022431s 6th  | 0.039612s ✓ 8th | 0.015348s ✓ 4th | 0.014943s ✓ 3rd
2000x2500 | 0.035328s 6th  | 2.170211s ✓ 8th | 0.018410s ✓ 5th | 0.018250s ✓ 4th
5000x5000 | 1.129035s 6th  | 1.656052s ✓ 8th | 0.590073s ✓ 5th | 0.568115s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000035s ✓ 4th | 0.000044s ✓ 8th | 0.000030s ✓ 1st | 0.000030s ✓ 2nd
25x20     | 0.000041s ✓ 7th | 0.000041s ✓ 4th | 0.000032s ✓ 2nd | 0.000032s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000049s ✓ 5th | 0.000039s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000635s ✓ 8th | 0.000106s ✓ 3rd | 0.000067s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001186s ✓ 8th | 0.000392s ✓ 5th | 0.000259s ✓ 1st | 0.000264s ✓ 2nd
550x500   | 0.016309s ✓ 8th | 0.000936s ✓ 3rd | 0.000569s ✓ 1st | 0.000608s ✓ 2nd
1000x1000 | 0.024233s ✓ 7th | 0.016284s ✓ 5th | 0.004089s ✓ 2nd | 0.004025s ✓ 1st
2000x2500 | 1.745250s ✓ 7th | 0.012813s ✓ 3rd | 0.004110s ✓ 1st | 0.004657s ✓ 2nd
5000x5000 | 1.307515s ✓ 7th | 0.385126s ✓ 3rd | 0.278854s ✓ 2nd | 0.252021s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   261.7399 ms | ✅ | 🥇x4 🥈x5
     2. LAPX LAPJVR    :   288.0496 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJVS    :   415.7905 ms | ✅ | 🥉x4 🚩x1 🏳️x3 🙅‍♂️x1
     4. LAPX LAPJVX    :   603.0376 ms | ✅ | 🥉x2 🚩x4 🏳️x2 🥴x1
     5. LAPX LAPJV     :   625.5504 ms | ✅ | 🥉x1 🚩x3 🏳️x4 🥴x1
     6. BASELINE SciPy :  1191.4983 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3095.2688 ms | ✅ | 🚩x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3878.4579 ms | ✅ | 🗿x4 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000031s 3rd  | 0.000036s ✓ 8th | 0.000036s ✓ 7th | 0.000036s ✓ 6th
25x20     | 0.000036s 3rd  | 0.000044s ✓ 7th | 0.000049s ✓ 8th | 0.000040s ✓ 5th
50x50     | 0.000055s 6th  | 0.000067s ✓ 8th | 0.000047s ✓ 4th | 0.000047s ✓ 3rd
100x150   | 0.000137s 6th  | 0.000594s ✓ 7th | 0.000122s ✓ 5th | 0.000110s ✓ 4th
250x250   | 0.001089s 6th  | 0.001103s ✓ 7th | 0.000378s ✓ 4th | 0.000368s ✓ 3rd
550x500   | 0.003492s 6th  | 0.011440s ✓ 7th | 0.001088s ✓ 4th | 0.001091s ✓ 5th
1000x1000 | 0.022558s 6th  | 0.042524s ✓ 8th | 0.016031s ✓ 4th | 0.015456s ✓ 3rd
2000x2500 | 0.034325s 6th  | 2.105565s ✓ 8th | 0.017508s ✓ 4th | 0.018518s ✓ 5th
5000x5000 | 1.165366s 6th  | 1.745570s ✓ 8th | 0.617482s ✓ 4th | 0.647913s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000035s ✓ 5th | 0.000035s ✓ 4th | 0.000030s ✓ 1st | 0.000031s ✓ 2nd
25x20     | 0.000041s ✓ 6th | 0.000040s ✓ 4th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000048s ✓ 5th | 0.000039s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000634s ✓ 8th | 0.000108s ✓ 3rd | 0.000067s ✓ 2nd | 0.000064s ✓ 1st
250x250   | 0.001191s ✓ 8th | 0.000401s ✓ 5th | 0.000267s ✓ 2nd | 0.000262s ✓ 1st
550x500   | 0.016468s ✓ 8th | 0.000934s ✓ 3rd | 0.000591s ✓ 1st | 0.000686s ✓ 2nd
1000x1000 | 0.024765s ✓ 7th | 0.016277s ✓ 5th | 0.004170s ✓ 2nd | 0.004141s ✓ 1st
2000x2500 | 1.692155s ✓ 7th | 0.012586s ✓ 3rd | 0.004746s ✓ 2nd | 0.004361s ✓ 1st
5000x5000 | 1.329131s ✓ 7th | 0.381499s ✓ 3rd | 0.280493s ✓ 2nd | 0.277723s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   287.3394 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   290.4374 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVS    :   411.9278 ms | ✅ | 🥉x4 🚩x2 🏳️x3
     4. LAPX LAPJV     :   652.7408 ms | ✅ | 🚩x6 🏳️x1 🗿x1 🙅‍♂️x1
     5. LAPX LAPJVX    :   683.5785 ms | ✅ | 🥉x3 🚩x1 🏳️x4 🥴x1
     6. BASELINE SciPy :  1227.0881 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3064.4836 ms | ✅ | 🏳️x1 🥴x1 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3906.9433 ms | ✅ | 🗿x4 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these historical runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. R/H have the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
