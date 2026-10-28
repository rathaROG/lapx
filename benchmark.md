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

### Historical results (LAPX 0.12.1)

R/H single and batch results use float64 costs and `return_cost=False`.
See each case for matrix sizes, thread counts, and timing settings.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.12.1
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
lapjvr   ✅ PASS   0.000516  🥇 3.57x faster
lapjvh   ✅ PASS   0.000532  🥈 3.47x faster
scipy    ⭐ BASE   0.001844  ⭐ baseline
lapjvc   ✅ PASS   0.003928  🐌 2.13x slower
lapjvxa  ✅ PASS   0.005000  🐌 2.71x slower
lapjvx   ✅ PASS   0.005776  🐌 3.13x slower
lapjvs   ✅ PASS   0.006224  🐌 3.38x slower
lapjv    ✅ PASS   0.006252  🐌 3.39x slower
lapjvsa  ✅ PASS   0.007852  🐌 4.26x slower
--------------------------------------------

### Matrix 5 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000552  🥇 3.33x faster
lapjvh   ✅ PASS   0.000576  🥈 3.19x faster
lapjvsa  ✅ PASS   0.001348  🥉 1.36x faster
scipy    ⭐ BASE   0.001836  ⭐ baseline
lapjvxa  ✅ PASS   0.003068  🐌 1.67x slower
lapjvx   ✅ PASS   0.003808  🐌 2.07x slower
lapjvc   ✅ PASS   0.003960  🐌 2.16x slower
lapjv    ✅ PASS   0.004124  🐌 2.25x slower
lapjvs   ✅ PASS   0.004196  🐌 2.29x slower
--------------------------------------------

### Matrix 5 x 6 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000548  🥇 3.36x faster
lapjvh   ✅ PASS   0.000560  🥈 3.29x faster
scipy    ⭐ BASE   0.001840  ⭐ baseline
lapjvc   ✅ PASS   0.004100  🐌 2.23x slower
lapjvxa  ✅ PASS   0.004972  🐌 2.70x slower
lapjvx   ✅ PASS   0.005716  🐌 3.11x slower
lapjv    ✅ PASS   0.006116  🐌 3.32x slower
lapjvs   ✅ PASS   0.006216  🐌 3.38x slower
lapjvsa  ✅ PASS   0.007904  🐌 4.30x slower
--------------------------------------------

### Matrix 45 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.003192  🥇 5.48x faster
lapjvh   ✅ PASS   0.003224  🥈 5.42x faster
lapjvxa  ✅ PASS   0.010164  🥉 1.72x faster
lapjvx   ✅ PASS   0.011664  🏆 1.50x faster
lapjv    ✅ PASS   0.011896  🏆 1.47x faster
lapjvs   ✅ PASS   0.011948  🏆 1.46x faster
lapjvsa  ✅ PASS   0.013972  🏆 1.25x faster
scipy    ⭐ BASE   0.017484  ⭐ baseline
lapjvc   ✅ PASS   0.039712  🐌 2.27x slower
--------------------------------------------

### Matrix 50 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.006332  🥇 3.94x faster
lapjvr   ✅ PASS   0.006836  🥈 3.65x faster
lapjvsa  ✅ PASS   0.009016  🥉 2.77x faster
lapjvxa  ✅ PASS   0.010084  🏆 2.47x faster
lapjv    ✅ PASS   0.011900  🏆 2.10x faster
lapjvs   ✅ PASS   0.012636  🏆 1.97x faster
lapjvx   ✅ PASS   0.014152  🏆 1.76x faster
scipy    ⭐ BASE   0.024940  ⭐ baseline
lapjvc   ✅ PASS   0.028052  🐌 1.12x slower
--------------------------------------------

### Matrix 50 x 55 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.003892  🥇 5.34x faster
lapjvr   ✅ PASS   0.004096  🥈 5.07x faster
lapjvxa  ✅ PASS   0.011780  🥉 1.76x faster
lapjvs   ✅ PASS   0.012300  🏆 1.69x faster
lapjvx   ✅ PASS   0.012540  🏆 1.66x faster
lapjv    ✅ PASS   0.012752  🏆 1.63x faster
lapjvsa  ✅ PASS   0.016524  🏆 1.26x faster
scipy    ⭐ BASE   0.020768  ⭐ baseline
lapjvc   ✅ PASS   0.053084  🐌 2.56x slower
--------------------------------------------

