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

### Historical results (LAPX 0.13.0)

R/H single and batch results use float64 costs and `return_cost=False`.
See each case for matrix sizes, thread counts, and timing settings.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.13.0
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
lapjvr   ✅ PASS   0.000472  🥇 3.47x faster
lapjvh   ✅ PASS   0.000476  🥈 3.45x faster
scipy    ⭐ BASE   0.001640  ⭐ baseline
lapjvc   ✅ PASS   0.003672  🐌 2.24x slower
lapjvxa  ✅ PASS   0.004628  🐌 2.82x slower
lapjvx   ✅ PASS   0.005320  🐌 3.24x slower
lapjv    ✅ PASS   0.005880  🐌 3.59x slower
lapjvs   ✅ PASS   0.005916  🐌 3.61x slower
lapjvsa  ✅ PASS   0.007348  🐌 4.48x slower
--------------------------------------------

### Matrix 5 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000540  🥇 3.14x faster
lapjvh   ✅ PASS   0.000576  🥈 2.94x faster
lapjvsa  ✅ PASS   0.001276  🥉 1.33x faster
scipy    ⭐ BASE   0.001696  ⭐ baseline
lapjvxa  ✅ PASS   0.002860  🐌 1.69x slower
lapjvx   ✅ PASS   0.003792  🐌 2.24x slower
lapjv    ✅ PASS   0.003868  🐌 2.28x slower
lapjvs   ✅ PASS   0.004140  🐌 2.44x slower
lapjvc   ✅ PASS   0.005212  🐌 3.07x slower
--------------------------------------------

### Matrix 5 x 6 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000476  🥇 3.55x faster
lapjvh   ✅ PASS   0.000500  🥈 3.38x faster
scipy    ⭐ BASE   0.001692  ⭐ baseline
lapjvc   ✅ PASS   0.003848  🐌 2.27x slower
lapjvxa  ✅ PASS   0.004672  🐌 2.76x slower
lapjvx   ✅ PASS   0.005332  🐌 3.15x slower
lapjv    ✅ PASS   0.005712  🐌 3.38x slower
lapjvs   ✅ PASS   0.005812  🐌 3.43x slower
lapjvsa  ✅ PASS   0.007476  🐌 4.42x slower
--------------------------------------------

### Matrix 45 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.002892  🥇 5.54x faster
lapjvh   ✅ PASS   0.003108  🥈 5.16x faster
lapjvxa  ✅ PASS   0.009508  🥉 1.69x faster
lapjvx   ✅ PASS   0.010768  🏆 1.49x faster
lapjvs   ✅ PASS   0.011208  🏆 1.43x faster
lapjv    ✅ PASS   0.011468  🏆 1.40x faster
lapjvsa  ✅ PASS   0.013412  🏆 1.19x faster
scipy    ⭐ BASE   0.016024  ⭐ baseline
lapjvc   ✅ PASS   0.048412  🐌 3.02x slower
--------------------------------------------

### Matrix 50 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.006028  🥇 3.69x faster
lapjvr   ✅ PASS   0.006208  🥈 3.58x faster
lapjvsa  ✅ PASS   0.009436  🥉 2.36x faster
lapjvxa  ✅ PASS   0.009732  🏆 2.29x faster
lapjv    ✅ PASS   0.010632  🏆 2.09x faster
lapjvx   ✅ PASS   0.010836  🏆 2.05x faster
lapjvs   ✅ PASS   0.011444  🏆 1.94x faster
scipy    ⭐ BASE   0.022252  ⭐ baseline
lapjvc   ✅ PASS   0.026568  🐌 1.19x slower
--------------------------------------------

### Matrix 50 x 55 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.003548  🥇 6.38x faster
lapjvh   ✅ PASS   0.003816  🥈 5.93x faster
lapjv    ✅ PASS   0.011868  🥉 1.91x faster
lapjvx   ✅ PASS   0.012020  🏆 1.88x faster
lapjvs   ✅ PASS   0.012872  🏆 1.76x faster
lapjvxa  ✅ PASS   0.013500  🏆 1.68x faster
lapjvsa  ✅ PASS   0.019964  🏆 1.13x faster
scipy    ⭐ BASE   0.022644  ⭐ baseline
lapjvc   ✅ PASS   0.051992  🐌 2.30x slower
--------------------------------------------

