[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# 🏆 Quick Benchmark

The [batch benchmark](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_batch.py)
and [single-matrix benchmark](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_single.py) compare application workflows on your machine.
These scripts are not intended for scientific research or competitive evaluation.
The results below record sample runs on selected platforms and architectures.

See [Cost values in the README](README.md#cost-values) for cost limits, total costs, and the difference between solver limits and filtering after solving.

## 💡 Run the quick benchmark

Run these commands:

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/benchmarks
python benchmark_batch.py
python benchmark_single.py
```

Both scripts use [SciPy](https://pypi.org/project/scipy/) for comparison.

<details><summary>Read the batch benchmark methods</summary><br>

### Batch cost calculation

`benchmark_batch.py` uses `return_cost=False` by default for all dense and sparse solvers, including loops over single problems.
Solver lines print only `time`. Add `--cost` to select `return_cost=True`.
In this mode, each line prints `cost` (the total across the batch) and `time`.
Each section title shows the selected `return_cost` value. Each case runs once in that mode.

The `scipy-loop` row calls `scipy.optimize.linear_sum_assignment` in sequence on the same matrices, including `np.inf` for missing edges.
SciPy returns only assignment indices. With `--cost`, the loop also sums selected costs with NumPy inside the timed region.
It uses the same initial untimed calls and independent result checks as the lapx rows.

`--threads` controls the lapx batch solvers. The loop baselines remain sequential.

```bash
python benchmark_batch.py --quick --threads 2
python benchmark_batch.py --quick --threads 2 --cost
```

### Sparse batch comparisons

The sparse section compares `lapmod_batch` with dense batch solvers on square problems.
All solvers receive the same costs and allowed assignments.
Dense arrays use `np.inf` for missing edges. `lapmod` receives finite entries as `(n, cc, ii, kk)` tuples.

The generator adds a finite diagonal to guarantee a full assignment.
The output reports the actual density after this step.
The dense section contains the rectangular cases because `lapmod` requires square inputs.

By default, the sparse section runs two batches:

- **100 matrices of size 1000x1000**, at a requested density of **1%**.
- **50 matrices of size 2000x2000**, at a requested density of **5%**.

`--quick` replaces these cases with one batch of **4 matrices of size 32x32**, at a requested density of **10%**.
This mode also uses smaller dense batches.

The script measures conversion from dense arrays to compressed sparse row (CSR) format separately.
The preparation line reports only this conversion time.
Solver times start with prepared inputs and include input checks and the solve.
With `--cost`, solver times also include the total-cost calculation.
They exclude conversion, initial untimed calls, and independent result checks.

The sparse section compares these methods:

- A loop over `lapmod` calls.
- `lapmod_batch` with one worker.
- `lapmod_batch` with the requested thread count.

With `--threads 1`, the script prints the batch result only once. Cases use fixed random seeds.

In both modes, the benchmark checks assignments after the timed call.
It calculates costs from the original matrices and compares them with `lapjvx_batch`, using floating-point tolerances.
With `--cost`, it also compares the returned totals with these independently calculated costs.
Successful checks produce no output. A mismatch raises an error.
These checks also apply to dense cases and never contribute to `time`.

From `benchmarks/`, use these commands for a small check or only the sparse cases:

```bash
python benchmark_batch.py --quick --threads 2
python benchmark_batch.py --sparse-only --threads 8
python benchmark_batch.py --sparse-only --threads 8 --cost
```

To use a local build, run this command from the repository root:

```bash
python -m benchmarks.benchmark_batch --quick --threads 2
```

The sparse section requires a build that provides `lapmod_batch`.
If the installed package lacks this function, the script prints a skip message.
It still runs the selected dense cases. The default dense cases use large matrices.
Use `--quick` for a small run.

The batch workflow runs the script without arguments.
It uses the default cases, the CPU count for threads, and `return_cost=False`.
The workflow installs lapx from PyPI. That package must provide `lapmod_batch` to run the sparse section.

</details>

### Benchmark results

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.

```
lapx==0.10.0rc1 (2026/09/07)
scipy==1.17.1
numpy==2.4.6
```

<details><summary>📄 Single:</summary><br>

```
Microsoft Windows [Version 10.0.26200.9168]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new3\lapx\benchmarks>python benchmark_single.py
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.52 x slower
 * lapjv : ✅ Passed 🐌 2.61 x slower
 * lapjvx : ✅ Passed 🐌 2.86 x slower
 * lapjvxa : ✅ Passed 🐌 1.52 x slower
 * lapjvs : ✅ Passed 🐌 3.05 x slower
 * lapjvsa : ✅ Passed 🐌 4.95 x slower

 ----- 🎉 SPEED RANKING 🎉 -----
   1. scipy ⭐  : 0.00000440s
   2. lapjvc    : 0.00000670s
   3. lapjvxa   : 0.00000670s
   4. lapjv     : 0.00001150s
   5. lapjvx    : 0.00001260s
   6. lapjvs    : 0.00001340s
   7. lapjvsa   : 0.00002180s
 -------------------------------

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.88 x slower
 * lapjv : ✅ Passed 🐌 2.35 x slower
 * lapjvx : ✅ Passed 🐌 1.91 x slower
 * lapjvxa : ✅ Passed 🐌 1.09 x slower
 * lapjvs : ✅ Passed 🐌 2.09 x slower
 * lapjvsa : ✅ Passed 🏆 1.42 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvsa   : 0.00000240s
   2. scipy ⭐  : 0.00000340s
   3. lapjvxa   : 0.00000370s
   4. lapjvx    : 0.00000650s
   5. lapjvs    : 0.00000710s
   6. lapjv     : 0.00000800s
   7. lapjvc    : 0.00000980s
 -------------------------------

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.13 x slower
 * lapjv : ✅ Passed 🐌 4.39 x slower
 * lapjvx : ✅ Passed 🐌 2.39 x slower
 * lapjvxa : ✅ Passed 🐌 1.77 x slower
 * lapjvs : ✅ Passed 🐌 20.97 x slower
 * lapjvsa : ✅ Passed 🐌 3.29 x slower

 ----- 🎉 SPEED RANKING 🎉 -----
   1. scipy ⭐  : 0.00000310s
   2. lapjvxa   : 0.00000550s
   3. lapjvc    : 0.00000660s
   4. lapjvx    : 0.00000740s
   5. lapjvsa   : 0.00001020s
   6. lapjv     : 0.00001360s
   7. lapjvs    : 0.00006500s
 -------------------------------

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.54 x slower
 * lapjv : ✅ Passed 🏆 1.33 x faster
 * lapjvx : ✅ Passed 🏆 1.51 x faster
 * lapjvxa : ✅ Passed 🏆 2.02 x faster
 * lapjvs : ✅ Passed 🏆 1.1 x faster
 * lapjvsa : ✅ Passed 🏆 1.2 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00001380s
   2. lapjvx    : 0.00001850s
   3. lapjv     : 0.00002090s
   4. lapjvsa   : 0.00002320s
   5. lapjvs    : 0.00002540s
   6. scipy ⭐  : 0.00002790s
   7. lapjvc    : 0.00004290s
 -------------------------------

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.07 x faster
 * lapjv : ✅ Passed 🏆 2.39 x faster
 * lapjvx : ✅ Passed 🏆 2.82 x faster
 * lapjvxa : ✅ Passed 🏆 3.58 x faster
 * lapjvs : ✅ Passed 🏆 2.34 x faster
 * lapjvsa : ✅ Passed 🏆 3.98 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvsa   : 0.00001070s
   2. lapjvxa   : 0.00001190s
   3. lapjvx    : 0.00001510s
   4. lapjv     : 0.00001780s
   5. lapjvs    : 0.00001820s
   6. lapjvc    : 0.00003980s
   7. scipy ⭐  : 0.00004260s
 -------------------------------

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.1 x slower
 * lapjv : ✅ Passed 🏆 1.31 x faster
 * lapjvx : ✅ Passed 🏆 1.53 x faster
 * lapjvxa : ✅ Passed 🏆 1.92 x faster
 * lapjvs : ✅ Passed 🏆 1.29 x faster
 * lapjvsa : ✅ Passed 🏆 1.21 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00001620s
   2. lapjvx    : 0.00002030s
   3. lapjv     : 0.00002370s
   4. lapjvs    : 0.00002410s
   5. lapjvsa   : 0.00002580s
   6. scipy ⭐  : 0.00003110s
   7. lapjvc    : 0.00006530s
 -------------------------------

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.22 x slower
 * lapjv : ✅ Passed 🏆 2.99 x faster
 * lapjvx : ✅ Passed 🏆 3.54 x faster
 * lapjvxa : ✅ Passed 🏆 3.61 x faster
 * lapjvs : ✅ Passed 🏆 4.29 x faster
 * lapjvsa : ✅ Passed 🏆 3.69 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvs    : 0.00061200s
   2. lapjvsa   : 0.00071050s
   3. lapjvxa   : 0.00072650s
   4. lapjvx    : 0.00074180s
   5. lapjv     : 0.00087590s
   6. scipy ⭐  : 0.00262250s
   7. lapjvc    : 0.01107370s
 -------------------------------

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.17 x slower
 * lapjv : ✅ Passed 🏆 2.15 x faster
 * lapjvx : ✅ Passed 🏆 2.14 x faster
 * lapjvxa : ✅ Passed 🏆 2.25 x faster
 * lapjvs : ✅ Passed 🏆 2.11 x faster
 * lapjvsa : ✅ Passed 🏆 2.2 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00208140s
   2. lapjvsa   : 0.00212820s
   3. lapjv     : 0.00217760s
   4. lapjvx    : 0.00218240s
   5. lapjvs    : 0.00221490s
   6. scipy ⭐  : 0.00467920s
   7. lapjvc    : 0.00549220s
 -------------------------------

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.07 x slower
 * lapjv : ✅ Passed 🏆 3.11 x faster
 * lapjvx : ✅ Passed 🏆 3.38 x faster
 * lapjvxa : ✅ Passed 🏆 3.44 x faster
 * lapjvs : ✅ Passed 🏆 4.07 x faster
 * lapjvsa : ✅ Passed 🏆 4.16 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvsa   : 0.00078740s
   2. lapjvs    : 0.00080500s
   3. lapjvxa   : 0.00095240s
   4. lapjvx    : 0.00097040s
   5. lapjv     : 0.00105500s
   6. scipy ⭐  : 0.00327790s
   7. lapjvc    : 0.01335420s
 -------------------------------

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 231.63 x slower
 * lapjv : ✅ Passed 🐌 1.53 x slower
 * lapjvx : ✅ Passed 🐌 1.5 x slower
 * lapjvxa : ✅ Passed 🐌 1.54 x slower
 * lapjvs : ✅ Passed 🏆 1.01 x faster
 * lapjvsa : ✅ Passed 🐌 1.06 x slower

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvs    : 0.05518570s
   2. scipy ⭐  : 0.05548150s
   3. lapjvsa   : 0.05884320s
   4. lapjvx    : 0.08336290s
   5. lapjv     : 0.08492760s
   6. lapjvxa   : 0.08533950s
   7. lapjvc    : 12.85111410s
 -------------------------------

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.12 x slower
 * lapjv : ✅ Passed 🏆 1.42 x faster
 * lapjvx : ✅ Passed 🏆 1.39 x faster
 * lapjvxa : ✅ Passed 🏆 1.27 x faster
 * lapjvs : ✅ Passed 🏆 2.1 x faster
 * lapjvsa : ✅ Passed 🏆 2.11 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvsa   : 0.52549630s
   2. lapjvs    : 0.52774620s
   3. lapjv     : 0.78183430s
   4. lapjvx    : 0.79479410s
   5. lapjvxa   : 0.87470650s
   6. scipy ⭐  : 1.10752510s
   7. lapjvc    : 1.24388590s
 -------------------------------

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 241.59 x slower
 * lapjv : ✅ Passed 🏆 1.35 x faster
 * lapjvx : ✅ Passed 🏆 1.28 x faster
 * lapjvxa : ✅ Passed 🏆 1.34 x faster
 * lapjvs : ✅ Passed 🏆 1.83 x faster
 * lapjvsa : ✅ Passed 🏆 1.96 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvsa   : 0.11139560s
   2. lapjvs    : 0.11915310s
   3. lapjv     : 0.16122710s
   4. lapjvxa   : 0.16275500s
   5. lapjvx    : 0.17050540s
   6. scipy ⭐  : 0.21814760s
   7. lapjvc    : 52.70290610s
 -------------------------------
```

</details>

<details><summary>🗂️ Batch:</summary><br>

```
Microsoft Windows [Version 10.0.26200.9168]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new3\lapx\benchmarks>python benchmark_batch.py

# Dense 10 x (4000x4000) | n_threads = 24 | return_cost = False

  CPU lapx-batch-jvx        :  time=1.26371860s
  CPU lapx-batch-jvs        :  time=0.46452740s
  CPU lapx-batch-jvxa       :  time=1.30170600s
  CPU lapx-batch-jvsa       :  time=0.43165550s
  CPU lapx-batch-jvsa64     :  time=1.26892690s
  CPU lapx-loop-jvx         :  time=6.11976390s
  CPU lapx-loop-jvs         :  time=2.64915310s
  CPU scipy-loop            :  time=7.17354660s

# Dense 20 x (3000x2000) | n_threads = 24 | return_cost = False

  CPU lapx-batch-jvx        :  time=0.12149920s
  CPU lapx-batch-jvs        :  time=0.08574870s
  CPU lapx-batch-jvxa       :  time=0.11881300s
  CPU lapx-batch-jvsa       :  time=0.09538000s
  CPU lapx-batch-jvsa64     :  time=0.14972810s
  CPU lapx-loop-jvx         :  time=0.79143780s
  CPU lapx-loop-jvs         :  time=0.61057540s
  CPU scipy-loop            :  time=0.95921520s

# Dense 50 x (2000x2000) | n_threads = 24 | return_cost = False

  CPU lapx-batch-jvx        :  time=0.46470050s
  CPU lapx-batch-jvs        :  time=0.29533320s
  CPU lapx-batch-jvxa       :  time=0.47589490s
  CPU lapx-batch-jvsa       :  time=0.28527810s
  CPU lapx-batch-jvsa64     :  time=0.47854580s
  CPU lapx-loop-jvx         :  time=4.03728170s
  CPU lapx-loop-jvs         :  time=3.01349750s
  CPU scipy-loop            :  time=5.90575280s

# Dense 100 x (1000x2000) | n_threads = 24 | return_cost = False

  CPU lapx-batch-jvx        :  time=0.18961440s
  CPU lapx-batch-jvs        :  time=0.11674890s
  CPU lapx-batch-jvxa       :  time=0.23145900s
  CPU lapx-batch-jvsa       :  time=0.12588530s
  CPU lapx-batch-jvsa64     :  time=0.21117900s
  CPU lapx-loop-jvx         :  time=1.18952180s
  CPU lapx-loop-jvs         :  time=0.80156130s
  CPU scipy-loop            :  time=0.87303590s

# Dense 500 x (1000x1000) | n_threads = 24 | return_cost = False

  CPU lapx-batch-jvx        :  time=0.63356070s
  CPU lapx-batch-jvs        :  time=0.55916580s
  CPU lapx-batch-jvxa       :  time=0.62701490s
  CPU lapx-batch-jvsa       :  time=0.55466290s
  CPU lapx-batch-jvsa64     :  time=0.62845360s
  CPU lapx-loop-jvx         :  time=7.11993820s
  CPU lapx-loop-jvs         :  time=6.74855210s
  CPU scipy-loop            :  time=11.35094930s

# Sparse 100 x (1000x1000) | density = 1.10% | n_threads = 24 | return_cost = False

  Same problems: dense solvers use inf for missing edges; lapmod uses CSR.
  Dense-to-CSR preparation  :  0.22184090s (excluded from solve times)

  CPU lapx-batch-jvx        :  time=0.12684750s
  CPU lapx-batch-jvs        :  time=0.11200840s
  CPU lapx-batch-jvxa       :  time=0.12108070s
  CPU lapx-batch-jvsa       :  time=0.11145000s
  CPU lapx-batch-jvsa64     :  time=0.11971870s
  CPU lapx-loop-jvx         :  time=1.24242260s
  CPU lapx-loop-jvs         :  time=1.19506530s
  CPU scipy-loop            :  time=1.68470530s
  CPU lapx-loop-mod         :  time=0.09815280s
  CPU lapx-batch-mod-1t     :  time=0.09657110s
  CPU lapx-batch-mod        :  time=0.01828630s

# Sparse 50 x (2000x2000) | density = 5.05% | n_threads = 24 | return_cost = False

  Same problems: dense solvers use inf for missing edges; lapmod uses CSR.
  Dense-to-CSR preparation  :  0.63996470s (excluded from solve times)

  CPU lapx-batch-jvx        :  time=0.41099270s
  CPU lapx-batch-jvs        :  time=0.30337600s
  CPU lapx-batch-jvxa       :  time=0.42309730s
  CPU lapx-batch-jvsa       :  time=0.28861380s
  CPU lapx-batch-jvsa64     :  time=0.41789420s
  CPU lapx-loop-jvx         :  time=3.44474170s
  CPU lapx-loop-jvs         :  time=2.83047850s
  CPU scipy-loop            :  time=5.11176970s
  CPU lapx-loop-mod         :  time=0.50238070s
  CPU lapx-batch-mod-1t     :  time=0.50107200s
  CPU lapx-batch-mod        :  time=0.05089830s
```

</details>

See the [single-matrix workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
and [batch workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml) for newer results across platforms.

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

The [tracking benchmark](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) compares object tracking workflows with [SciPy](https://pypi.org/project/scipy/) as the baseline.
Times include the solve, conversion to assignment pairs, and calculation of unmatched indices.
All lapx calls use `return_cost=False`.

The table labels identify two threshold methods:

- **LAPX LAPJV-IFT** passes `cost_limit=thresh` to `lapjv`.
- **The other rows**, including SciPy, remove pairs above `thresh` after solving. Their times include this filtering step.

See [Cost values in the README](README.md#cost-values) for the behavior and performance implications of these methods.
The `✓` and `✗` symbols show whether matched pairs and unmatched indices equal the SciPy baseline.
A difference between threshold methods does not by itself indicate a solver error.

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/benchmarks
python benchmark_tracking.py
```

<details><summary>📊 Show the results:</summary><br>

Sample run: Windows 11, i9-13900KS (8 P-cores + 8 E-cores), Python 3.11.

```
lapx==0.10.0rc1 (2026/09/07)
scipy==1.17.1
numpy==2.4.6
```

```
Microsoft Windows [Version 10.0.26200.9168]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\projects\lapx_all\new3\lapx\benchmarks>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000149s 6th  | 0.000045s ✓ 2nd | 0.000051s ✓ 4th | 0.000048s ✓ 3rd | 0.000136s ✓ 5th | 0.000044s ✓ 1st
25x20     | 0.000050s 3rd  | 0.000049s ✗ 2nd | 0.000050s ✓ 4th | 0.000047s ✓ 1st | 0.000054s ✓ 5th | 0.000059s ✓ 6th
50x50     | 0.000089s 6th  | 0.000073s ✗ 4th | 0.000055s ✓ 2nd | 0.000054s ✓ 1st | 0.000083s ✓ 5th | 0.000056s ✓ 3rd
100x150   | 0.000155s 3rd  | 0.000545s ✓ 5th | 0.000250s ✓ 4th | 0.000104s ✓ 1st | 0.000717s ✓ 6th | 0.000107s ✓ 2nd
250x250   | 0.001148s 4th  | 0.001483s ✓ 6th | 0.000594s ✓ 1st | 0.000595s ✓ 2nd | 0.001328s ✓ 5th | 0.000605s ✓ 3rd
550x500   | 0.003695s 4th  | 0.011657s ✓ 5th | 0.001240s ✓ 2nd | 0.001253s ✓ 3rd | 0.016362s ✓ 6th | 0.001038s ✓ 1st
1000x1000 | 0.021064s 4th  | 0.036917s ✓ 6th | 0.012872s ✓ 1st | 0.012967s ✓ 2nd | 0.022644s ✓ 5th | 0.013104s ✓ 3rd
2000x2500 | 0.039832s 4th  | 2.167027s ✓ 6th | 0.017522s ✓ 2nd | 0.017572s ✓ 3rd | 1.688402s ✓ 5th | 0.012390s ✓ 1st
5000x5000 | 1.233839s 4th  | 1.578792s ✓ 6th | 0.570229s ✓ 2nd | 0.587457s ✓ 3rd | 1.388625s ✓ 5th | 0.391425s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   418.8285 ms | ✅ | 🥇x4 🥈x1 🥉x3 🥴x1
     2. LAPX LAPJV     :   602.8636 ms | ✅ | 🥇x2 🥈x4 🚩x3
     3. LAPX LAPJVX    :   620.0980 ms | ✅ | 🥇x3 🥈x2 🥉x4
     4. BASELINE SciPy :  1300.0202 ms | ⭐ | 🥉x2 🚩x5 🥴x2
     5. LAPX LAPJVC    :  3118.3517 ms | ✅ | 🏳️x7 🥴x2
     6. LAPX LAPJV-IFT :  3796.5867 ms | ⚠️ | 🥈x2 🚩x1 🏳️x2 🥴x4
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000042s 6th  | 0.000041s ✗ 4th | 0.000038s ✓ 3rd | 0.000037s ✓ 2nd | 0.000041s ✓ 5th | 0.000036s ✓ 1st
25x20     | 0.000043s 1st  | 0.000052s ✗ 6th | 0.000046s ✓ 3rd | 0.000045s ✓ 2nd | 0.000050s ✓ 5th | 0.000048s ✓ 4th
50x50     | 0.000078s 5th  | 0.000077s ✗ 4th | 0.000057s ✓ 3rd | 0.000055s ✓ 1st | 0.000101s ✓ 6th | 0.000056s ✓ 2nd
100x150   | 0.000127s 4th  | 0.000638s ✓ 5th | 0.000113s ✓ 3rd | 0.000101s ✓ 1st | 0.000847s ✓ 6th | 0.000108s ✓ 2nd
250x250   | 0.001124s 5th  | 0.001502s ✓ 6th | 0.000602s ✓ 1st | 0.000620s ✓ 3rd | 0.001067s ✓ 4th | 0.000612s ✓ 2nd
550x500   | 0.003582s 4th  | 0.010808s ✓ 5th | 0.001108s ✓ 3rd | 0.001091s ✓ 2nd | 0.015098s ✓ 6th | 0.000919s ✓ 1st
1000x1000 | 0.022953s 4th  | 0.032272s ✓ 6th | 0.009968s ✓ 1st | 0.010186s ✓ 2nd | 0.027038s ✓ 5th | 0.010257s ✓ 3rd
2000x2500 | 0.037348s 4th  | 1.999662s ✓ 6th | 0.015911s ✓ 2nd | 0.017521s ✓ 3rd | 1.696982s ✓ 5th | 0.012160s ✓ 1st
5000x5000 | 1.137676s 4th  | 1.758436s ✓ 6th | 0.676492s ✓ 3rd | 0.658470s ✓ 2nd | 1.339713s ✓ 5th | 0.374923s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   399.1186 ms | ✅ | 🥇x4 🥈x3 🥉x1 🚩x1
     2. LAPX LAPJVX    :   688.1245 ms | ✅ | 🥇x2 🥈x5 🥉x2
     3. LAPX LAPJV     :   704.3352 ms | ✅ | 🥇x2 🥈x1 🥉x6
     4. BASELINE SciPy :  1202.9745 ms | ⭐ | 🥇x1 🚩x5 🏳️x2 🥴x1
     5. LAPX LAPJVC    :  3080.9372 ms | ✅ | 🚩x1 🏳️x5 🥴x3
     6. LAPX LAPJV-IFT :  3803.4871 ms | ⚠️ | 🚩x2 🏳️x2 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000040s 5th  | 0.000038s ✓ 4th | 0.000037s ✓ 3rd | 0.000037s ✓ 1st | 0.000041s ✓ 6th | 0.000037s ✓ 2nd
25x20     | 0.000042s 1st  | 0.000060s ✓ 5th | 0.000065s ✓ 6th | 0.000047s ✓ 2nd | 0.000047s ✓ 3rd | 0.000049s ✓ 4th
50x50     | 0.000066s 4th  | 0.000067s ✓ 5th | 0.000049s ✓ 3rd | 0.000048s ✓ 1st | 0.000160s ✓ 6th | 0.000048s ✓ 2nd
100x150   | 0.000127s 3rd  | 0.000638s ✓ 5th | 0.000134s ✓ 4th | 0.000098s ✓ 1st | 0.000647s ✓ 6th | 0.000106s ✓ 2nd
250x250   | 0.001157s 4th  | 0.001275s ✓ 5th | 0.000647s ✓ 3rd | 0.000463s ✓ 1st | 0.001422s ✓ 6th | 0.000498s ✓ 2nd
550x500   | 0.003513s 4th  | 0.010663s ✓ 5th | 0.000988s ✓ 3rd | 0.000982s ✓ 2nd | 0.015724s ✓ 6th | 0.000826s ✓ 1st
1000x1000 | 0.021679s 1st  | 0.050155s ✓ 6th | 0.022014s ✓ 2nd | 0.025452s ✓ 5th | 0.024939s ✓ 4th | 0.022107s ✓ 3rd
2000x2500 | 0.035311s 4th  | 2.083071s ✓ 6th | 0.017339s ✓ 3rd | 0.017196s ✓ 2nd | 1.758709s ✓ 5th | 0.011940s ✓ 1st
5000x5000 | 1.176536s 4th  | 1.766618s ✓ 6th | 0.675123s ✓ 3rd | 0.662769s ✓ 2nd | 1.565922s ✓ 5th | 0.355046s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   390.6557 ms | ✅ | 🥇x3 🥈x4 🥉x1 🚩x1
     2. LAPX LAPJVX    :   707.0914 ms | ✅ | 🥇x4 🥈x4 🏳️x1
     3. LAPX LAPJV     :   716.3958 ms | ✅ | 🥈x1 🥉x6 🚩x1 🥴x1
     4. BASELINE SciPy :  1238.4709 ms | ⭐ | 🥇x2 🥉x1 🚩x5 🏳️x1
     5. LAPX LAPJVC    :  3367.6107 ms | ✅ | 🥉x1 🚩x1 🏳️x2 🥴x5
     6. LAPX LAPJV-IFT :  3912.5858 ms | ✅ | 🚩x1 🏳️x5 🥴x3
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000049s 6th  | 0.000036s ✓ 1st | 0.000037s ✓ 2nd | 0.000039s ✓ 4th | 0.000038s ✓ 3rd | 0.000041s ✓ 5th
25x20     | 0.000043s 1st  | 0.000053s ✓ 5th | 0.000045s ✓ 2nd | 0.000045s ✓ 3rd | 0.000053s ✓ 6th | 0.000052s ✓ 4th
50x50     | 0.000073s 4th  | 0.000073s ✓ 5th | 0.000056s ✓ 2nd | 0.000053s ✓ 1st | 0.000085s ✓ 6th | 0.000058s ✓ 3rd
100x150   | 0.000123s 3rd  | 0.000683s ✓ 6th | 0.000127s ✓ 4th | 0.000101s ✓ 1st | 0.000577s ✓ 5th | 0.000107s ✓ 2nd
250x250   | 0.001073s 4th  | 0.001678s ✓ 6th | 0.000718s ✓ 1st | 0.000754s ✓ 2nd | 0.001195s ✓ 5th | 0.000766s ✓ 3rd
550x500   | 0.003354s 4th  | 0.010708s ✓ 5th | 0.001011s ✓ 3rd | 0.001004s ✓ 2nd | 0.015042s ✓ 6th | 0.000825s ✓ 1st
1000x1000 | 0.022851s 4th  | 0.040433s ✓ 6th | 0.015482s ✓ 3rd | 0.015451s ✓ 2nd | 0.026653s ✓ 5th | 0.015239s ✓ 1st
2000x2500 | 0.033847s 4th  | 2.017503s ✓ 6th | 0.015699s ✓ 3rd | 0.015648s ✓ 2nd | 1.654979s ✓ 5th | 0.010818s ✓ 1st
5000x5000 | 1.042984s 4th  | 2.271059s ✓ 6th | 0.944712s ✓ 3rd | 0.928014s ✓ 2nd | 1.185254s ✓ 5th | 0.370548s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   398.4528 ms | ✅ | 🥇x4 🥈x1 🥉x2 🚩x1 🏳️x1
     2. LAPX LAPJVX    :   961.1091 ms | ✅ | 🥇x2 🥈x5 🥉x1 🚩x1
     3. LAPX LAPJV     :   977.8875 ms | ✅ | 🥇x1 🥈x3 🥉x4 🚩x1
     4. BASELINE SciPy :  1104.3976 ms | ⭐ | 🥇x1 🥉x1 🚩x6 🥴x1
     5. LAPX LAPJVC    :  2883.8761 ms | ✅ | 🥉x1 🏳️x5 🥴x3
     6. LAPX LAPJV-IFT :  4342.2269 ms | ✅ | 🥇x1 🏳️x3 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000051s 6th  | 0.000038s ✓ 3rd | 0.000037s ✓ 1st | 0.000038s ✓ 4th | 0.000039s ✓ 5th | 0.000037s ✓ 2nd
25x20     | 0.000046s 2nd  | 0.000054s ✓ 5th | 0.000049s ✓ 3rd | 0.000046s ✓ 1st | 0.000052s ✓ 4th | 0.000075s ✓ 6th
50x50     | 0.000068s 4th  | 0.000069s ✓ 5th | 0.000052s ✓ 2nd | 0.000051s ✓ 1st | 0.000079s ✓ 6th | 0.000054s ✓ 3rd
100x150   | 0.000128s 3rd  | 0.000648s ✓ 6th | 0.000130s ✓ 4th | 0.000100s ✓ 1st | 0.000598s ✓ 5th | 0.000101s ✓ 2nd
250x250   | 0.001073s 4th  | 0.001209s ✓ 6th | 0.000420s ✓ 3rd | 0.000415s ✓ 1st | 0.001096s ✓ 5th | 0.000419s ✓ 2nd
550x500   | 0.003212s 4th  | 0.011381s ✓ 5th | 0.001016s ✓ 2nd | 0.001037s ✓ 3rd | 0.013218s ✓ 6th | 0.000838s ✓ 1st
1000x1000 | 0.024444s 4th  | 0.044673s ✓ 6th | 0.015256s ✓ 1st | 0.015515s ✓ 2nd | 0.028290s ✓ 5th | 0.022879s ✓ 3rd
2000x2500 | 0.037608s 4th  | 2.186560s ✓ 6th | 0.017448s ✓ 2nd | 0.017506s ✓ 3rd | 1.651947s ✓ 5th | 0.012600s ✓ 1st
5000x5000 | 1.167876s 4th  | 1.429866s ✓ 5th | 0.548546s ✓ 3rd | 0.543160s ✓ 2nd | 1.473259s ✓ 6th | 0.358496s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   395.4994 ms | ✅ | 🥇x3 🥈x3 🥉x2 🥴x1
     2. LAPX LAPJVX    :   577.8684 ms | ✅ | 🥇x4 🥈x2 🥉x2 🚩x1
     3. LAPX LAPJV     :   582.9527 ms | ✅ | 🥇x2 🥈x3 🥉x3 🚩x1
     4. BASELINE SciPy :  1234.5065 ms | ⭐ | 🥈x1 🥉x1 🚩x6 🥴x1
     5. LAPX LAPJVC    :  3168.5778 ms | ✅ | 🚩x1 🏳️x5 🥴x3
     6. LAPX LAPJV-IFT :  3674.4995 ms | ✅ | 🥉x1 🏳️x4 🥴x4
 🎉 ------------------------------------------------------------------------- 🎉
```

</details>

In these recorded runs, `lapjv` and `lapjvx` match the SciPy baseline outputs.
Both are faster than SciPy in most cases. `lapjvs` has the lowest total time in each tracking summary.
`LAPX LAPJV-IFT` has a higher total time and produces different assignments in some cases.

Use the [tracking script](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) to compare the methods on your inputs.
See the [tracking workflow](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml) for results from other platforms and architectures.
