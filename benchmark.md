[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# 🏆 Quick Benchmark

The [single-matrix](benchmarks/benchmark_single.py), [batch](benchmarks/benchmark_batch.py),
and [tracking](benchmarks/benchmark_tracking.py) scripts compare assignment workflows with SciPy on your machine.
The recorded results below come from earlier versions of the scripts.

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

### Historical results (lapx 0.11.0rc1)

These logs use lapx 0.11.0rc1 and older benchmark scripts. They retain the earlier output format,
do not include R/H, and were not measured with the current repeat method.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.

```
lapx==0.11.0rc1 (2026/10/20)
scipy==1.17.1
numpy==2.4.6
```

<details><summary>📄 Historical single results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new4\lapx\benchmarks>python benchmark_single.py


Note: R/H native float64, JVS default float32.


### Matrix 4 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.000464  🥇 3.68x faster
lapjvr   ✅ PASS   0.000488  🥈 3.50x faster
scipy    ⭐ BASE   0.001708  ⭐ baseline
lapjvc   ✅ PASS   0.003748  🐌 2.19x slower
lapjvxa  ✅ PASS   0.004932  🐌 2.89x slower
lapjvx   ✅ PASS   0.005388  🐌 3.15x slower
lapjv    ✅ PASS   0.005888  🐌 3.45x slower
lapjvs   ✅ PASS   0.007336  🐌 4.30x slower
lapjvsa  ✅ PASS   0.008112  🐌 4.75x slower
--------------------------------------------

### Matrix 5 x 5 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000496  🥇 3.36x faster
lapjvh   ✅ PASS   0.000512  🥈 3.26x faster
lapjvsa  ✅ PASS   0.001220  🥉 1.37x faster
scipy    ⭐ BASE   0.001668  ⭐ baseline
lapjvxa  ✅ PASS   0.002968  🐌 1.78x slower
lapjvx   ✅ PASS   0.003548  🐌 2.13x slower
lapjvc   ✅ PASS   0.003724  🐌 2.23x slower
lapjvs   ✅ PASS   0.003812  🐌 2.29x slower
lapjv    ✅ PASS   0.003928  🐌 2.35x slower
--------------------------------------------

### Matrix 5 x 6 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.000448  🥇 3.80x faster
lapjvh   ✅ PASS   0.000496  🥈 3.44x faster
scipy    ⭐ BASE   0.001704  ⭐ baseline
lapjvc   ✅ PASS   0.003952  🐌 2.32x slower
lapjvxa  ✅ PASS   0.005152  🐌 3.02x slower
lapjvx   ✅ PASS   0.005368  🐌 3.15x slower
lapjvs   ✅ PASS   0.005760  🐌 3.38x slower
lapjv    ✅ PASS   0.005992  🐌 3.52x slower
lapjvsa  ✅ PASS   0.007168  🐌 4.21x slower
--------------------------------------------

### Matrix 45 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.002592  🥇 6.49x faster
lapjvh   ✅ PASS   0.002800  🥈 6.01x faster
lapjvxa  ✅ PASS   0.009688  🥉 1.74x faster
lapjvs   ✅ PASS   0.010780  🏆 1.56x faster
lapjvx   ✅ PASS   0.011500  🏆 1.46x faster
lapjv    ✅ PASS   0.011592  🏆 1.45x faster
lapjvsa  ✅ PASS   0.013276  🏆 1.27x faster
scipy    ⭐ BASE   0.016820  ⭐ baseline
lapjvc   ✅ PASS   0.039256  🐌 2.33x slower
--------------------------------------------

### Matrix 50 x 50 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvh   ✅ PASS   0.005480  🥇 4.43x faster
lapjvr   ✅ PASS   0.005548  🥈 4.37x faster
lapjvsa  ✅ PASS   0.009436  🥉 2.57x faster
lapjvxa  ✅ PASS   0.009992  🏆 2.43x faster
lapjv    ✅ PASS   0.011048  🏆 2.20x faster
lapjvx   ✅ PASS   0.011120  🏆 2.18x faster
lapjvs   ✅ PASS   0.012420  🏆 1.95x faster
scipy    ⭐ BASE   0.024264  ⭐ baseline
lapjvc   ✅ PASS   0.024796  🐌 1.02x slower
--------------------------------------------

### Matrix 50 x 55 | float64 | return_cost=False

* Median of 3 shuffled rounds, 25 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.003096  🥇 6.65x faster
lapjvh   ✅ PASS   0.003232  🥈 6.37x faster
lapjvxa  ✅ PASS   0.011824  🥉 1.74x faster
lapjvx   ✅ PASS   0.012104  🏆 1.70x faster
lapjvs   ✅ PASS   0.015420  🏆 1.33x faster
lapjvsa  ✅ PASS   0.015680  🏆 1.31x faster
lapjv    ✅ PASS   0.015996  🏆 1.29x faster
scipy    ⭐ BASE   0.020584  ⭐ baseline
lapjvc   ✅ PASS   0.051984  🐌 2.53x slower
--------------------------------------------

### Matrix 450 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.336300  🥇 6.89x faster
lapjvh   ✅ PASS   0.338700  🥈 6.84x faster
lapjvs   ✅ PASS   0.520100  🥉 4.46x faster
lapjvsa  ✅ PASS   0.543000  🏆 4.27x faster
lapjvx   ✅ PASS   0.820800  🏆 2.82x faster
lapjvxa  ✅ PASS   0.824700  🏆 2.81x faster
lapjv    ✅ PASS   0.849100  🏆 2.73x faster
scipy    ⭐ BASE   2.317800  ⭐ baseline
lapjvc   ✅ PASS  11.112200  🐌 4.79x slower
--------------------------------------------

### Matrix 500 x 500 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.856900  🥇 5.51x faster
lapjvh   ✅ PASS   0.860400  🥈 5.49x faster
lapjvsa  ✅ PASS   2.077400  🥉 2.27x faster
lapjvxa  ✅ PASS   2.085900  🏆 2.26x faster
lapjvx   ✅ PASS   2.094600  🏆 2.25x faster
lapjv    ✅ PASS   2.100200  🏆 2.25x faster
lapjvs   ✅ PASS   2.147800  🏆 2.20x faster
scipy    ⭐ BASE   4.721500  ⭐ baseline
lapjvc   ✅ PASS   5.115700  🐌 1.08x slower
--------------------------------------------

### Matrix 500 x 550 | float64 | return_cost=False

* Median of 3 shuffled rounds, 1 calls/round;
input seeds=2026..2028; warmup each round.

Solver   Check    Time (ms)  vs SciPy
--------------------------------------------
lapjvr   ✅ PASS   0.386200  🥇 7.00x faster
lapjvh   ✅ PASS   0.390000  🥈 6.93x faster
lapjvs   ✅ PASS   0.760500  🥉 3.55x faster
lapjvsa  ✅ PASS   0.788500  🏆 3.43x faster
lapjvxa  ✅ PASS   0.936300  🏆 2.89x faster
lapjvx   ✅ PASS   0.945200  🏆 2.86x faster
lapjv    ✅ PASS   0.948100  🏆 2.85x faster
scipy    ⭐ BASE   2.701600  ⭐ baseline
lapjvc   ✅ PASS  14.136200  🐌 5.23x slower
--------------------------------------------

### Matrix 2500 x 5000 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS      6.866500  🥇 7.64x faster
lapjvh   ✅ PASS      7.093300  🥈 7.40x faster
scipy    ⭐ BASE     52.483000  ⭐ baseline
lapjvsa  ✅ PASS     52.949600  🐌 1.01x slower
lapjvs   ✅ PASS     58.164000  🐌 1.11x slower
lapjv    ✅ PASS     72.735500  🐌 1.39x slower
lapjvxa  ✅ PASS     88.067800  🐌 1.68x slower
lapjvx   ✅ PASS     88.309100  🐌 1.68x slower
lapjvc   ✅ PASS  12187.386500  🐌 232.22x slower
-------------------------------------------------

### Matrix 5000 x 5000 | float64 | return_cost=False

Solver   Check      Time (ms)  vs SciPy
----------------------------------------------
lapjvh   ✅ PASS   251.584600  🥇 4.46x faster
lapjvr   ✅ PASS   274.450000  🥈 4.09x faster
lapjvsa  ✅ PASS   366.985100  🥉 3.06x faster
lapjvs   ✅ PASS   374.470100  🏆 3.00x faster
lapjvx   ✅ PASS   616.771500  🏆 1.82x faster
lapjvxa  ✅ PASS   621.376400  🏆 1.81x faster
lapjv    ✅ PASS   625.615700  🏆 1.79x faster
scipy    ⭐ BASE  1122.227200  ⭐ baseline
lapjvc   ✅ PASS  1294.830600  🐌 1.15x slower
----------------------------------------------

### Matrix 5000 x 7500 | float64 | return_cost=False

Solver   Check       Time (ms)  vs SciPy
-------------------------------------------------
lapjvr   ✅ PASS     19.430500  🥇 10.43x faster
lapjvh   ✅ PASS     27.205000  🥈 7.45x faster
lapjvsa  ✅ PASS    105.869500  🥉 1.91x faster
lapjvs   ✅ PASS    112.006600  🏆 1.81x faster
lapjvx   ✅ PASS    147.127000  🏆 1.38x faster
lapjv    ✅ PASS    150.552200  🏆 1.35x faster
lapjvxa  ✅ PASS    158.551800  🏆 1.28x faster
scipy    ⭐ BASE    202.640900  ⭐ baseline
lapjvc   ✅ PASS  55465.559500  🐌 273.71x slower
-------------------------------------------------
```

</details>

<details><summary>🗂️ Historical batch results:</summary><br>

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new4\lapx\benchmarks>python benchmark_batch.py


Note: R/H native float64, JVS default float32, jvsa64 float64.


### Dense 10 x (4000x4000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   305.307200  🥇 21.81x faster
lapx-batch-jvr     ✅ PASS   335.637800  🥈 19.84x faster
lapx-batch-jvsa    ✅ PASS   405.485200  🥉 16.42x faster
lapx-batch-jvs     ✅ PASS   424.436800  🏆 15.69x faster
lapx-batch-jvsa64  ✅ PASS  1052.290300  🏆 6.33x faster
lapx-batch-jvxa    ✅ PASS  1127.172700  🏆 5.91x faster
lapx-batch-jvx     ✅ PASS  1156.924600  🏆 5.76x faster
lapx-loop-jvh      ✅ PASS  1479.487900  🏆 4.50x faster
lapx-loop-jvr      ✅ PASS  1574.337200  🏆 4.23x faster
lapx-loop-jvs      ✅ PASS  2615.703100  🏆 2.55x faster
lapx-loop-jvx      ✅ PASS  5226.083500  🏆 1.27x faster
scipy-loop         ⭐ BASE  6659.042500  ⭐ baseline
---------------------------------------------------------

### Dense 20 x (3000x2000) | n_threads=0 | return_cost=False

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS    70.880100  🥇 14.15x faster
lapx-batch-jvr     ✅ PASS    78.406900  🥈 12.79x faster
lapx-batch-jvs     ✅ PASS    94.997800  🥉 10.56x faster
lapx-batch-jvsa    ✅ PASS    99.014600  🏆 10.13x faster
lapx-batch-jvsa64  ✅ PASS   124.270600  🏆 8.07x faster
lapx-batch-jvxa    ✅ PASS   127.176400  🏆 7.89x faster
lapx-batch-jvx     ✅ PASS   146.063700  🏆 6.87x faster
lapx-loop-jvr      ✅ PASS   291.174600  🏆 3.44x faster
lapx-loop-jvh      ✅ PASS   303.220800  🏆 3.31x faster
lapx-loop-jvs      ✅ PASS   791.096100  🏆 1.27x faster
lapx-loop-jvx      ✅ PASS   973.291000  🏆 1.03x faster
scipy-loop         ⭐ BASE  1002.891400  ⭐ baseline
---------------------------------------------------------

### Dense 50 x (2000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS   222.424700  🥇 26.60x faster
lapx-batch-jvr     ✅ PASS   230.883300  🥈 25.63x faster
lapx-batch-jvsa    ✅ PASS   298.122500  🥉 19.85x faster
lapx-batch-jvs     ✅ PASS   304.841050  🏆 19.41x faster
lapx-batch-jvsa64  ✅ PASS   434.623850  🏆 13.61x faster
lapx-batch-jvxa    ✅ PASS   450.615250  🏆 13.13x faster
lapx-batch-jvx     ✅ PASS   451.959650  🏆 13.09x faster
lapx-loop-jvh      ✅ PASS  1141.322250  🏆 5.18x faster
lapx-loop-jvr      ✅ PASS  1164.852250  🏆 5.08x faster
lapx-loop-jvs      ✅ PASS  2920.143950  🏆 2.03x faster
lapx-loop-jvx      ✅ PASS  3729.783450  🏆 1.59x faster
scipy-loop         ⭐ BASE  5917.139250  ⭐ baseline
---------------------------------------------------------

### Dense 100 x (1000x2000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-jvh     ✅ PASS    21.931950  🥇 38.30x faster
lapx-batch-jvr     ✅ PASS    22.040100  🥈 38.11x faster
lapx-loop-jvr      ✅ PASS   107.704850  🥉 7.80x faster
lapx-loop-jvh      ✅ PASS   114.691150  🏆 7.32x faster
lapx-batch-jvsa    ✅ PASS   121.854950  🏆 6.89x faster
lapx-batch-jvs     ✅ PASS   126.950400  🏆 6.62x faster
lapx-batch-jvxa    ✅ PASS   216.949200  🏆 3.87x faster
lapx-batch-jvsa64  ✅ PASS   222.754150  🏆 3.77x faster
lapx-batch-jvx     ✅ PASS   223.249700  🏆 3.76x faster
lapx-loop-jvs      ✅ PASS   781.342150  🏆 1.08x faster
scipy-loop         ⭐ BASE   839.950050  ⭐ baseline
lapx-loop-jvx      ✅ PASS  1180.486050  🐌 1.41x slower
---------------------------------------------------------

### Dense 500 x (1000x1000) | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check       Time (ms)  vs SciPy
----------------------------------------------------------
lapx-batch-jvh     ✅ PASS    308.687250  🥇 36.61x faster
lapx-batch-jvr     ✅ PASS    311.188400  🥈 36.31x faster
lapx-batch-jvs     ✅ PASS    523.695450  🥉 21.58x faster
lapx-batch-jvsa    ✅ PASS    525.729000  🏆 21.49x faster
lapx-batch-jvsa64  ✅ PASS    577.253800  🏆 19.57x faster
lapx-batch-jvx     ✅ PASS    578.432000  🏆 19.53x faster
lapx-batch-jvxa    ✅ PASS    586.463900  🏆 19.27x faster
lapx-loop-jvh      ✅ PASS   2119.521850  🏆 5.33x faster
lapx-loop-jvr      ✅ PASS   2151.523350  🏆 5.25x faster
lapx-loop-jvs      ✅ PASS   6447.690350  🏆 1.75x faster
lapx-loop-jvx      ✅ PASS   6820.104200  🏆 1.66x faster
scipy-loop         ⭐ BASE  11299.642650  ⭐ baseline
----------------------------------------------------------

### Sparse 100 x (1000x1000) | target density=1.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    18.120150  🥇 92.85x faster
lapx-batch-jvh     ✅ PASS    59.869300  🥈 28.10x faster
lapx-batch-jvr     ✅ PASS    60.075950  🥉 28.00x faster
lapx-loop-mod      ✅ PASS    98.719050  🏆 17.04x faster
lapx-batch-mod-1t  ✅ PASS    98.949550  🏆 17.00x faster
lapx-batch-jvsa    ✅ PASS   111.273100  🏆 15.12x faster
lapx-batch-jvs     ✅ PASS   113.086850  🏆 14.88x faster
lapx-batch-jvsa64  ✅ PASS   123.190500  🏆 13.66x faster
lapx-batch-jvx     ✅ PASS   123.686150  🏆 13.60x faster
lapx-batch-jvxa    ✅ PASS   126.298500  🏆 13.32x faster
lapx-loop-jvh      ✅ PASS   348.536900  🏆 4.83x faster
lapx-loop-jvr      ✅ PASS   364.548050  🏆 4.62x faster
lapx-loop-jvs      ✅ PASS  1191.784700  🏆 1.41x faster
lapx-loop-jvx      ✅ PASS  1262.302300  🏆 1.33x faster
scipy-loop         ⭐ BASE  1682.410900  ⭐ baseline
---------------------------------------------------------

### Sparse 50 x (2000x2000) | target density=5.00% | n_threads=0 | return_cost=False

* Median of 2 shuffled rounds;
input seeds=2026..2027; warmup each round.

Solver             Check      Time (ms)  vs SciPy
---------------------------------------------------------
lapx-batch-mod     ✅ PASS    60.044800  🥇 85.32x faster
lapx-batch-jvh     ✅ PASS   210.457550  🥈 24.34x faster
lapx-batch-jvr     ✅ PASS   213.821850  🥉 23.96x faster
lapx-batch-jvsa    ✅ PASS   282.295000  🏆 18.15x faster
lapx-batch-jvs     ✅ PASS   288.003800  🏆 17.79x faster
lapx-batch-jvx     ✅ PASS   457.999100  🏆 11.19x faster
lapx-batch-jvsa64  ✅ PASS   468.105650  🏆 10.94x faster
lapx-batch-jvxa    ✅ PASS   477.668100  🏆 10.73x faster
lapx-batch-mod-1t  ✅ PASS   525.989900  🏆 9.74x faster
lapx-loop-mod      ✅ PASS   531.794600  🏆 9.63x faster
lapx-loop-jvr      ✅ PASS  1064.626250  🏆 4.81x faster
lapx-loop-jvh      ✅ PASS  1081.290100  🏆 4.74x faster
lapx-loop-jvs      ✅ PASS  2821.016850  🏆 1.82x faster
lapx-loop-jvx      ✅ PASS  3654.051850  🏆 1.40x faster
scipy-loop         ⭐ BASE  5123.226500  ⭐ baseline
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

<details><summary>📊 Historical tracking results (lapx 0.11.0rc1):</summary><br>

These logs predate the current repeat method and R/H rows.

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.

```
lapx==0.11.0rc1 (2026/10/20)
scipy==1.17.1
numpy==2.4.6
```

```
Microsoft Windows [Version 10.0.26300.9711]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new4\lapx\benchmarks>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000032s 3rd  | 0.000037s ✗ 7th | 0.000035s ✓ 4th | 0.000035s ✓ 5th
25x20     | 0.000035s 3rd  | 0.000041s ✗ 6th | 0.000039s ✓ 5th | 0.000047s ✓ 8th
50x50     | 0.000058s 6th  | 0.000067s ✗ 8th | 0.000048s ✓ 5th | 0.000045s ✓ 3rd
100x150   | 0.000138s 6th  | 0.000480s ✓ 7th | 0.000101s ✓ 4th | 0.000108s ✓ 5th
250x250   | 0.001118s 7th  | 0.001004s ✗ 6th | 0.000363s ✓ 3rd | 0.000366s ✓ 4th
550x500   | 0.003476s 6th  | 0.011500s ✓ 7th | 0.001115s ✓ 5th | 0.001092s ✓ 4th
1000x1000 | 0.023021s 6th  | 0.038744s ✓ 8th | 0.015356s ✓ 3rd | 0.015548s ✓ 5th
2000x2500 | 0.036226s 6th  | 2.091826s ✓ 8th | 0.018083s ✓ 5th | 0.017675s ✓ 4th
5000x5000 | 1.115714s 6th  | 1.619377s ✓ 8th | 0.552453s ✓ 4th | 0.645715s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 6th | 0.000038s ✓ 8th | 0.000031s ✓ 2nd | 0.000030s ✓ 1st
25x20     | 0.000042s ✓ 7th | 0.000038s ✓ 4th | 0.000033s ✓ 2nd | 0.000031s ✓ 1st
50x50     | 0.000064s ✓ 7th | 0.000046s ✓ 4th | 0.000038s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000638s ✓ 8th | 0.000100s ✓ 3rd | 0.000066s ✓ 2nd | 0.000062s ✓ 1st
250x250   | 0.001157s ✓ 8th | 0.000374s ✓ 5th | 0.000256s ✓ 1st | 0.000257s ✓ 2nd
550x500   | 0.016645s ✓ 8th | 0.000942s ✓ 3rd | 0.000595s ✓ 1st | 0.000826s ✓ 2nd
1000x1000 | 0.024987s ✓ 7th | 0.015518s ✓ 4th | 0.004184s ✓ 2nd | 0.004031s ✓ 1st
2000x2500 | 1.704036s ✓ 7th | 0.012404s ✓ 3rd | 0.004598s ✓ 2nd | 0.003996s ✓ 1st
5000x5000 | 1.292485s ✓ 7th | 0.378975s ✓ 3rd | 0.275935s ✓ 1st | 0.277989s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   285.7360 ms | ✅ | 🥇x3 🥈x6
     2. LAPX LAPJVH    :   287.2603 ms | ✅ | 🥇x6 🥈x3
     3. LAPX LAPJVS    :   408.4359 ms | ✅ | 🥉x4 🚩x3 🏳️x1 🙅‍♂️x1
     4. LAPX LAPJV     :   587.5927 ms | ✅ | 🥉x2 🚩x3 🏳️x4
     5. LAPX LAPJVX    :   680.6321 ms | ✅ | 🥉x1 🚩x3 🏳️x4 🙅‍♂️x1
     6. BASELINE SciPy :  1179.8184 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3040.0884 ms | ✅ | 🥴x1 🗿x5 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3763.0748 ms | ⚠️ | 🥴x2 🗿x3 🙅‍♂️x4
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 2nd  | 0.000035s ✗ 7th | 0.000033s ✓ 4th | 0.000033s ✓ 3rd
25x20     | 0.000033s 3rd  | 0.000041s ✗ 8th | 0.000037s ✓ 4th | 0.000037s ✓ 5th
50x50     | 0.000056s 6th  | 0.000069s ✗ 8th | 0.000046s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000157s 6th  | 0.000576s ✓ 7th | 0.000109s ✓ 5th | 0.000106s ✓ 3rd
250x250   | 0.001132s 7th  | 0.001121s ✓ 6th | 0.000375s ✓ 3rd | 0.000377s ✓ 4th
550x500   | 0.003465s 6th  | 0.011399s ✓ 7th | 0.001080s ✓ 4th | 0.001086s ✓ 5th
1000x1000 | 0.022778s 6th  | 0.041162s ✓ 8th | 0.015872s ✓ 4th | 0.015416s ✓ 3rd
2000x2500 | 0.037486s 6th  | 2.178234s ✓ 8th | 0.017819s ✓ 5th | 0.017145s ✓ 4th
5000x5000 | 1.174092s 6th  | 1.697081s ✓ 8th | 0.598032s ✓ 4th | 0.648125s ✓ 5th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000043s ✓ 8th | 0.000034s ✓ 5th | 0.000034s ✓ 6th | 0.000028s ✓ 1st
25x20     | 0.000038s ✓ 7th | 0.000037s ✓ 6th | 0.000031s ✓ 2nd | 0.000031s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 1st | 0.000038s ✓ 2nd
100x150   | 0.000642s ✓ 8th | 0.000108s ✓ 4th | 0.000064s ✓ 2nd | 0.000061s ✓ 1st
250x250   | 0.001161s ✓ 8th | 0.000377s ✓ 5th | 0.000270s ✓ 2nd | 0.000261s ✓ 1st
550x500   | 0.016545s ✓ 8th | 0.000881s ✓ 3rd | 0.000599s ✓ 1st | 0.000602s ✓ 2nd
1000x1000 | 0.024377s ✓ 7th | 0.015894s ✓ 5th | 0.004144s ✓ 2nd | 0.004049s ✓ 1st
2000x2500 | 1.720586s ✓ 7th | 0.012190s ✓ 3rd | 0.004586s ✓ 2nd | 0.004549s ✓ 1st
5000x5000 | 1.280558s ✓ 7th | 0.378798s ✓ 3rd | 0.261815s ✓ 1st | 0.272378s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   271.5815 ms | ✅ | 🥇x3 🥈x5 🥴x1
     2. LAPX LAPJVH    :   281.9980 ms | ✅ | 🥇x6 🥈x3
     3. LAPX LAPJVS    :   408.3659 ms | ✅ | 🥉x3 🚩x1 🏳️x4 🥴x1
     4. LAPX LAPJV     :   633.4017 ms | ✅ | 🥉x1 🚩x6 🏳️x2
     5. LAPX LAPJVX    :   682.3707 ms | ✅ | 🥉x4 🚩x2 🏳️x3
     6. BASELINE SciPy :  1239.2296 ms | ⭐ | 🥈x1 🥉x1 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3044.0131 ms | ✅ | 🗿x5 🙅‍♂️x4
     8. LAPX LAPJV-IFT :  3929.7179 ms | ⚠️ | 🥴x1 🗿x3 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000031s 3rd  | 0.000037s ✗ 8th | 0.000035s ✓ 5th | 0.000035s ✓ 6th
25x20     | 0.000034s 3rd  | 0.000042s ✓ 8th | 0.000037s ✓ 4th | 0.000038s ✓ 5th
50x50     | 0.000056s 6th  | 0.000065s ✓ 8th | 0.000045s ✓ 4th | 0.000045s ✓ 3rd
100x150   | 0.000142s 6th  | 0.000588s ✓ 7th | 0.000104s ✓ 4th | 0.000110s ✓ 5th
250x250   | 0.001124s 6th  | 0.001150s ✓ 7th | 0.000376s ✓ 3rd | 0.000434s ✓ 5th
550x500   | 0.003475s 6th  | 0.011255s ✓ 7th | 0.001134s ✓ 5th | 0.001089s ✓ 4th
1000x1000 | 0.022863s 6th  | 0.040968s ✓ 8th | 0.015940s ✓ 5th | 0.015489s ✓ 3rd
2000x2500 | 0.037059s 6th  | 2.107005s ✓ 8th | 0.017796s ✓ 5th | 0.017627s ✓ 4th
5000x5000 | 1.163267s 6th  | 1.733930s ✓ 8th | 0.654927s ✓ 5th | 0.652927s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000036s ✓ 7th | 0.000034s ✓ 4th | 0.000030s ✓ 1st | 0.000030s ✓ 2nd
25x20     | 0.000039s ✓ 7th | 0.000039s ✓ 6th | 0.000031s ✓ 1st | 0.000034s ✓ 2nd
50x50     | 0.000061s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 1st | 0.000038s ✓ 2nd
100x150   | 0.000638s ✓ 8th | 0.000101s ✓ 3rd | 0.000064s ✓ 1st | 0.000065s ✓ 2nd
250x250   | 0.001214s ✓ 8th | 0.000385s ✓ 4th | 0.000269s ✓ 2nd | 0.000258s ✓ 1st
550x500   | 0.016040s ✓ 8th | 0.000996s ✓ 3rd | 0.000576s ✓ 1st | 0.000609s ✓ 2nd
1000x1000 | 0.024558s ✓ 7th | 0.015870s ✓ 4th | 0.004198s ✓ 2nd | 0.003978s ✓ 1st
2000x2500 | 1.737007s ✓ 7th | 0.012274s ✓ 3rd | 0.004065s ✓ 1st | 0.004571s ✓ 2nd
5000x5000 | 1.311709s ✓ 7th | 0.379168s ✓ 3rd | 0.280087s ✓ 2nd | 0.273420s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   283.0026 ms | ✅ | 🥇x3 🥈x6
     2. LAPX LAPJVR    :   289.3575 ms | ✅ | 🥇x6 🥈x3
     3. LAPX LAPJVS    :   408.9130 ms | ✅ | 🥉x4 🚩x3 🏳️x1 🥴x1
     4. LAPX LAPJVX    :   687.7933 ms | ✅ | 🥉x2 🚩x3 🏳️x3 🥴x1
     5. LAPX LAPJV     :   690.3940 ms | ✅ | 🥉x1 🚩x3 🏳️x5
     6. BASELINE SciPy :  1228.0504 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3091.3024 ms | ✅ | 🗿x6 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3895.0392 ms | ⚠️ | 🗿x3 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 3rd  | 0.000038s ✓ 8th | 0.000033s ✓ 5th | 0.000033s ✓ 6th
25x20     | 0.000033s 3rd  | 0.000049s ✓ 8th | 0.000038s ✓ 5th | 0.000037s ✓ 4th
50x50     | 0.000056s 6th  | 0.000065s ✓ 8th | 0.000045s ✓ 4th | 0.000044s ✓ 3rd
100x150   | 0.000141s 6th  | 0.000585s ✓ 7th | 0.000105s ✓ 4th | 0.000104s ✓ 3rd
250x250   | 0.001121s 7th  | 0.001117s ✓ 6th | 0.000383s ✓ 5th | 0.000380s ✓ 4th
550x500   | 0.003438s 6th  | 0.011395s ✓ 7th | 0.001094s ✓ 5th | 0.001083s ✓ 4th
1000x1000 | 0.022706s 6th  | 0.041878s ✓ 8th | 0.015928s ✓ 5th | 0.015629s ✓ 3rd
2000x2500 | 0.035596s 6th  | 2.163564s ✓ 8th | 0.017848s ✓ 4th | 0.017927s ✓ 5th
5000x5000 | 1.127586s 6th  | 1.725706s ✓ 8th | 0.640167s ✓ 5th | 0.612770s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000033s ✓ 7th | 0.000032s ✓ 4th | 0.000029s ✓ 1st | 0.000029s ✓ 2nd
25x20     | 0.000039s ✓ 7th | 0.000038s ✓ 6th | 0.000031s ✓ 2nd | 0.000031s ✓ 1st
50x50     | 0.000062s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 1st | 0.000038s ✓ 2nd
100x150   | 0.000643s ✓ 8th | 0.000106s ✓ 5th | 0.000062s ✓ 2nd | 0.000061s ✓ 1st
250x250   | 0.001173s ✓ 8th | 0.000378s ✓ 3rd | 0.000263s ✓ 2nd | 0.000260s ✓ 1st
550x500   | 0.015989s ✓ 8th | 0.000886s ✓ 3rd | 0.000580s ✓ 1st | 0.000701s ✓ 2nd
1000x1000 | 0.024357s ✓ 7th | 0.015900s ✓ 4th | 0.004126s ✓ 2nd | 0.003988s ✓ 1st
2000x2500 | 1.725748s ✓ 7th | 0.011325s ✓ 3rd | 0.004652s ✓ 2nd | 0.004247s ✓ 1st
5000x5000 | 1.300565s ✓ 7th | 0.377369s ✓ 3rd | 0.251710s ✓ 1st | 0.273771s ✓ 2nd
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVR    :   261.4903 ms | ✅ | 🥇x4 🥈x5
     2. LAPX LAPJVH    :   283.1252 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJVS    :   406.0796 ms | ✅ | 🥉x4 🚩x2 🏳️x2 🥴x1
     4. LAPX LAPJVX    :   648.0079 ms | ✅ | 🥉x3 🚩x4 🏳️x1 🥴x1
     5. LAPX LAPJV     :   675.6392 ms | ✅ | 🚩x3 🏳️x6
     6. BASELINE SciPy :  1190.7077 ms | ⭐ | 🥉x2 🥴x6 🗿x1
     7. LAPX LAPJVC    :  3068.6097 ms | ✅ | 🗿x6 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3944.3959 ms | ✅ | 🥴x1 🗿x2 🙅‍♂️x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

--------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX
--------------------------------------------------------------------------------
10x10     | 0.000029s 3rd  | 0.000033s ✓ 8th | 0.000033s ✓ 7th | 0.000033s ✓ 5th
25x20     | 0.000033s 3rd  | 0.000041s ✓ 7th | 0.000038s ✓ 4th | 0.000045s ✓ 8th
50x50     | 0.000058s 6th  | 0.000066s ✓ 8th | 0.000045s ✓ 3rd | 0.000045s ✓ 4th
100x150   | 0.000147s 6th  | 0.000589s ✓ 7th | 0.000106s ✓ 5th | 0.000106s ✓ 4th
250x250   | 0.001120s 6th  | 0.001138s ✓ 7th | 0.000373s ✓ 4th | 0.000371s ✓ 3rd
550x500   | 0.003473s 6th  | 0.011458s ✓ 7th | 0.001302s ✓ 5th | 0.001074s ✓ 4th
1000x1000 | 0.022652s 6th  | 0.042463s ✓ 8th | 0.015936s ✓ 5th | 0.015448s ✓ 3rd
2000x2500 | 0.036005s 6th  | 2.203505s ✓ 8th | 0.018101s ✓ 5th | 0.017784s ✓ 4th
5000x5000 | 1.185836s 6th  | 1.728481s ✓ 8th | 0.650640s ✓ 5th | 0.646867s ✓ 4th
--------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Size      | LAPX LAPJVC     | LAPX LAPJVS     | LAPX LAPJVR     | LAPX LAPJVH
---------------------------------------------------------------------------------
10x10     | 0.000033s ✓ 6th | 0.000032s ✓ 4th | 0.000028s ✓ 1st | 0.000029s ✓ 2nd
25x20     | 0.000039s ✓ 6th | 0.000039s ✓ 5th | 0.000031s ✓ 2nd | 0.000031s ✓ 1st
50x50     | 0.000063s ✓ 7th | 0.000046s ✓ 5th | 0.000038s ✓ 2nd | 0.000038s ✓ 1st
100x150   | 0.000635s ✓ 8th | 0.000102s ✓ 3rd | 0.000063s ✓ 2nd | 0.000061s ✓ 1st
250x250   | 0.001165s ✓ 8th | 0.000379s ✓ 5th | 0.000272s ✓ 2nd | 0.000264s ✓ 1st
550x500   | 0.016055s ✓ 8th | 0.001012s ✓ 3rd | 0.000565s ✓ 1st | 0.000601s ✓ 2nd
1000x1000 | 0.024362s ✓ 7th | 0.015887s ✓ 4th | 0.004143s ✓ 2nd | 0.003990s ✓ 1st
2000x2500 | 1.744677s ✓ 7th | 0.012428s ✓ 3rd | 0.004609s ✓ 2nd | 0.004586s ✓ 1st
5000x5000 | 1.277330s ✓ 7th | 0.378245s ✓ 3rd | 0.277742s ✓ 2nd | 0.272951s ✓ 1st
---------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVH    :   282.5500 ms | ✅ | 🥇x7 🥈x2
     2. LAPX LAPJVR    :   287.4900 ms | ✅ | 🥇x2 🥈x7
     3. LAPX LAPJVS    :   408.1699 ms | ✅ | 🥉x4 🚩x2 🏳️x3
     4. LAPX LAPJVX    :   681.7735 ms | ✅ | 🥉x2 🚩x5 🏳️x1 🙅‍♂️x1
     5. LAPX LAPJV     :   686.5746 ms | ✅ | 🥉x1 🚩x2 🏳️x5 🗿x1
     6. BASELINE SciPy :  1249.3546 ms | ⭐ | 🥉x2 🥴x7
     7. LAPX LAPJVC    :  3064.3574 ms | ✅ | 🥴x2 🗿x4 🙅‍♂️x3
     8. LAPX LAPJV-IFT :  3987.7740 ms | ✅ | 🗿x4 🙅‍♂️x5
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these historical runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. `lapjvs` has the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