### Matrix 450 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.358100  🥇 6.45x faster
lapjvr   ✅ PASS   0.375900  🥈 6.14x faster
lapjvs   ✅ PASS   0.577300  🥉 4.00x faster
lapjvsa  ✅ PASS   0.607700  🏆 3.80x faster
lapjvxa  ✅ PASS   0.810400  🏆 2.85x faster
lapjv    ✅ PASS   0.816600  🏆 2.83x faster
lapjvx   ✅ PASS   0.837900  🏆 2.76x faster
scipy    ⭐ BASE   2.308600  ⭐ baseline
lapjvc   ✅ PASS  11.330800  🐌 4.91x slower
--------------------------------------------

### Matrix 500 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.995100  🥇 4.59x faster
lapjvr   ✅ PASS   1.014100  🥈 4.51x faster
lapjvx   ✅ PASS   2.085800  🥉 2.19x faster
lapjv    ✅ PASS   2.101700  🏆 2.17x faster
lapjvxa  ✅ PASS   2.176000  🏆 2.10x faster
lapjvsa  ✅ PASS   2.333700  🏆 1.96x faster
lapjvs   ✅ PASS   2.358200  🏆 1.94x faster
scipy    ⭐ BASE   4.570600  ⭐ baseline
lapjvc   ✅ PASS   4.957000  🐌 1.08x slower
--------------------------------------------

### Matrix 500 x 550 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.433500  🥇 6.33x faster
lapjvh   ✅ PASS   0.434800  🥈 6.31x faster
lapjvs   ✅ PASS   0.803000  🥉 3.42x faster
lapjvsa  ✅ PASS   0.839200  🏆 3.27x faster
lapjv    ✅ PASS   0.960900  🏆 2.85x faster
lapjvxa  ✅ PASS   0.965500  🏆 2.84x faster
lapjvx   ✅ PASS   1.099100  🏆 2.50x faster
scipy    ⭐ BASE   2.742800  ⭐ baseline
lapjvc   ✅ PASS  14.110500  🐌 5.14x slower
--------------------------------------------

### Matrix 2500 x 5000 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvh   ✅ PASS      7.088800  🥇 7.22x faster
lapjvr   ✅ PASS      7.584000  🥈 6.75x faster
scipy    ⭐ BASE     51.178000  ⭐ baseline
lapjvsa  ✅ PASS     61.986300  🐌 1.21x slower
lapjvs   ✅ PASS     62.246800  🐌 1.22x slower
lapjvxa  ✅ PASS     87.812000  🐌 1.72x slower
lapjv    ✅ PASS     88.587100  🐌 1.73x slower
lapjvx   ✅ PASS     89.401300  🐌 1.75x slower
lapjvc   ✅ PASS  12216.548800  🐌 238.71x slower
-------------------------------------------------

### Matrix 5000 x 5000 | float64 | return_cost=False

Solver   Check      Time (ms)  vs SciPy
----------------------------------------------
lapjvr   ✅ PASS   288.707200  🥇 4.01x faster
lapjvh   ✅ PASS   288.751600  🥈 4.01x faster
lapjvxa  ✅ PASS   638.454200  🥉 1.81x faster
lapjv    ✅ PASS   659.925400  🏆 1.75x faster
lapjvx   ✅ PASS   660.182900  🏆 1.75x faster
lapjvsa  ✅ PASS   699.402400  🏆 1.65x faster
lapjvs   ✅ PASS   707.770500  🏆 1.63x faster
scipy    ⭐ BASE  1156.610000  ⭐ baseline
lapjvc   ✅ PASS  1285.191800  🐌 1.11x slower
----------------------------------------------

