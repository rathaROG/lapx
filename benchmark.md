[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg?v=0.8.1)](https://badge.fury.io/py/lapx)
[![Benchmark](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# 🏆 Quick Benchmark

`lapx` focuses more on real-world applications, and the [benchmark_batch.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_batch.py) 
and [benchmark.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark.py) are **not** 
intended for scientific research or competitive evaluation. Instead, it provides a quick and accessible way for 
you to run benchmark tests on your own machine. Below, you will also find a collection of interesting results 
gathered from various major platforms and architectures.

## 💡 Run the quick benchmark

To see some quick benchmark results for these functions, simply run:

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/.github/test
python benchmark_batch.py
python benchmark.py
```

Note: [SciPy](https://pypi.org/project/scipy/) is used as the baseline in the benchmark.

📊 Some benchmark results using `lapx` [v0.8.0](https://github.com/rathaROG/lapx/releases/tag/v0.8.0) (2025/10/27):

<details><summary>🗂️ Batch on my Windows 11 i9-13900KS (8 p-core + 8 e-core) + python 3.9.13:</summary>

```
# 50 x (3000x3000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=82.08230873, time=1.40321970s
  CPU lapx-batch-jvs     :  cost=82.08230873, time=0.80294538s
  CPU lapx-batch-jvxa    :  cost=82.08230873, time=1.40610409s
  CPU lapx-batch-jvsa    :  cost=82.08230873, time=0.81906796s
  CPU lapx-batch-jvsa64  :  cost=82.08230873, time=1.42109323s
  CPU lapx-loop-jvx      :  cost=82.08230873, time=11.01966000s
  CPU lapx-loop-jvs      :  cost=82.08230873, time=8.18710470s

# 100 x (2000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=164.54469568, time=0.81932855s
  CPU lapx-batch-jvs     :  cost=164.54469568, time=0.58506370s
  CPU lapx-batch-jvxa    :  cost=164.54469568, time=0.83581567s
  CPU lapx-batch-jvsa    :  cost=164.54469568, time=0.59467125s
  CPU lapx-batch-jvsa64  :  cost=164.54469568, time=0.88178015s
  CPU lapx-loop-jvx      :  cost=164.54469568, time=7.68291450s
  CPU lapx-loop-jvs      :  cost=164.54469568, time=6.44884777s

# 500 x (1000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=291.25078928, time=0.91706204s
  CPU lapx-batch-jvs     :  cost=291.25078928, time=0.79455686s
  CPU lapx-batch-jvxa    :  cost=291.25078928, time=0.93096972s
  CPU lapx-batch-jvsa    :  cost=291.25078928, time=0.79109597s
  CPU lapx-batch-jvsa64  :  cost=291.25078928, time=1.23274732s
  CPU lapx-loop-jvx      :  cost=291.25078928, time=5.47222424s
  CPU lapx-loop-jvs      :  cost=291.25078928, time=5.73832059s

# 1000 x (1000x1000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=1641.72891905, time=1.18257976s
  CPU lapx-batch-jvs     :  cost=1641.72891905, time=1.13616300s
  CPU lapx-batch-jvxa    :  cost=1641.72891905, time=1.16668177s
  CPU lapx-batch-jvsa    :  cost=1641.72891905, time=1.11944461s
  CPU lapx-batch-jvsa64  :  cost=1641.72891905, time=1.23001194s
  CPU lapx-loop-jvx      :  cost=1641.72891905, time=13.90460992s
  CPU lapx-loop-jvs      :  cost=1641.72891905, time=14.32015085s
```

</details>

<details><summary>📄 Single-matrix on ubuntu-latest + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18851354956/job/53788494991

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.13 x slower 
 * lapjv : ✅ Passed 🐌 2.85 x slower 
 * lapjvx : ✅ Passed 🐌 1.17 x slower 
 * lapjvxa : ✅ Passed 🏆 1.6 x faster 
 * lapjvs : ✅ Passed 🐌 2.33 x slower 
 * lapjvsa : ✅ Passed 🐌 2.1 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00001882s
   2. scipy ⭐ 	: 0.00003012s
   3. lapjvx  	: 0.00003522s
   4. lapjvsa  	: 0.00006335s
   5. lapjvc  	: 0.00006415s
   6. lapjvs  	: 0.00007016s
   7. lapjv  	: 0.00008579s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.5 x slower 
 * lapjv : ✅ Passed 🐌 1.9 x slower 
 * lapjvx : ✅ Passed 🐌 1.3 x slower 
 * lapjvxa : ✅ Passed 🏆 1.15 x faster 
 * lapjvs : ✅ Passed 🐌 1.92 x slower 
 * lapjvsa : ✅ Passed 🏆 1.79 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00000646s
   2. lapjvxa  	: 0.00001002s
   3. scipy ⭐ 	: 0.00001154s
   4. lapjvx  	: 0.00001498s
   5. lapjvc  	: 0.00001732s
   6. lapjv  	: 0.00002196s
   7. lapjvs  	: 0.00002215s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.82 x slower 
 * lapjv : ✅ Passed 🐌 3.92 x slower 
 * lapjvx : ✅ Passed 🐌 2.34 x slower 
 * lapjvxa : ✅ Passed 🐌 1.69 x slower 
 * lapjvs : ✅ Passed 🐌 3.3 x slower 
 * lapjvsa : ✅ Passed 🐌 5.28 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000862s
   2. lapjvxa  	: 0.00001455s
   3. lapjvc  	: 0.00001566s
   4. lapjvx  	: 0.00002017s
   5. lapjvs  	: 0.00002845s
   6. lapjv  	: 0.00003373s
   7. lapjvsa  	: 0.00004552s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.87 x slower 
 * lapjv : ✅ Passed 🏆 1.19 x faster 
 * lapjvx : ✅ Passed 🏆 1.62 x faster 
 * lapjvxa : ✅ Passed 🏆 2.35 x faster 
 * lapjvs : ✅ Passed 🏆 1.33 x faster 
 * lapjvsa : ✅ Passed 🏆 1.32 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00003084s
   2. lapjvx  	: 0.00004490s
   3. lapjvs  	: 0.00005469s
   4. lapjvsa  	: 0.00005475s
   5. lapjv  	: 0.00006076s
   6. scipy ⭐ 	: 0.00007253s
   7. lapjvc  	: 0.00013553s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.19 x faster 
 * lapjv : ✅ Passed 🏆 2.1 x faster 
 * lapjvx : ✅ Passed 🏆 2.77 x faster 
 * lapjvxa : ✅ Passed 🏆 4.34 x faster 
 * lapjvs : ✅ Passed 🏆 2.3 x faster 
 * lapjvsa : ✅ Passed 🏆 5.58 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00001290s
   2. lapjvxa  	: 0.00001658s
   3. lapjvx  	: 0.00002601s
   4. lapjvs  	: 0.00003129s
   5. lapjv  	: 0.00003426s
   6. lapjvc  	: 0.00006070s
   7. scipy ⭐ 	: 0.00007195s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.59 x slower 
 * lapjv : ✅ Passed 🏆 1.14 x faster 
 * lapjvx : ✅ Passed 🏆 1.65 x faster 
 * lapjvxa : ✅ Passed 🏆 2.33 x faster 
 * lapjvs : ✅ Passed 🏆 1.58 x faster 
 * lapjvsa : ✅ Passed 🏆 1.37 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00003199s
   2. lapjvx  	: 0.00004507s
   3. lapjvs  	: 0.00004723s
   4. lapjvsa  	: 0.00005446s
   5. lapjv  	: 0.00006505s
   6. scipy ⭐ 	: 0.00007443s
   7. lapjvc  	: 0.00011813s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.19 x slower 
 * lapjv : ✅ Passed 🏆 2.46 x faster 
 * lapjvx : ✅ Passed 🏆 2.84 x faster 
 * lapjvxa : ✅ Passed 🏆 3.94 x faster 
 * lapjvs : ✅ Passed 🏆 4.37 x faster 
 * lapjvsa : ✅ Passed 🏆 4.45 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00108461s
   2. lapjvs  	: 0.00110318s
   3. lapjvxa  	: 0.00122390s
   4. lapjvx  	: 0.00169714s
   5. lapjv  	: 0.00195890s
   6. scipy ⭐ 	: 0.00482560s
   7. lapjvc  	: 0.02019986s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.01 x slower 
 * lapjv : ✅ Passed 🏆 2.0 x faster 
 * lapjvx : ✅ Passed 🏆 2.06 x faster 
 * lapjvxa : ✅ Passed 🏆 2.06 x faster 
 * lapjvs : ✅ Passed 🏆 2.05 x faster 
 * lapjvsa : ✅ Passed 🏆 2.06 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00498536s
   2. lapjvxa  	: 0.00499154s
   3. lapjvx  	: 0.00499524s
   4. lapjvs  	: 0.00501234s
   5. lapjv  	: 0.00512501s
   6. scipy ⭐ 	: 0.01026616s
   7. lapjvc  	: 0.01041151s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.17 x slower 
 * lapjv : ✅ Passed 🏆 3.74 x faster 
 * lapjvx : ✅ Passed 🏆 4.29 x faster 
 * lapjvxa : ✅ Passed 🏆 4.37 x faster 
 * lapjvs : ✅ Passed 🏆 4.33 x faster 
 * lapjvsa : ✅ Passed 🏆 4.38 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00136651s
   2. lapjvxa  	: 0.00136884s
   3. lapjvs  	: 0.00138280s
   4. lapjvx  	: 0.00139509s
   5. lapjv  	: 0.00160113s
   6. scipy ⭐ 	: 0.00598653s
   7. lapjvc  	: 0.02498232s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 222.34 x slower 
 * lapjv : ✅ Passed 🏆 1.15 x faster 
 * lapjvx : ✅ Passed 🏆 1.31 x faster 
 * lapjvxa : ✅ Passed 🏆 1.29 x faster 
 * lapjvs : ✅ Passed 🐌 1.11 x slower 
 * lapjvsa : ✅ Passed 🐌 1.11 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.07696005s
   2. lapjvxa  	: 0.07810211s
   3. lapjv  	: 0.08824028s
   4. scipy ⭐ 	: 0.10107496s
   5. lapjvsa  	: 0.11232857s
   6. lapjvs  	: 0.11252413s
   7. lapjvc  	: 22.47302152s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.17 x faster 
 * lapjv : ✅ Passed 🏆 1.3 x faster 
 * lapjvx : ✅ Passed 🏆 1.31 x faster 
 * lapjvxa : ✅ Passed 🏆 1.31 x faster 
 * lapjvs : ✅ Passed 🏆 2.06 x faster 
 * lapjvsa : ✅ Passed 🏆 2.06 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvs  	: 1.16571718s
   2. lapjvsa  	: 1.16708573s
   3. lapjvxa  	: 1.84065010s
   4. lapjvx  	: 1.84106529s
   5. lapjv  	: 1.84539000s
   6. lapjvc  	: 2.04553916s
   7. scipy ⭐ 	: 2.40261425s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 230.42 x slower 
 * lapjv : ✅ Passed 🏆 2.24 x faster 
 * lapjvx : ✅ Passed 🏆 2.54 x faster 
 * lapjvxa : ✅ Passed 🏆 2.5 x faster 
 * lapjvs : ✅ Passed 🏆 1.66 x faster 
 * lapjvsa : ✅ Passed 🏆 1.68 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.16310518s
   2. lapjvxa  	: 0.16545943s
   3. lapjv  	: 0.18474822s
   4. lapjvsa  	: 0.24673601s
   5. lapjvs  	: 0.24954140s
   6. scipy ⭐ 	: 0.41429755s
   7. lapjvc  	: 95.46102137s
 ------------------------------- 
```

</details>

<details><summary>📄 Single-matrix on macos-latest (arm) + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18851354956/job/53788495229

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.65 x slower 
 * lapjv : ✅ Passed 🐌 4.13 x slower 
 * lapjvx : ✅ Passed 🐌 1.26 x slower 
 * lapjvxa : ✅ Passed 🏆 3.06 x faster 
 * lapjvs : ✅ Passed 🐌 1.52 x slower 
 * lapjvsa : ✅ Passed 🐌 1.46 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00001037s
   2. scipy ⭐ 	: 0.00003179s
   3. lapjvx  	: 0.00003996s
   4. lapjvsa  	: 0.00004642s
   5. lapjvs  	: 0.00004833s
   6. lapjvc  	: 0.00005250s
   7. lapjv  	: 0.00013146s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.51 x slower 
 * lapjv : ✅ Passed 🐌 1.65 x slower 
 * lapjvx : ✅ Passed 🐌 1.09 x slower 
 * lapjvxa : ✅ Passed 🏆 1.27 x faster 
 * lapjvs : ✅ Passed 🐌 1.67 x slower 
 * lapjvsa : ✅ Passed 🏆 1.99 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00000308s
   2. lapjvxa  	: 0.00000483s
   3. scipy ⭐ 	: 0.00000613s
   4. lapjvx  	: 0.00000667s
   5. lapjvc  	: 0.00000925s
   6. lapjv  	: 0.00001013s
   7. lapjvs  	: 0.00001021s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.95 x slower 
 * lapjv : ✅ Passed 🐌 3.42 x slower 
 * lapjvx : ✅ Passed 🐌 2.1 x slower 
 * lapjvxa : ✅ Passed 🐌 1.68 x slower 
 * lapjvs : ✅ Passed 🐌 3.23 x slower 
 * lapjvsa : ✅ Passed 🐌 4.63 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000429s
   2. lapjvxa  	: 0.00000721s
   3. lapjvc  	: 0.00000837s
   4. lapjvx  	: 0.00000900s
   5. lapjvs  	: 0.00001387s
   6. lapjv  	: 0.00001467s
   7. lapjvsa  	: 0.00001988s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.49 x slower 
 * lapjv : ✅ Passed 🏆 1.7 x faster 
 * lapjvx : ✅ Passed 🏆 2.13 x faster 
 * lapjvxa : ✅ Passed 🏆 2.67 x faster 
 * lapjvs : ✅ Passed 🏆 1.8 x faster 
 * lapjvsa : ✅ Passed 🏆 1.89 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00002146s
   2. lapjvx  	: 0.00002683s
   3. lapjvsa  	: 0.00003033s
   4. lapjvs  	: 0.00003183s
   5. lapjv  	: 0.00003358s
   6. scipy ⭐ 	: 0.00005721s
   7. lapjvc  	: 0.00008517s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.41 x faster 
 * lapjv : ✅ Passed 🏆 3.95 x faster 
 * lapjvx : ✅ Passed 🏆 4.4 x faster 
 * lapjvxa : ✅ Passed 🏆 6.29 x faster 
 * lapjvs : ✅ Passed 🏆 3.59 x faster 
 * lapjvsa : ✅ Passed 🏆 6.65 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00001100s
   2. lapjvxa  	: 0.00001162s
   3. lapjvx  	: 0.00001662s
   4. lapjv  	: 0.00001850s
   5. lapjvs  	: 0.00002038s
   6. lapjvc  	: 0.00005183s
   7. scipy ⭐ 	: 0.00007312s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.17 x slower 
 * lapjv : ✅ Passed 🏆 1.56 x faster 
 * lapjvx : ✅ Passed 🏆 1.73 x faster 
 * lapjvxa : ✅ Passed 🏆 2.29 x faster 
 * lapjvs : ✅ Passed 🏆 1.46 x faster 
 * lapjvsa : ✅ Passed 🏆 1.4 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00001733s
   2. lapjvx  	: 0.00002292s
   3. lapjv  	: 0.00002546s
   4. lapjvs  	: 0.00002713s
   5. lapjvsa  	: 0.00002838s
   6. scipy ⭐ 	: 0.00003962s
   7. lapjvc  	: 0.00008579s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 5.08 x slower 
 * lapjv : ✅ Passed 🏆 1.44 x faster 
 * lapjvx : ✅ Passed 🏆 1.95 x faster 
 * lapjvxa : ✅ Passed 🏆 3.47 x faster 
 * lapjvs : ✅ Passed 🏆 2.22 x faster 
 * lapjvsa : ✅ Passed 🏆 2.18 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00098750s
   2. lapjvs  	: 0.00154171s
   3. lapjvsa  	: 0.00157042s
   4. lapjvx  	: 0.00175387s
   5. lapjv  	: 0.00237538s
   6. scipy ⭐ 	: 0.00342258s
   7. lapjvc  	: 0.01738238s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.23 x slower 
 * lapjv : ✅ Passed 🏆 3.51 x faster 
 * lapjvx : ✅ Passed 🏆 3.61 x faster 
 * lapjvxa : ✅ Passed 🏆 3.69 x faster 
 * lapjvs : ✅ Passed 🏆 3.29 x faster 
 * lapjvsa : ✅ Passed 🏆 3.42 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00192367s
   2. lapjvx  	: 0.00196654s
   3. lapjv  	: 0.00201971s
   4. lapjvsa  	: 0.00207583s
   5. lapjvs  	: 0.00215921s
   6. scipy ⭐ 	: 0.00709604s
   7. lapjvc  	: 0.00875521s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 5.09 x slower 
 * lapjv : ✅ Passed 🏆 3.0 x faster 
 * lapjvx : ✅ Passed 🏆 3.6 x faster 
 * lapjvxa : ✅ Passed 🏆 3.71 x faster 
 * lapjvs : ✅ Passed 🏆 2.83 x faster 
 * lapjvsa : ✅ Passed 🏆 2.74 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00110967s
   2. lapjvx  	: 0.00114104s
   3. lapjv  	: 0.00137046s
   4. lapjvs  	: 0.00145308s
   5. lapjvsa  	: 0.00150308s
   6. scipy ⭐ 	: 0.00411283s
   7. lapjvc  	: 0.02093913s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 199.7 x slower 
 * lapjv : ✅ Passed 🐌 1.48 x slower 
 * lapjvx : ✅ Passed 🏆 1.17 x faster 
 * lapjvxa : ✅ Passed 🏆 1.08 x faster 
 * lapjvs : ✅ Passed 🐌 1.75 x slower 
 * lapjvsa : ✅ Passed 🐌 1.58 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.09995704s
   2. lapjvxa  	: 0.10858558s
   3. scipy ⭐ 	: 0.11726183s
   4. lapjv  	: 0.17386667s
   5. lapjvsa  	: 0.18564625s
   6. lapjvs  	: 0.20479308s
   7. lapjvc  	: 23.41745225s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.01 x slower 
 * lapjv : ✅ Passed 🏆 1.21 x faster 
 * lapjvx : ✅ Passed 🏆 1.25 x faster 
 * lapjvxa : ✅ Passed 🏆 1.19 x faster 
 * lapjvs : ✅ Passed 🏆 1.73 x faster 
 * lapjvsa : ✅ Passed 🏆 1.84 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.92814183s
   2. lapjvs  	: 0.98585971s
   3. lapjvx  	: 1.36841413s
   4. lapjv  	: 1.41392200s
   5. lapjvxa  	: 1.43138329s
   6. scipy ⭐ 	: 1.70584088s
   7. lapjvc  	: 3.43550417s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 283.01 x slower 
 * lapjv : ✅ Passed 🐌 2.24 x slower 
 * lapjvx : ✅ Passed 🏆 1.39 x faster 
 * lapjvxa : ✅ Passed 🏆 2.27 x faster 
 * lapjvs : ✅ Passed 🐌 1.5 x slower 
 * lapjvsa : ✅ Passed 🐌 1.79 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.16666625s
   2. lapjvx  	: 0.27308525s
   3. scipy ⭐ 	: 0.37829733s
   4. lapjvs  	: 0.56853200s
   5. lapjvsa  	: 0.67584400s
   6. lapjv  	: 0.84921917s
   7. lapjvc  	: 107.06137171s
 ------------------------------- 
```

</details>

👁️ See newer benchmark results on all platforms [here on GitHub](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml).

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

This [benchmark_tracking.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_tracking.py) is specifically desinged for the Object Tracking applications, with [SciPy](https://pypi.org/project/scipy/) as the baseline.

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/.github/test
python benchmark_tracking.py
```

As shown in the updated benchmark results below, the new function [`lapjvx()`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) (LAPX LAPJVX in the tables) and the original [`lapjv()`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv) (LAPX LAPJV in the tables) consistently matches the baseline outputs of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html), as indicated by “✓” and ✅ in the tables.

In most scenarios, `lapjvx()` and `lapjv()` demonstrate faster performance than the baseline SciPy's `linear_sum_assignment`, and they remain competitive with other LAPX variants such as [`lapjvc`](https://github.com/rathaROG/lapx#4-the-new-function-lapjvc) (LAPX LAPJVC in the tables). When in-function filtering with `cost_limit` is used, `lapjv()` (LAPX LAPJV-IFT in the tables) experiences a significant performance impact and can produce different outputs compared to SciPy's baseline, as indicated by “✗” and ⚠️ in the tables.

🆕 `lapx` [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) introduced [`lapjvs()`](https://github.com/rathaROG/lapx#5-the-new-function-lapjvs), a highly competitive solver. Notably, `lapjvs()` outperforms other solvers in terms of speed when the input cost matrix is square, especially for sizes 5000 and above.

💡 To achieve optimal performance of `lapjvx()` or `lapjv()` in object tracking application, follow the implementation in the current [`benchmark_tracking.py`](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_tracking.py) script.

<details><summary>📊 Show the results:</summary>

https://github.com/rathaROG/lapx/actions/runs/18830580672/job/53721233510

```
#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000325s 6th  | 0.000137s ✗ 1st | 0.000168s ✓ 3rd | 0.000177s ✓ 4th | 0.000206s ✓ 5th | 0.000162s ✓ 2nd
25x20     | 0.000170s 5th  | 0.000191s ✗ 6th | 0.000155s ✓ 1st | 0.000170s ✓ 4th | 0.000162s ✓ 3rd | 0.000160s ✓ 2nd
50x50     | 0.000265s 6th  | 0.000214s ✗ 4th | 0.000190s ✓ 1st | 0.000193s ✓ 2nd | 0.000246s ✓ 5th | 0.000194s ✓ 3rd
100x150   | 0.000453s 4th  | 0.001335s ✓ 6th | 0.000402s ✓ 3rd | 0.000396s ✓ 2nd | 0.001067s ✓ 5th | 0.000330s ✓ 1st
250x250   | 0.002854s 5th  | 0.002952s ✓ 6th | 0.001731s ✓ 3rd | 0.001559s ✓ 2nd | 0.001977s ✓ 4th | 0.001536s ✓ 1st
550x500   | 0.008365s 1st  | 0.064973s ✓ 6th | 0.012927s ✓ 4th | 0.011949s ✓ 3rd | 0.030009s ✓ 5th | 0.011664s ✓ 2nd
1000x1000 | 0.051245s 2nd  | 0.111529s ✓ 6th | 0.057231s ✓ 5th | 0.055981s ✓ 4th | 0.044361s ✓ 1st | 0.055155s ✓ 3rd
2000x2500 | 0.075957s 4th  | 3.645535s ✓ 6th | 0.020558s ✓ 1st | 0.020706s ✓ 2nd | 2.975010s ✓ 5th | 0.034655s ✓ 3rd
5000x5000 | 2.114572s 5th  | 2.563577s ✓ 6th | 1.214149s ✓ 2nd | 1.219787s ✓ 3rd | 1.844269s ✓ 4th | 0.959447s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1063.3028 ms | ✅ | 🥇x3 🥈x3 🥉x3
     2. LAPX LAPJV     :  1307.5116 ms | ✅ | 🥇x3 🥈x1 🥉x3 🚩x1 🏳️x1
     3. LAPX LAPJVX    :  1310.9174 ms | ✅ | 🥈x4 🥉x2 🚩x3
     4. BASELINE SciPy :  2254.2068 ms | ⭐ | 🥇x1 🥈x1 🚩x2 🏳️x3 🥴x2
     5. LAPX LAPJVC    :  4897.3061 ms | ✅ | 🥇x1 🥉x1 🚩x2 🏳️x5
     6. LAPX LAPJV-IFT :  6390.4416 ms | ⚠️ | 🥇x1 🚩x1 🥴x7
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000188s 6th  | 0.000157s ✗ 5th | 0.000130s ✓ 3rd | 0.000129s ✓ 1st | 0.000139s ✓ 4th | 0.000129s ✓ 2nd
25x20     | 0.000152s 3rd  | 0.000171s ✗ 6th | 0.000148s ✓ 1st | 0.000149s ✓ 2nd | 0.000159s ✓ 4th | 0.000160s ✓ 5th
50x50     | 0.000245s 6th  | 0.000230s ✗ 4th | 0.000188s ✓ 1st | 0.000194s ✓ 2nd | 0.000231s ✓ 5th | 0.000197s ✓ 3rd
100x150   | 0.000417s 4th  | 0.001254s ✓ 6th | 0.000334s ✓ 2nd | 0.000333s ✓ 1st | 0.000887s ✓ 5th | 0.000349s ✓ 3rd
250x250   | 0.002642s 5th  | 0.003365s ✓ 6th | 0.001734s ✓ 2nd | 0.001751s ✓ 3rd | 0.002294s ✓ 4th | 0.001708s ✓ 1st
550x500   | 0.007055s 1st  | 0.127557s ✓ 6th | 0.011708s ✓ 4th | 0.011700s ✓ 3rd | 0.040566s ✓ 5th | 0.011671s ✓ 2nd
1000x1000 | 0.045616s 5th  | 0.085374s ✓ 6th | 0.041577s ✓ 3rd | 0.041732s ✓ 4th | 0.040828s ✓ 1st | 0.041053s ✓ 2nd
2000x2500 | 0.075874s 4th  | 3.594363s ✓ 6th | 0.020592s ✓ 2nd | 0.020426s ✓ 1st | 2.840181s ✓ 5th | 0.024470s ✓ 3rd
5000x5000 | 2.493812s 5th  | 3.415118s ✓ 6th | 1.651438s ✓ 3rd | 1.646662s ✓ 2nd | 2.010495s ✓ 4th | 0.994217s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1073.9525 ms | ✅ | 🥇x2 🥈x3 🥉x3 🏳️x1
     2. LAPX LAPJVX    :  1723.0752 ms | ✅ | 🥇x3 🥈x3 🥉x2 🚩x1
     3. LAPX LAPJV     :  1727.8499 ms | ✅ | 🥇x2 🥈x3 🥉x3 🚩x1
     4. BASELINE SciPy :  2626.0008 ms | ⭐ | 🥇x1 🥉x1 🚩x2 🏳️x3 🥴x2
     5. LAPX LAPJVC    :  4935.7815 ms | ✅ | 🥇x1 🚩x4 🏳️x4
     6. LAPX LAPJV-IFT :  7227.5912 ms | ⚠️ | 🚩x1 🏳️x1 🥴x7
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000218s 6th  | 0.000129s ✓ 1st | 0.000131s ✓ 3rd | 0.000154s ✓ 5th | 0.000139s ✓ 4th | 0.000131s ✓ 2nd
25x20     | 0.000150s 1st  | 0.000178s ✓ 6th | 0.000151s ✓ 2nd | 0.000158s ✓ 4th | 0.000163s ✓ 5th | 0.000155s ✓ 3rd
50x50     | 0.000211s 5th  | 0.000194s ✓ 3rd | 0.000283s ✓ 6th | 0.000180s ✓ 1st | 0.000194s ✓ 2nd | 0.000197s ✓ 4th
100x150   | 0.000404s 4th  | 0.001266s ✓ 6th | 0.000344s ✓ 3rd | 0.000318s ✓ 1st | 0.000955s ✓ 5th | 0.000341s ✓ 2nd
250x250   | 0.002778s 6th  | 0.002573s ✓ 5th | 0.001292s ✓ 2nd | 0.001324s ✓ 3rd | 0.001683s ✓ 4th | 0.001267s ✓ 1st
550x500   | 0.007734s 1st  | 0.238647s ✓ 6th | 0.012039s ✓ 4th | 0.011927s ✓ 3rd | 0.040219s ✓ 5th | 0.011922s ✓ 2nd
1000x1000 | 0.046291s 5th  | 0.075969s ✓ 6th | 0.036951s ✓ 2nd | 0.037461s ✓ 3rd | 0.039884s ✓ 4th | 0.020911s ✓ 1st
2000x2500 | 0.076470s 4th  | 3.556511s ✓ 6th | 0.020127s ✓ 1st | 0.020713s ✓ 2nd | 2.866433s ✓ 5th | 0.023518s ✓ 3rd
5000x5000 | 2.853023s 5th  | 2.870481s ✓ 6th | 1.372504s ✓ 3rd | 1.367633s ✓ 2nd | 1.949158s ✓ 4th | 1.205538s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1263.9814 ms | ✅ | 🥇x3 🥈x3 🥉x2 🚩x1
     2. LAPX LAPJVX    :  1439.8675 ms | ✅ | 🥇x2 🥈x2 🥉x3 🚩x1 🏳️x1
     3. LAPX LAPJV     :  1443.8227 ms | ✅ | 🥇x1 🥈x3 🥉x3 🚩x1 🥴x1
     4. BASELINE SciPy :  2987.2792 ms | ⭐ | 🥇x2 🚩x2 🏳️x3 🥴x2
     5. LAPX LAPJVC    :  4898.8268 ms | ✅ | 🥈x1 🚩x4 🏳️x4
     6. LAPX LAPJV-IFT :  6745.9482 ms | ✅ | 🥇x1 🥉x1 🏳️x1 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000233s 6th  | 0.000127s ✓ 1st | 0.000158s ✓ 5th | 0.000128s ✓ 2nd | 0.000142s ✓ 4th | 0.000129s ✓ 3rd
25x20     | 0.000144s 1st  | 0.000165s ✓ 5th | 0.000172s ✓ 6th | 0.000159s ✓ 4th | 0.000155s ✓ 3rd | 0.000148s ✓ 2nd
50x50     | 0.000269s 6th  | 0.000203s ✓ 3rd | 0.000184s ✓ 1st | 0.000191s ✓ 2nd | 0.000223s ✓ 4th | 0.000254s ✓ 5th
100x150   | 0.000417s 4th  | 0.001233s ✓ 6th | 0.000308s ✓ 1st | 0.000356s ✓ 3rd | 0.001072s ✓ 5th | 0.000326s ✓ 2nd
250x250   | 0.002866s 5th  | 0.003220s ✓ 6th | 0.001664s ✓ 1st | 0.001702s ✓ 3rd | 0.002252s ✓ 4th | 0.001676s ✓ 2nd
550x500   | 0.008314s 1st  | 0.249585s ✓ 6th | 0.011429s ✓ 2nd | 0.011442s ✓ 3rd | 0.030332s ✓ 5th | 0.011470s ✓ 4th
1000x1000 | 0.046902s 5th  | 0.080581s ✓ 6th | 0.039630s ✓ 2nd | 0.039960s ✓ 3rd | 0.045573s ✓ 4th | 0.038703s ✓ 1st
2000x2500 | 0.074322s 4th  | 3.490300s ✓ 6th | 0.020954s ✓ 1st | 0.021199s ✓ 2nd | 2.761126s ✓ 5th | 0.024095s ✓ 3rd
5000x5000 | 2.614220s 5th  | 4.553976s ✓ 6th | 2.238387s ✓ 3rd | 2.240301s ✓ 4th | 1.912648s ✓ 2nd | 1.146587s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1223.3865 ms | ✅ | 🥇x2 🥈x3 🥉x2 🚩x1 🏳️x1
     2. LAPX LAPJV     :  2312.8874 ms | ✅ | 🥇x4 🥈x2 🥉x1 🏳️x1 🥴x1
     3. LAPX LAPJVX    :  2315.4386 ms | ✅ | 🥈x3 🥉x4 🚩x2
     4. BASELINE SciPy :  2747.6856 ms | ⭐ | 🥇x2 🚩x2 🏳️x3 🥴x2
     5. LAPX LAPJVC    :  4753.5226 ms | ✅ | 🥈x1 🥉x1 🚩x4 🏳️x3
     6. LAPX LAPJV-IFT :  8379.3885 ms | ✅ | 🥇x1 🥉x1 🏳️x1 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000210s 6th  | 0.000136s ✓ 4th | 0.000133s ✓ 3rd | 0.000127s ✓ 1st | 0.000142s ✓ 5th | 0.000131s ✓ 2nd
25x20     | 0.000150s 3rd  | 0.000203s ✓ 6th | 0.000145s ✓ 1st | 0.000148s ✓ 2nd | 0.000152s ✓ 4th | 0.000178s ✓ 5th
50x50     | 0.000243s 6th  | 0.000239s ✓ 5th | 0.000194s ✓ 1st | 0.000201s ✓ 2nd | 0.000233s ✓ 4th | 0.000203s ✓ 3rd
100x150   | 0.000426s 4th  | 0.001229s ✓ 6th | 0.000335s ✓ 3rd | 0.000329s ✓ 2nd | 0.001090s ✓ 5th | 0.000311s ✓ 1st
250x250   | 0.002309s 6th  | 0.002270s ✓ 5th | 0.001100s ✓ 1st | 0.001198s ✓ 3rd | 0.001776s ✓ 4th | 0.001157s ✓ 2nd
550x500   | 0.007958s 1st  | 0.236500s ✓ 6th | 0.012768s ✓ 3rd | 0.012651s ✓ 2nd | 0.039369s ✓ 5th | 0.012789s ✓ 4th
1000x1000 | 0.047147s 5th  | 0.089055s ✓ 6th | 0.044446s ✓ 4th | 0.044309s ✓ 3rd | 0.043942s ✓ 2nd | 0.043357s ✓ 1st
2000x2500 | 0.078020s 4th  | 3.430561s ✓ 6th | 0.021284s ✓ 1st | 0.021622s ✓ 2nd | 2.844436s ✓ 5th | 0.024936s ✓ 3rd
5000x5000 | 2.490763s 5th  | 4.480608s ✓ 6th | 2.195783s ✓ 3rd | 2.198696s ✓ 4th | 2.009281s ✓ 2nd | 1.052344s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1135.4053 ms | ✅ | 🥇x3 🥈x2 🥉x2 🚩x1 🏳️x1
     2. LAPX LAPJV     :  2276.1874 ms | ✅ | 🥇x4 🥉x4 🚩x1
     3. LAPX LAPJVX    :  2279.2815 ms | ✅ | 🥇x1 🥈x5 🥉x2 🚩x1
     4. BASELINE SciPy :  2627.2261 ms | ⭐ | 🥇x1 🥉x1 🚩x2 🏳️x2 🥴x3
     5. LAPX LAPJVC    :  4940.4219 ms | ✅ | 🥈x2 🚩x3 🏳️x4
     6. LAPX LAPJV-IFT :  8240.8002 ms | ✅ | 🚩x1 🏳️x2 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉 
```

👁️ See more results on various platforms and architectures [here](https://github.com/rathaROG/lapx/actions/runs/18830580672).

</details>