### Matrix 450 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.349200  🥇 6.53x faster
lapjvr   ✅ PASS   0.351500  🥈 6.49x faster
lapjvs   ✅ PASS   0.535100  🥉 4.26x faster
lapjvsa  ✅ PASS   0.562600  🏆 4.05x faster
lapjvxa  ✅ PASS   0.777200  🏆 2.93x faster
lapjvx   ✅ PASS   0.784600  🏆 2.91x faster
lapjv    ✅ PASS   0.808700  🏆 2.82x faster
scipy    ⭐ BASE   2.280400  ⭐ baseline
lapjvc   ✅ PASS  10.820500  🐌 4.75x slower
--------------------------------------------

### Matrix 500 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.891900  🥇 5.19x faster
lapjvh   ✅ PASS   1.022100  🥈 4.53x faster
lapjvx   ✅ PASS   2.090400  🥉 2.22x faster
lapjvxa  ✅ PASS   2.104800  🏆 2.20x faster
lapjv    ✅ PASS   2.112700  🏆 2.19x faster
lapjvsa  ✅ PASS   2.329700  🏆 1.99x faster
lapjvs   ✅ PASS   2.368300  🏆 1.96x faster
scipy    ⭐ BASE   4.630800  ⭐ baseline
lapjvc   ✅ PASS   5.153100  🐌 1.11x slower
--------------------------------------------

### Matrix 500 x 550 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.427800  🥇 6.31x faster
lapjvh   ✅ PASS   0.441500  🥈 6.12x faster
lapjvs   ✅ PASS   0.817100  🥉 3.31x faster
lapjvsa  ✅ PASS   0.926800  🏆 2.91x faster
lapjvxa  ✅ PASS   0.954000  🏆 2.83x faster
lapjv    ✅ PASS   0.987500  🏆 2.73x faster
lapjvx   ✅ PASS   1.034800  🏆 2.61x faster
scipy    ⭐ BASE   2.700700  ⭐ baseline
lapjvc   ✅ PASS  14.058100  🐌 5.21x slower
--------------------------------------------

### Matrix 2500 x 5000 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS      7.459400  🥇 7.43x faster
lapjvh   ✅ PASS      7.592900  🥈 7.30x faster
scipy    ⭐ BASE     55.436100  ⭐ baseline
lapjvs   ✅ PASS     60.461400  🐌 1.09x slower
lapjvsa  ✅ PASS     62.008600  🐌 1.12x slower
lapjvx   ✅ PASS     84.731200  🐌 1.53x slower
lapjvxa  ✅ PASS     85.168800  🐌 1.54x slower
lapjv    ✅ PASS     85.439100  🐌 1.54x slower
lapjvc   ✅ PASS  12010.458300  🐌 216.65x slower
-------------------------------------------------

### Matrix 5000 x 5000 | float64 | return_cost=False

Solver   Check      Time (ms)  vs SciPy
----------------------------------------------
lapjvr   ✅ PASS   259.687200  🥇 4.16x faster
lapjvh   ✅ PASS   263.211900  🥈 4.10x faster
lapjvx   ✅ PASS   608.858100  🥉 1.77x faster
lapjv    ✅ PASS   610.246500  🏆 1.77x faster
lapjvxa  ✅ PASS   627.677900  🏆 1.72x faster
lapjvsa  ✅ PASS   679.361900  🏆 1.59x faster
lapjvs   ✅ PASS   685.105400  🏆 1.58x faster
scipy    ⭐ BASE  1080.190800  ⭐ baseline
lapjvc   ✅ PASS  1244.011900  🐌 1.15x slower
----------------------------------------------