### Matrix 5000 x 7500 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS     26.729500  🥇 7.91x faster
lapjvh   ✅ PASS     30.085000  🥈 7.02x faster
lapjvs   ✅ PASS    123.768900  🥉 1.71x faster
lapjvsa  ✅ PASS    124.765800  🏆 1.69x faster
lapjvx   ✅ PASS    172.504400  🏆 1.22x faster
lapjv    ✅ PASS    177.471200  🏆 1.19x faster
lapjvxa  ✅ PASS    179.496700  🏆 1.18x faster
scipy    ⭐ BASE    211.315700  ⭐ baseline
lapjvc   ✅ PASS  55056.618700  🐌 260.54x slower
-------------------------------------------------
```

</details>

<details><summary>🗂️ Historical batch results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new8\lapx\benchmarks>python benchmark_batch.py


Note: R/H native float64, JVS default float32, jvsa64 float64.


### Dense 10 x (4000x4000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   311.987400  🥇 21.49x faster
lapx-batch-jvr     ✅ PASS   336.081100  🥈 19.95x faster
lapx-batch-jvsa    ✅ PASS  1056.304100  🥉 6.35x faster
lapx-batch-jvxa    ✅ PASS  1061.836900  🏆 6.31x faster
lapx-batch-jvs     ✅ PASS  1078.399300  🏆 6.22x faster
lapx-batch-jvsa64  ✅ PASS  1136.606600  🏆 5.90x faster
lapx-batch-jvx     ✅ PASS  1193.452600  🏆 5.62x faster
lapx-loop-jvh      ✅ PASS  1627.470100  🏆 4.12x faster
lapx-loop-jvr      ✅ PASS  1652.825500  🏆 4.06x faster
lapx-loop-jvx      ✅ PASS  5294.394900  🏆 1.27x faster
lapx-loop-jvs      ✅ PASS  5662.273300  🏆 1.18x faster
scipy-loop         ⭐ BASE  6705.111900  ⭐ baseline
---------------------------------------------------------

### Dense 20 x (3000x2000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS    68.259500  🥇 14.82x faster
lapx-batch-jvr     ✅ PASS    85.982300  🥈 11.76x faster
lapx-batch-jvsa    ✅ PASS    96.450800  🥉 10.49x faster
lapx-batch-jvs     ✅ PASS   121.641400  🏆 8.31x faster
lapx-batch-jvxa    ✅ PASS   135.461500  🏆 7.47x faster
lapx-batch-jvsa64  ✅ PASS   139.503100  🏆 7.25x faster
lapx-batch-jvx     ✅ PASS   151.586600  🏆 6.67x faster
lapx-loop-jvh      ✅ PASS   315.727300  🏆 3.20x faster
lapx-loop-jvr      ✅ PASS   334.046600  🏆 3.03x faster
lapx-loop-jvs      ✅ PASS   841.269800  🏆 1.20x faster
lapx-loop-jvx      ✅ PASS   976.666800  🏆 1.04x faster
scipy-loop         ⭐ BASE  1011.388300  ⭐ baseline
---------------------------------------------------------

### Dense 50 x (2000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   215.992400  🥇 27.32x faster
lapx-batch-jvr     ✅ PASS   219.242750  🥈 26.91x faster
lapx-batch-jvx     ✅ PASS   434.797950  🥉 13.57x faster
lapx-batch-jvs     ✅ PASS   442.649000  🏆 13.33x faster
lapx-batch-jvsa64  ✅ PASS   453.533900  🏆 13.01x faster
lapx-batch-jvxa    ✅ PASS   453.888550  🏆 13.00x faster
lapx-batch-jvsa    ✅ PASS   455.432750  🏆 12.95x faster
lapx-loop-jvr      ✅ PASS  1223.564550  🏆 4.82x faster
lapx-loop-jvh      ✅ PASS  1240.386200  🏆 4.76x faster
lapx-loop-jvx      ✅ PASS  3771.836850  🏆 1.56x faster
lapx-loop-jvs      ✅ PASS  4485.316150  🏆 1.32x faster
scipy-loop         ⭐ BASE  5900.049250  ⭐ baseline
---------------------------------------------------------

### Dense 100 x (1000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvr     ✅ PASS    21.207100  🥇 42.38x faster
lapx-batch-jvh     ✅ PASS    25.538450  🥈 35.19x faster
lapx-loop-jvh      ✅ PASS   116.084500  🥉 7.74x faster
lapx-loop-jvr      ✅ PASS   119.542500  🏆 7.52x faster
lapx-batch-jvs     ✅ PASS   120.690000  🏆 7.45x faster
lapx-batch-jvsa    ✅ PASS   130.252650  🏆 6.90x faster
lapx-batch-jvx     ✅ PASS   215.953450  🏆 4.16x faster
lapx-batch-jvxa    ✅ PASS   219.173850  🏆 4.10x faster
lapx-batch-jvsa64  ✅ PASS   226.644200  🏆 3.97x faster
lapx-loop-jvs      ✅ PASS   868.488500  🏆 1.03x faster
scipy-loop         ⭐ BASE   898.717450  ⭐ baseline
lapx-loop-jvx      ✅ PASS  1274.524500  🐌 1.42x slower
---------------------------------------------------------

### Dense 500 x (1000x1000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check       Time (ms)  vs SciPy
----------------------------------------------------------
lapx-batch-jvh     ✅ PASS    310.213850  🥇 36.55x faster
lapx-batch-jvr     ✅ PASS    314.985700  🥈 36.00x faster
lapx-batch-jvxa    ✅ PASS    588.633600  🥉 19.26x faster
lapx-batch-jvx     ✅ PASS    593.780700  🏆 19.10x faster
lapx-batch-jvsa64  ✅ PASS    600.551600  🏆 18.88x faster
lapx-batch-jvsa    ✅ PASS    648.946750  🏆 17.47x faster
lapx-batch-jvs     ✅ PASS    658.010550  🏆 17.23x faster
lapx-loop-jvh      ✅ PASS   2239.705200  🏆 5.06x faster
lapx-loop-jvr      ✅ PASS   2296.434350  🏆 4.94x faster
lapx-loop-jvx      ✅ PASS   6819.758900  🏆 1.66x faster
lapx-loop-jvs      ✅ PASS   8070.581050  🏆 1.41x faster
scipy-loop         ⭐ BASE  11339.563250  ⭐ baseline
----------------------------------------------------------

### Sparse 100 x (1000x1000) | target density=1.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    17.392050  🥇 96.47x faster
lapx-batch-jvh     ✅ PASS    60.764600  🥈 27.61x faster
lapx-batch-jvr     ✅ PASS    62.458550  🥉 26.86x faster
lapx-batch-mod-1t  ✅ PASS    98.755250  🏆 16.99x faster
lapx-loop-mod      ✅ PASS   100.324500  🏆 16.72x faster
lapx-batch-jvsa64  ✅ PASS   124.655050  🏆 13.46x faster
lapx-batch-jvxa    ✅ PASS   126.393150  🏆 13.27x faster
lapx-batch-jvx     ✅ PASS   131.738650  🏆 12.74x faster
lapx-batch-jvsa    ✅ PASS   144.114450  🏆 11.64x faster
lapx-batch-jvs     ✅ PASS   156.968100  🏆 10.69x faster
lapx-loop-jvh      ✅ PASS   345.832500  🏆 4.85x faster
lapx-loop-jvr      ✅ PASS   363.701500  🏆 4.61x faster
lapx-loop-jvx      ✅ PASS  1237.649300  🏆 1.36x faster
lapx-loop-jvs      ✅ PASS  1503.914850  🏆 1.12x faster
scipy-loop         ⭐ BASE  1677.732650  ⭐ baseline
---------------------------------------------------------

### Sparse 50 x (2000x2000) | target density=5.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    66.465350  🥇 77.14x faster
lapx-batch-jvh     ✅ PASS   211.003750  🥈 24.30x faster
lapx-batch-jvr     ✅ PASS   212.296700  🥉 24.15x faster
lapx-batch-jvx     ✅ PASS   470.988450  🏆 10.89x faster
lapx-batch-jvsa64  ✅ PASS   471.463200  🏆 10.88x faster
lapx-batch-jvsa    ✅ PASS   471.604650  🏆 10.87x faster
lapx-batch-jvs     ✅ PASS   474.103100  🏆 10.81x faster
lapx-batch-jvxa    ✅ PASS   491.106050  🏆 10.44x faster
lapx-batch-mod-1t  ✅ PASS   532.671200  🏆 9.63x faster
lapx-loop-mod      ✅ PASS   533.244350  🏆 9.62x faster
lapx-loop-jvh      ✅ PASS  1138.445550  🏆 4.50x faster
lapx-loop-jvr      ✅ PASS  1158.162100  🏆 4.43x faster
lapx-loop-jvx      ✅ PASS  3710.410800  🏆 1.38x faster
lapx-loop-jvs      ✅ PASS  4443.933250  🏆 1.15x faster
scipy-loop         ⭐ BASE  5127.397950  ⭐ baseline
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

<details><summary>📊 Historical tracking results (LAPX 0.12.1):</summary><br>

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.12.1
scipy==1.17.1
numpy==2.4.6
```

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new8\lapx\benchmarks>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000031s 3rd  | 0.000036s ✗ 8th | 0.000035s ✓ 6th | 0.000034s ✓ 4th
25x20     | 0.000035s 3rd  | 0.000043s ✗ 8th | 0.000040s ✓ 4th | 0.000040s ✓ 5th
50x50     | 0.000057s 6th  | 0.000068s ✗ 8th | 0.000045s ✓ 4th | 0.000046s ✓ 5th
100x150   | 0.000138s 6th  | 0.000484s ✓ 7th | 0.000104s ✓ 4th | 0.000106s ✓ 5th
250x250   | 0.001123s 7th  | 0.001022s ✗ 6th | 0.000377s ✓ 4th | 0.000374s ✓ 3rd
550x500   | 0.003572s 6th  | 0.012070s ✓ 7th | 0.001113s ✓ 4th | 0.001269s ✓ 5th
1000x1000 | 0.022919s 6th  | 0.038759s ✓ 8th | 0.015939s ✓ 4th | 0.014982s ✓ 3rd
2000x2500 | 0.037141s 6th  | 1.991995s ✓ 8th | 0.018098s ✓ 5th | 0.017866s ✓ 4th
5000x5000 | 1.200425s 6th  | 1.719911s ✓ 8th | 0.650989s ✓ 3rd | 0.653436s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000035s ✓ 7th | 0.000035s ✓ 5th | 0.000030s ✓ 1st | 0.000030s ✓ 2nd
25x20     | 0.000041s ✓ 7th | 0.000040s ✓ 6th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000045s ✓ 3rd | 0.000039s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000640s ✓ 8th | 0.000103s ✓ 3rd | 0.000067s ✓ 2nd | 0.000066s ✓ 1st
250x250   | 0.001169s ✓ 8th | 0.000424s ✓ 5th | 0.000279s ✓ 2nd | 0.000275s ✓ 1st
550x500   | 0.016944s ✓ 8th | 0.001024s ✓ 3rd | 0.000777s ✓ 2nd | 0.000664s ✓ 1st
1000x1000 | 0.024904s ✓ 7th | 0.018257s ✓ 5th | 0.004268s ✓ 1st | 0.004365s ✓ 2nd
2000x2500 | 1.722461s ✓ 7th | 0.013838s ✓ 3rd | 0.004604s ✓ 1st | 0.005177s ✓ 2nd
5000x5000 | 1.275929s ✓ 7th | 0.697988s ✓ 5th | 0.287103s ✓ 1st | 0.287307s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   297.1973 ms | ✅ | 🥇x5 🥈x4
     2. LAPX LAPJVH    :   297.9552 ms | ✅ | 🥇x4 🥈x5
     3. LAPX LAPJV     :   686.7395 ms | ✅ | 🥉x1 🚩x6 🏳️x1 🥴x1
     4. LAPX LAPJVX    :   688.1518 ms | ✅ | 🥉x2 🚩x3 🏳️x4
     5. LAPX LAPJVS    :   731.7526 ms | ✅ | 🥉x4 🏳️x4 🥴x1
     6. BASELINE SciPy :  1265.4415 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3042.1877 ms | ✅ | 🗿x6 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3764.3866 ms | ⚠️ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 3rd  | 0.000034s ✗ 7th | 0.000034s ✓ 6th | 0.000034s ✓ 5th
25x20     | 0.000034s 3rd  | 0.000041s ✗ 8th | 0.000039s ✓ 5th | 0.000037s ✓ 4th
50x50     | 0.000057s 6th  | 0.000069s ✗ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000139s 6th  | 0.000600s ✓ 7th | 0.000106s ✓ 4th | 0.000104s ✓ 3rd
250x250   | 0.001126s 6th  | 0.001149s ✓ 7th | 0.000375s ✓ 3rd | 0.000378s ✓ 4th
550x500   | 0.003646s 6th  | 0.011433s ✓ 7th | 0.001102s ✓ 5th | 0.001096s ✓ 4th
1000x1000 | 0.022846s 6th  | 0.041946s ✓ 8th | 0.016033s ✓ 4th | 0.015424s ✓ 3rd
2000x2500 | 0.036984s 6th  | 2.193563s ✓ 8th | 0.019024s ✓ 5th | 0.018064s ✓ 4th
5000x5000 | 1.178241s 6th  | 1.710774s ✓ 8th | 0.629621s ✓ 3rd | 0.635209s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000033s ✓ 4th | 0.000035s ✓ 8th | 0.000029s ✓ 2nd | 0.000028s ✓ 1st
25x20     | 0.000040s ✓ 7th | 0.000039s ✓ 6th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000065s ✓ 7th | 0.000046s ✓ 5th | 0.000039s ✓ 2nd | 0.000039s ✓ 1st
100x150   | 0.000640s ✓ 8th | 0.000109s ✓ 5th | 0.000067s ✓ 2nd | 0.000064s ✓ 1st
250x250   | 0.001176s ✓ 8th | 0.000455s ✓ 5th | 0.000280s ✓ 2nd | 0.000279s ✓ 1st
550x500   | 0.016540s ✓ 8th | 0.000955s ✓ 3rd | 0.000647s ✓ 1st | 0.000653s ✓ 2nd
1000x1000 | 0.024783s ✓ 7th | 0.018378s ✓ 5th | 0.004254s ✓ 1st | 0.004254s ✓ 2nd
2000x2500 | 1.726171s ✓ 7th | 0.013715s ✓ 3rd | 0.005197s ✓ 1st | 0.005216s ✓ 2nd
5000x5000 | 1.275814s ✓ 7th | 0.688048s ✓ 5th | 0.286777s ✓ 2nd | 0.284447s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   295.0102 ms | ✅ | 🥇x5 🥈x4
     2. LAPX LAPJVR    :   297.3204 ms | ✅ | 🥇x4 🥈x5
     3. LAPX LAPJV     :   666.3803 ms | ✅ | 🥉x2 🚩x3 🏳️x3 🥴x1
     4. LAPX LAPJVX    :   670.3911 ms | ✅ | 🥉x3 🚩x5 🏳️x1
     5. LAPX LAPJVS    :   721.7801 ms | ✅ | 🥉x2 🏳️x5 🥴x1 🙅‍♂️x1
     6. BASELINE SciPy :  1243.1034 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3045.2613 ms | ✅ | 🚩x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3959.6111 ms | ⚠️ | 🗿x4 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 3rd  | 0.000036s ✗ 7th | 0.000033s ✓ 5th | 0.000033s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000042s ✓ 8th | 0.000037s ✓ 5th | 0.000037s ✓ 4th