### Matrix 5000 x 7500 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS     20.934200  🥇 9.94x faster
lapjvh   ✅ PASS     28.787800  🥈 7.23x faster
lapjvsa  ✅ PASS    108.657800  🥉 1.91x faster
lapjvs   ✅ PASS    126.326000  🏆 1.65x faster
lapjvx   ✅ PASS    162.478900  🏆 1.28x faster
lapjv    ✅ PASS    169.417200  🏆 1.23x faster
lapjvxa  ✅ PASS    173.821000  🏆 1.20x faster
scipy    ⭐ BASE    208.077300  ⭐ baseline
lapjvc   ✅ PASS  54272.405300  🐌 260.83x slower
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
lapx-batch-jvh     ✅ PASS   324.347400  🥇 20.08x faster
lapx-batch-jvr     ✅ PASS   336.763300  🥈 19.34x faster
lapx-batch-jvsa    ✅ PASS  1083.131500  🥉 6.01x faster
lapx-batch-jvsa64  ✅ PASS  1096.002300  🏆 5.94x faster
lapx-batch-jvxa    ✅ PASS  1105.314900  🏆 5.89x faster
lapx-batch-jvs     ✅ PASS  1126.184000  🏆 5.78x faster
lapx-batch-jvx     ✅ PASS  1129.443600  🏆 5.77x faster
lapx-loop-jvh      ✅ PASS  1547.916000  🏆 4.21x faster
lapx-loop-jvr      ✅ PASS  1595.296400  🏆 4.08x faster
lapx-loop-jvx      ✅ PASS  5124.030000  🏆 1.27x faster
lapx-loop-jvs      ✅ PASS  5573.622900  🏆 1.17x faster
scipy-loop         ⭐ BASE  6511.804700  ⭐ baseline
---------------------------------------------------------

### Dense 20 x (3000x2000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS    67.842000  🥇 14.82x faster
lapx-batch-jvr     ✅ PASS    82.998100  🥈 12.12x faster
lapx-batch-jvsa    ✅ PASS   102.103200  🥉 9.85x faster
lapx-batch-jvs     ✅ PASS   109.336100  🏆 9.20x faster
lapx-batch-jvxa    ✅ PASS   140.042300  🏆 7.18x faster
lapx-batch-jvsa64  ✅ PASS   147.307100  🏆 6.83x faster
lapx-batch-jvx     ✅ PASS   149.062300  🏆 6.75x faster
lapx-loop-jvr      ✅ PASS   311.627300  🏆 3.23x faster
lapx-loop-jvh      ✅ PASS   317.830100  🏆 3.16x faster
lapx-loop-jvs      ✅ PASS   819.222300  🏆 1.23x faster
lapx-loop-jvx      ✅ PASS   978.620900  🏆 1.03x faster
scipy-loop         ⭐ BASE  1005.573500  ⭐ baseline
---------------------------------------------------------

### Dense 50 x (2000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   216.084900  🥇 27.37x faster
lapx-batch-jvr     ✅ PASS   217.250450  🥈 27.22x faster
lapx-batch-jvx     ✅ PASS   433.701250  🥉 13.64x faster
lapx-batch-jvs     ✅ PASS   442.287900  🏆 13.37x faster
lapx-batch-jvsa    ✅ PASS   454.157700  🏆 13.02x faster
lapx-batch-jvxa    ✅ PASS   456.180900  🏆 12.96x faster
lapx-batch-jvsa64  ✅ PASS   462.528450  🏆 12.79x faster
lapx-loop-jvr      ✅ PASS  1160.749950  🏆 5.09x faster
lapx-loop-jvh      ✅ PASS  1161.524550  🏆 5.09x faster
lapx-loop-jvx      ✅ PASS  3776.627350  🏆 1.57x faster
lapx-loop-jvs      ✅ PASS  4487.674100  🏆 1.32x faster
scipy-loop         ⭐ BASE  5914.019250  ⭐ baseline
---------------------------------------------------------

### Dense 100 x (1000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS    20.476800  🥇 43.25x faster
lapx-batch-jvr     ✅ PASS    20.477950  🥈 43.24x faster
lapx-loop-jvr      ✅ PASS   109.265250  🥉 8.10x faster
lapx-loop-jvh      ✅ PASS   117.913300  🏆 7.51x faster
lapx-batch-jvs     ✅ PASS   132.217850  🏆 6.70x faster
lapx-batch-jvsa    ✅ PASS   137.088100  🏆 6.46x faster
lapx-batch-jvx     ✅ PASS   227.076100  🏆 3.90x faster
lapx-batch-jvsa64  ✅ PASS   231.805800  🏆 3.82x faster
lapx-batch-jvxa    ✅ PASS   237.660350  🏆 3.73x faster
lapx-loop-jvs      ✅ PASS   874.837900  🏆 1.01x faster
scipy-loop         ⭐ BASE   885.526900  ⭐ baseline
lapx-loop-jvx      ✅ PASS  1263.491050  🐌 1.43x slower
---------------------------------------------------------

### Dense 500 x (1000x1000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check       Time (ms)  vs SciPy
----------------------------------------------------------
lapx-batch-jvh     ✅ PASS    310.793550  🥇 36.37x faster
lapx-batch-jvr     ✅ PASS    313.681300  🥈 36.03x faster
lapx-batch-jvxa    ✅ PASS    582.098350  🥉 19.42x faster
lapx-batch-jvx     ✅ PASS    584.075250  🏆 19.35x faster
lapx-batch-jvsa64  ✅ PASS    594.172400  🏆 19.02x faster
lapx-batch-jvs     ✅ PASS    655.505600  🏆 17.24x faster
lapx-batch-jvsa    ✅ PASS    658.906800  🏆 17.15x faster
lapx-loop-jvh      ✅ PASS   2172.043100  🏆 5.20x faster
lapx-loop-jvr      ✅ PASS   2239.025950  🏆 5.05x faster
lapx-loop-jvx      ✅ PASS   6730.088450  🏆 1.68x faster
lapx-loop-jvs      ✅ PASS   8049.269400  🏆 1.40x faster
scipy-loop         ⭐ BASE  11302.014500  ⭐ baseline
----------------------------------------------------------

### Sparse 100 x (1000x1000) | target density=1.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    19.408050  🥇 86.79x faster
lapx-batch-jvh     ✅ PASS    60.759200  🥈 27.72x faster
lapx-batch-jvr     ✅ PASS    64.640650  🥉 26.06x faster
lapx-batch-mod-1t  ✅ PASS    98.563550  🏆 17.09x faster
lapx-loop-mod      ✅ PASS    99.598300  🏆 16.91x faster
lapx-batch-jvsa64  ✅ PASS   125.916500  🏆 13.38x faster
lapx-batch-jvxa    ✅ PASS   127.350600  🏆 13.23x faster
lapx-batch-jvx     ✅ PASS   129.237500  🏆 13.03x faster
lapx-batch-jvsa    ✅ PASS   141.812300  🏆 11.88x faster
lapx-batch-jvs     ✅ PASS   146.593850  🏆 11.49x faster
lapx-loop-jvh      ✅ PASS   351.382500  🏆 4.79x faster
lapx-loop-jvr      ✅ PASS   377.152950  🏆 4.47x faster
lapx-loop-jvx      ✅ PASS  1277.929950  🏆 1.32x faster
lapx-loop-jvs      ✅ PASS  1523.419650  🏆 1.11x faster
scipy-loop         ⭐ BASE  1684.425400  ⭐ baseline
---------------------------------------------------------

### Sparse 50 x (2000x2000) | target density=5.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    65.181750  🥇 77.99x faster
lapx-batch-jvh     ✅ PASS   211.792850  🥈 24.00x faster
lapx-batch-jvr     ✅ PASS   220.376550  🥉 23.07x faster
lapx-batch-jvxa    ✅ PASS   470.618900  🏆 10.80x faster
lapx-batch-jvx     ✅ PASS   475.685650  🏆 10.69x faster
lapx-batch-jvsa64  ✅ PASS   478.610150  🏆 10.62x faster
lapx-batch-jvsa    ✅ PASS   479.885800  🏆 10.59x faster
lapx-batch-jvs     ✅ PASS   490.134050  🏆 10.37x faster
lapx-batch-mod-1t  ✅ PASS   532.491650  🏆 9.55x faster
lapx-loop-mod      ✅ PASS   533.744150  🏆 9.52x faster
lapx-loop-jvr      ✅ PASS  1057.223050  🏆 4.81x faster
lapx-loop-jvh      ✅ PASS  1087.284550  🏆 4.68x faster
lapx-loop-jvx      ✅ PASS  3641.297100  🏆 1.40x faster
lapx-loop-jvs      ✅ PASS  4415.208950  🏆 1.15x faster
scipy-loop         ⭐ BASE  5083.309300  ⭐ baseline
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