50x50     | 0.000057s 6th  | 0.000065s ✓ 8th | 0.000045s ✓ 5th | 0.000045s ✓ 4th
100x150   | 0.000142s 6th  | 0.000584s ✓ 7th | 0.000104s ✓ 5th | 0.000103s ✓ 4th
250x250   | 0.001125s 6th  | 0.001144s ✓ 7th | 0.000373s ✓ 3rd | 0.000375s ✓ 4th
550x500   | 0.003734s 6th  | 0.011302s ✓ 7th | 0.001283s ✓ 5th | 0.001200s ✓ 4th
1000x1000 | 0.022958s 6th  | 0.042920s ✓ 8th | 0.016055s ✓ 4th | 0.015417s ✓ 3rd
2000x2500 | 0.037084s 6th  | 2.215919s ✓ 8th | 0.018326s ✓ 5th | 0.017860s ✓ 4th
5000x5000 | 1.168722s 6th  | 1.611795s ✓ 8th | 0.654896s ✓ 3rd | 0.655273s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000039s ✓ 8th | 0.000032s ✓ 4th | 0.000029s ✓ 2nd | 0.000028s ✓ 1st
25x20     | 0.000039s ✓ 7th | 0.000037s ✓ 6th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000064s ✓ 7th | 0.000045s ✓ 3rd | 0.000039s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000637s ✓ 8th | 0.000101s ✓ 3rd | 0.000066s ✓ 2nd | 0.000063s ✓ 1st
250x250   | 0.001168s ✓ 8th | 0.000406s ✓ 5th | 0.000279s ✓ 1st | 0.000280s ✓ 2nd
550x500   | 0.016649s ✓ 8th | 0.001019s ✓ 3rd | 0.000741s ✓ 2nd | 0.000697s ✓ 1st
1000x1000 | 0.024679s ✓ 7th | 0.018301s ✓ 5th | 0.004502s ✓ 2nd | 0.004118s ✓ 1st
2000x2500 | 1.716722s ✓ 7th | 0.013663s ✓ 3rd | 0.005172s ✓ 1st | 0.005204s ✓ 2nd
5000x5000 | 1.267274s ✓ 7th | 0.691391s ✓ 5th | 0.288165s ✓ 2nd | 0.285362s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   295.8238 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   299.0237 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVX    :   690.3424 ms | ✅ | 🥉x1 🚩x7 🥴x1
     4. LAPX LAPJV     :   691.1530 ms | ✅ | 🥉x2 🚩x1 🏳️x6
     5. LAPX LAPJVS    :   724.9951 ms | ✅ | 🥉x4 🚩x1 🏳️x3 🥴x1
     6. BASELINE SciPy :  1233.8839 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3027.2709 ms | ✅ | 🗿x5 🙅‍♂️x4
     8. LAPX LAPJV-IFT :  3883.8058 ms | ⚠️ | 🗿x4 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 2nd  | 0.000034s ✓ 8th | 0.000033s ✓ 4th | 0.000034s ✓ 5th