<details><summary>📊 Historical tracking results (LAPX 0.13.0):</summary><br>

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.17.

```
lapx==0.13.0
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
10x10     | 0.000033s 3rd  | 0.000038s ✗ 8th | 0.000036s ✓ 5th | 0.000037s ✓ 6th
25x20     | 0.000036s 3rd  | 0.000043s ✗ 8th | 0.000040s ✓ 4th | 0.000040s ✓ 5th
50x50     | 0.000057s 6th  | 0.000067s ✗ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000143s 6th  | 0.000519s ✓ 7th | 0.000100s ✓ 3rd | 0.000102s ✓ 4th
250x250   | 0.001111s 7th  | 0.001026s ✗ 6th | 0.000367s ✓ 3rd | 0.000369s ✓ 4th
550x500   | 0.003344s 6th  | 0.010420s ✓ 7th | 0.001056s ✓ 5th | 0.001039s ✓ 4th
1000x1000 | 0.023462s 6th  | 0.041104s ✓ 8th | 0.015933s ✓ 4th | 0.015391s ✓ 3rd
2000x2500 | 0.037316s 6th  | 2.194672s ✓ 8th | 0.017909s ✓ 5th | 0.017574s ✓ 4th
5000x5000 | 1.173252s 7th  | 1.559677s ✓ 8th | 0.639932s ✓ 4th | 0.544521s ✓ 3rd
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 4th | 0.000037s ✓ 7th | 0.000032s ✓ 2nd | 0.000032s ✓ 1st
25x20     | 0.000040s ✓ 6th | 0.000040s ✓ 7th | 0.000033s ✓ 2nd | 0.000033s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000046s ✓ 5th | 0.000039s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000641s ✓ 8th | 0.000104s ✓ 5th | 0.000064s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001183s ✓ 8th | 0.000394s ✓ 5th | 0.000276s ✓ 2nd | 0.000268s ✓ 1st
550x500   | 0.016428s ✓ 8th | 0.000948s ✓ 3rd | 0.000614s ✓ 1st | 0.000648s ✓ 2nd
1000x1000 | 0.024766s ✓ 7th | 0.018306s ✓ 5th | 0.004276s ✓ 2nd | 0.004259s ✓ 1st
2000x2500 | 1.739532s ✓ 7th | 0.013891s ✓ 3rd | 0.004454s ✓ 1st | 0.005007s ✓ 2nd
5000x5000 | 1.171618s ✓ 6th | 0.652926s ✓ 5th | 0.276686s ✓ 2nd | 0.237941s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   248.2882 ms | ✅ | 🥇x6 🥈x3
     2. LAPX LAPJVR    :   286.4735 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJVX    :   579.1163 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🥴x1
     4. LAPX LAPJV     :   675.4193 ms | ✅ | 🥉x2 🚩x4 🏳️x3
     5. LAPX LAPJVS    :   686.6932 ms | ✅ | 🥉x2 🏳️x5 🗿x2
     6. BASELINE SciPy :  1238.7516 ms | ⭐ | 🥉x2 🥴x5 🗿x2
     7. LAPX LAPJVC    :  2954.3077 ms | ✅ | 🚩x1 🥴x2 🗿x3 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3807.5667 ms | ⚠️ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 2nd  | 0.000034s ✗ 8th | 0.000033s ✓ 7th | 0.000033s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000040s ✗ 8th | 0.000037s ✓ 4th | 0.000037s ✓ 5th
50x50     | 0.000056s 6th  | 0.000071s ✗ 8th | 0.000044s ✓ 3rd | 0.000045s ✓ 4th
100x150   | 0.000149s 6th  | 0.000571s ✓ 7th | 0.000105s ✓ 4th | 0.000105s ✓ 3rd
250x250   | 0.001120s 6th  | 0.001123s ✓ 7th | 0.000376s ✓ 4th | 0.000375s ✓ 3rd
550x500   | 0.003520s 6th  | 0.011172s ✓ 7th | 0.001144s ✓ 5th | 0.001076s ✓ 4th
1000x1000 | 0.023177s 6th  | 0.038715s ✓ 8th | 0.015283s ✓ 4th | 0.014982s ✓ 3rd
2000x2500 | 0.035127s 6th  | 1.832158s ✓ 8th | 0.016111s ✓ 5th | 0.015729s ✓ 4th
5000x5000 | 1.188143s 6th  | 1.735448s ✓ 8th | 0.553136s ✓ 3rd | 0.657660s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000032s ✓ 5th | 0.000032s ✓ 4th | 0.000030s ✓ 3rd | 0.000028s ✓ 1st
25x20     | 0.000039s ✓ 7th | 0.000038s ✓ 6th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000062s ✓ 7th | 0.000045s ✓ 5th | 0.000038s ✓ 1st | 0.000039s ✓ 2nd
100x150   | 0.000642s ✓ 8th | 0.000108s ✓ 5th | 0.000064s ✓ 2nd | 0.000064s ✓ 1st
250x250   | 0.001178s ✓ 8th | 0.000410s ✓ 5th | 0.000276s ✓ 2nd | 0.000271s ✓ 1st
550x500   | 0.016626s ✓ 8th | 0.000972s ✓ 3rd | 0.000620s ✓ 1st | 0.000672s ✓ 2nd
1000x1000 | 0.024535s ✓ 7th | 0.017804s ✓ 5th | 0.004394s ✓ 2nd | 0.004136s ✓ 1st
2000x2500 | 1.660876s ✓ 7th | 0.012098s ✓ 3rd | 0.004324s ✓ 2nd | 0.004282s ✓ 1st
5000x5000 | 1.277711s ✓ 7th | 0.684547s ✓ 5th | 0.253167s ✓ 1st | 0.277904s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   262.9434 ms | ✅ | 🥇x4 🥈x4 🥉x1
     2. LAPX LAPJVH    :   287.4261 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJV     :   586.2694 ms | ✅ | 🥉x2 🚩x4 🏳️x2 🗿x1
     4. LAPX LAPJVX    :   690.0420 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🥴x1
     5. LAPX LAPJVS    :   716.0532 ms | ✅ | 🥉x2 🚩x1 🏳️x5 🥴x1
     6. BASELINE SciPy :  1251.3540 ms | ⭐ | 🥈x1 🥉x1 🥴x7
     7. LAPX LAPJVC    :  2981.7024 ms | ✅ | 🏳️x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3619.3319 ms | ⚠️ | 🗿x3 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 2nd  | 0.000034s ✗ 8th | 0.000033s ✓ 7th | 0.000033s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000041s ✓ 8th | 0.000038s ✓ 5th | 0.000039s ✓ 6th
50x50     | 0.000057s 6th  | 0.000073s ✓ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000140s 6th  | 0.000579s ✓ 7th | 0.000116s ✓ 5th | 0.000111s ✓ 4th
250x250   | 0.001127s 6th  | 0.001159s ✓ 7th | 0.000374s ✓ 4th | 0.000373s ✓ 3rd
550x500   | 0.003552s 6th  | 0.011719s ✓ 7th | 0.001087s ✓ 5th | 0.001070s ✓ 4th
1000x1000 | 0.023303s 6th  | 0.041707s ✓ 8th | 0.016101s ✓ 4th | 0.015411s ✓ 3rd
2000x2500 | 0.036757s 6th  | 2.208501s ✓ 8th | 0.017881s ✓ 5th | 0.017577s ✓ 4th
5000x5000 | 1.112623s 6th  | 1.599544s ✓ 8th | 0.584984s ✓ 3rd | 0.598554s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000032s ✓ 5th | 0.000032s ✓ 4th | 0.000029s ✓ 1st | 0.000032s ✓ 3rd
25x20     | 0.000039s ✓ 7th | 0.000038s ✓ 4th | 0.000031s ✓ 2nd | 0.000030s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000047s ✓ 5th | 0.000039s ✓ 2nd | 0.000039s ✓ 1st
100x150   | 0.000650s ✓ 8th | 0.000104s ✓ 3rd | 0.000069s ✓ 2nd | 0.000063s ✓ 1st
250x250   | 0.001183s ✓ 8th | 0.000413s ✓ 5th | 0.000280s ✓ 2nd | 0.000273s ✓ 1st
550x500   | 0.016490s ✓ 8th | 0.000952s ✓ 3rd | 0.000703s ✓ 1st | 0.000737s ✓ 2nd
1000x1000 | 0.026247s ✓ 7th | 0.018946s ✓ 5th | 0.004335s ✓ 1st | 0.004355s ✓ 2nd
2000x2500 | 1.695714s ✓ 7th | 0.013886s ✓ 3rd | 0.005160s ✓ 2nd | 0.004983s ✓ 1st
5000x5000 | 1.212405s ✓ 7th | 0.668355s ✓ 5th | 0.258439s ✓ 2nd | 0.238361s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   248.8726 ms | ✅ | 🥇x6 🥈x2 🥉x1
     2. LAPX LAPJVR    :   269.0836 ms | ✅ | 🥇x3 🥈x6
     3. LAPX LAPJV     :   620.6595 ms | ✅ | 🥉x1 🚩x3 🏳️x4 🗿x1
     4. LAPX LAPJVX    :   633.2131 ms | ✅ | 🥉x3 🚩x4 🥴x2
     5. LAPX LAPJVS    :   702.7721 ms | ✅ | 🥉x3 🚩x2 🏳️x4
     6. BASELINE SciPy :  1177.6221 ms | ⭐ | 🥈x1 🥉x1 🥴x7
     7. LAPX LAPJVC    :  2952.8227 ms | ✅ | 🏳️x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3863.3558 ms | ⚠️ | 🗿x3 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 3rd  | 0.000034s ✓ 8th | 0.000033s ✓ 7th | 0.000032s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000045s ✓ 8th | 0.000041s ✓ 7th | 0.000038s ✓ 5th
50x50     | 0.000056s 6th  | 0.000064s ✓ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000136s 6th  | 0.000556s ✓ 7th | 0.000103s ✓ 3rd | 0.000105s ✓ 4th
250x250   | 0.001125s 7th  | 0.001118s ✓ 6th | 0.000369s ✓ 4th | 0.000368s ✓ 3rd
550x500   | 0.003471s 6th  | 0.010857s ✓ 7th | 0.001131s ✓ 5th | 0.001103s ✓ 4th
1000x1000 | 0.022955s 6th  | 0.041306s ✓ 8th | 0.015928s ✓ 4th | 0.014967s ✓ 3rd
2000x2500 | 0.036690s 6th  | 2.151244s ✓ 8th | 0.018985s ✓ 5th | 0.018215s ✓ 4th
5000x5000 | 1.155355s 6th  | 1.754843s ✓ 8th | 0.655778s ✓ 3rd | 0.658630s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000032s ✓ 5th | 0.000032s ✓ 4th | 0.000028s ✓ 2nd | 0.000028s ✓ 1st
25x20     | 0.000039s ✓ 6th | 0.000038s ✓ 4th | 0.000031s ✓ 1st | 0.000031s ✓ 2nd
50x50     | 0.000063s ✓ 7th | 0.000045s ✓ 5th | 0.000038s ✓ 1st | 0.000040s ✓ 2nd
100x150   | 0.000644s ✓ 8th | 0.000106s ✓ 5th | 0.000068s ✓ 2nd | 0.000063s ✓ 1st
250x250   | 0.001163s ✓ 8th | 0.000411s ✓ 5th | 0.000275s ✓ 1st | 0.000300s ✓ 2nd
550x500   | 0.016974s ✓ 8th | 0.000981s ✓ 3rd | 0.000620s ✓ 1st | 0.000852s ✓ 2nd
1000x1000 | 0.024671s ✓ 7th | 0.018516s ✓ 5th | 0.004342s ✓ 2nd | 0.004211s ✓ 1st
2000x2500 | 1.708798s ✓ 7th | 0.013369s ✓ 3rd | 0.005102s ✓ 2nd | 0.005005s ✓ 1st
5000x5000 | 1.283575s ✓ 7th | 0.696158s ✓ 5th | 0.282439s ✓ 2nd | 0.276299s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   286.8285 ms | ✅ | 🥇x5 🥈x4
     2. LAPX LAPJVR    :   292.9436 ms | ✅ | 🥇x4 🥈x5
     3. LAPX LAPJV     :   692.4125 ms | ✅ | 🥉x2 🚩x3 🏳️x2 🗿x2
     4. LAPX LAPJVX    :   693.5026 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🥴x1
     5. LAPX LAPJVS    :   729.6565 ms | ✅ | 🥉x2 🚩x2 🏳️x5
     6. BASELINE SciPy :  1219.8498 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3035.9578 ms | ✅ | 🏳️x1 🥴x1 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3960.0672 ms | ✅ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000030s 1st  | 0.000034s ✓ 8th | 0.000033s ✓ 6th | 0.000033s ✓ 7th
25x20     | 0.000033s 3rd  | 0.000041s ✓ 8th | 0.000040s ✓ 7th | 0.000037s ✓ 4th
50x50     | 0.000056s 6th  | 0.000065s ✓ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000137s 6th  | 0.000597s ✓ 7th | 0.000105s ✓ 5th | 0.000104s ✓ 4th
250x250   | 0.001126s 6th  | 0.001146s ✓ 7th | 0.000372s ✓ 3rd | 0.000375s ✓ 4th
550x500   | 0.003477s 6th  | 0.011444s ✓ 7th | 0.001139s ✓ 5th | 0.001111s ✓ 4th
1000x1000 | 0.023374s 6th  | 0.042982s ✓ 8th | 0.016034s ✓ 4th | 0.015921s ✓ 3rd
2000x2500 | 0.037402s 6th  | 1.951593s ✓ 8th | 0.018616s ✓ 5th | 0.018490s ✓ 4th
5000x5000 | 1.095558s 6th  | 1.645047s ✓ 8th | 0.623146s ✓ 3rd | 0.647310s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000032s ✓ 4th | 0.000032s ✓ 5th | 0.000030s ✓ 2nd | 0.000030s ✓ 3rd
25x20     | 0.000038s ✓ 6th | 0.000038s ✓ 5th | 0.000031s ✓ 2nd | 0.000031s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000048s ✓ 5th | 0.000038s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000644s ✓ 8th | 0.000104s ✓ 3rd | 0.000067s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001181s ✓ 8th | 0.000427s ✓ 5th | 0.000278s ✓ 2nd | 0.000273s ✓ 1st
550x500   | 0.016214s ✓ 8th | 0.000992s ✓ 3rd | 0.000625s ✓ 1st | 0.000656s ✓ 2nd
1000x1000 | 0.025337s ✓ 7th | 0.018501s ✓ 5th | 0.004283s ✓ 2nd | 0.004262s ✓ 1st
2000x2500 | 1.702979s ✓ 7th | 0.014027s ✓ 3rd | 0.004377s ✓ 1st | 0.004578s ✓ 2nd
5000x5000 | 1.259725s ✓ 7th | 0.697533s ✓ 5th | 0.262676s ✓ 1st | 0.278984s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   272.4042 ms | ✅ | 🥇x3 🥈x6
     2. LAPX LAPJVH    :   288.9139 ms | ✅ | 🥇x5 🥈x3 🥉x1
     3. LAPX LAPJV     :   659.5307 ms | ✅ | 🥉x2 🚩x2 🏳️x3 🥴x1 🗿x1
     4. LAPX LAPJVX    :   683.4269 ms | ✅ | 🥉x2 🚩x6 🗿x1
     5. LAPX LAPJVS    :   731.7007 ms | ✅ | 🥉x3 🏳️x6
     6. BASELINE SciPy :  1161.1938 ms | ⭐ | 🥇x1 🥉x1 🥴x7
     7. LAPX LAPJVC    :  3006.2143 ms | ✅ | 🚩x1 🥴x1 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3652.9490 ms | ✅ | 🗿x3 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these historical runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. R/H have the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