25x20     | 0.000034s 2nd  | 0.000042s ✓ 8th | 0.000037s ✓ 4th | 0.000039s ✓ 6th
50x50     | 0.000058s 6th  | 0.000066s ✓ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 5th
100x150   | 0.000137s 6th  | 0.000588s ✓ 7th | 0.000107s ✓ 5th | 0.000104s ✓ 3rd
250x250   | 0.001123s 7th  | 0.001116s ✓ 6th | 0.000374s ✓ 4th | 0.000372s ✓ 3rd
550x500   | 0.003860s 6th  | 0.011540s ✓ 7th | 0.001136s ✓ 4th | 0.001178s ✓ 5th
1000x1000 | 0.022897s 6th  | 0.042166s ✓ 8th | 0.016288s ✓ 4th | 0.015525s ✓ 3rd
2000x2500 | 0.037325s 6th  | 2.183449s ✓ 8th | 0.018123s ✓ 4th | 0.018298s ✓ 5th
5000x5000 | 1.177093s 6th  | 1.752119s ✓ 8th | 0.654097s ✓ 4th | 0.647550s ✓ 3rd
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000034s ✓ 6th | 0.000034s ✓ 7th | 0.000029s ✓ 1st | 0.000030s ✓ 3rd
25x20     | 0.000039s ✓ 7th | 0.000038s ✓ 5th | 0.000035s ✓ 3rd | 0.000031s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000045s ✓ 3rd | 0.000039s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000632s ✓ 8th | 0.000104s ✓ 4th | 0.000066s ✓ 2nd | 0.000063s ✓ 1st
250x250   | 0.001230s ✓ 8th | 0.000421s ✓ 5th | 0.000278s ✓ 2nd | 0.000275s ✓ 1st
550x500   | 0.016227s ✓ 8th | 0.001011s ✓ 3rd | 0.000648s ✓ 1st | 0.000689s ✓ 2nd
1000x1000 | 0.024807s ✓ 7th | 0.018554s ✓ 5th | 0.004251s ✓ 2nd | 0.004139s ✓ 1st
2000x2500 | 1.734697s ✓ 7th | 0.013809s ✓ 3rd | 0.005209s ✓ 1st | 0.005257s ✓ 2nd
5000x5000 | 1.278494s ✓ 7th | 0.691971s ✓ 5th | 0.285882s ✓ 1st | 0.287326s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   296.4366 ms | ✅ | 🥇x4 🥈x4 🥉x1
     2. LAPX LAPJVH    :   297.8483 ms | ✅ | 🥇x5 🥈x3 🥉x1
     3. LAPX LAPJVX    :   683.1442 ms | ✅ | 🥉x4 🏳️x4 🥴x1
     4. LAPX LAPJV     :   690.2414 ms | ✅ | 🚩x8 🏳️x1
     5. LAPX LAPJVS    :   725.9872 ms | ✅ | 🥉x3 🚩x1 🏳️x4 🗿x1
     6. BASELINE SciPy :  1242.5569 ms | ⭐ | 🥈x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3056.2234 ms | ✅ | 🥴x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3991.1196 ms | ✅ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000031s 3rd  | 0.000037s ✓ 8th | 0.000035s ✓ 5th | 0.000036s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000044s ✓ 8th | 0.000038s ✓ 5th | 0.000037s ✓ 4th
50x50     | 0.000057s 6th  | 0.000064s ✓ 8th | 0.000045s ✓ 5th | 0.000045s ✓ 4th
100x150   | 0.000144s 6th  | 0.000560s ✓ 7th | 0.000106s ✓ 5th | 0.000106s ✓ 4th
250x250   | 0.001120s 7th  | 0.001104s ✓ 6th | 0.000366s ✓ 3rd | 0.000376s ✓ 4th
550x500   | 0.003531s 6th  | 0.011329s ✓ 7th | 0.001092s ✓ 5th | 0.001077s ✓ 4th
1000x1000 | 0.023450s 6th  | 0.041878s ✓ 8th | 0.016035s ✓ 4th | 0.015391s ✓ 3rd
2000x2500 | 0.037801s 6th  | 2.198938s ✓ 8th | 0.018386s ✓ 5th | 0.017777s ✓ 4th
5000x5000 | 1.170333s 6th  | 1.750200s ✓ 8th | 0.661860s ✓ 4th | 0.648703s ✓ 3rd
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 7th | 0.000034s ✓ 4th | 0.000030s ✓ 1st | 0.000031s ✓ 2nd
25x20     | 0.000040s ✓ 6th | 0.000040s ✓ 7th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000063s ✓ 7th | 0.000045s ✓ 3rd | 0.000039s ✓ 2nd | 0.000039s ✓ 1st
100x150   | 0.000634s ✓ 8th | 0.000102s ✓ 3rd | 0.000066s ✓ 1st | 0.000066s ✓ 2nd
250x250   | 0.001201s ✓ 8th | 0.000402s ✓ 5th | 0.000277s ✓ 2nd | 0.000273s ✓ 1st
550x500   | 0.016164s ✓ 8th | 0.000965s ✓ 3rd | 0.000605s ✓ 1st | 0.000643s ✓ 2nd
1000x1000 | 0.024453s ✓ 7th | 0.018393s ✓ 5th | 0.004277s ✓ 1st | 0.004293s ✓ 2nd
2000x2500 | 1.742211s ✓ 7th | 0.013935s ✓ 3rd | 0.005203s ✓ 2nd | 0.005156s ✓ 1st
5000x5000 | 1.279940s ✓ 7th | 0.684757s ✓ 5th | 0.287305s ✓ 2nd | 0.285044s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   295.5755 ms | ✅ | 🥇x4 🥈x5
     2. LAPX LAPJVR    :   297.8328 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJVX    :   683.5487 ms | ✅ | 🥉x2 🚩x6 🥴x1
     4. LAPX LAPJV     :   697.9642 ms | ✅ | 🥉x1 🚩x2 🏳️x6
     5. LAPX LAPJVS    :   718.6742 ms | ✅ | 🥉x4 🚩x1 🏳️x3 🗿x1
     6. BASELINE SciPy :  1236.5016 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3064.7411 ms | ✅ | 🥴x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  4004.1539 ms | ✅ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these historical runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. R/H have the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
