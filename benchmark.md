[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg)](https://badge.fury.io/py/lapx)
[![Benchmark (Single)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml)
[![Benchmark (Batch)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_batch.yaml)
[![Benchmark (Object Tracking)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml/badge.svg)](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml)

# 🏆 Quick Benchmark

`lapx` focuses more on real-world applications, and the [benchmark_batch.py](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_batch.py) 
and [benchmark_single.py](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_single.py) are **not** 
intended for scientific research or competitive evaluation. Instead, it provides a quick and accessible way for 
you to run benchmark tests on your own machine. Below, you will also find a collection of interesting results 
gathered from various major platforms and architectures.

## 💡 Run the quick benchmark

To see some quick benchmark results for these functions, simply run:

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/benchmarks
python benchmark_batch.py
python benchmark_single.py
```

Note: [SciPy](https://pypi.org/project/scipy/) is used as the baseline in the benchmark single `benchmark_single.py`.

📊 Some benchmark results using `lapx` [v0.9.1](https://github.com/rathaROG/lapx/releases/tag/v0.9.1) (2025/10/31):

<details><summary>🗂️ Batch on my local Windows 11 i9-13900KS (8 p-core + 8 e-core) + python 3.11.9:</summary><br>

```
numpy==2.2.6
lapx @ git+https://github.com/rathaROG/lapx.git@8e1a5c5cbe1a813d5ee80570b285e316fcc99f7a # 0.9.1
```

```
Microsoft Windows [Version 10.0.26200.7019]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\lapx_all\tmp\lapx\benchmarks>python benchmark_batch.py

# 10 x (4000x4000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=16.48732425, time=0.70944118s
  CPU lapx-batch-jvs     :  cost=16.48732425, time=0.43542552s
  CPU lapx-batch-jvxa    :  cost=16.48732425, time=0.69259763s
  CPU lapx-batch-jvsa    :  cost=16.48732425, time=0.44047427s
  CPU lapx-batch-jvsa64  :  cost=16.48732425, time=0.78757620s
  CPU lapx-loop-jvx      :  cost=16.48732425, time=4.28805971s
  CPU lapx-loop-jvs      :  cost=16.48732425, time=2.85956860s

# 20 x (3000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=16.69374066, time=0.19042516s
  CPU lapx-batch-jvs     :  cost=16.69374066, time=0.19088888s
  CPU lapx-batch-jvxa    :  cost=16.69374066, time=0.17689967s
  CPU lapx-batch-jvsa    :  cost=16.69374066, time=0.18332553s
  CPU lapx-batch-jvsa64  :  cost=16.69374066, time=0.18913651s
  CPU lapx-loop-jvx      :  cost=16.69374066, time=0.85293603s
  CPU lapx-loop-jvs      :  cost=16.69374066, time=1.09705830s

# 50 x (2000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=81.88714629, time=0.40948844s
  CPU lapx-batch-jvs     :  cost=81.88714629, time=0.34669971s
  CPU lapx-batch-jvxa    :  cost=81.88714629, time=0.39700556s
  CPU lapx-batch-jvsa    :  cost=81.88714629, time=0.33096647s
  CPU lapx-batch-jvsa64  :  cost=81.88714629, time=0.44180655s
  CPU lapx-loop-jvx      :  cost=81.88714629, time=3.34968209s
  CPU lapx-loop-jvs      :  cost=81.88714629, time=3.22587180s

# 100 x (1000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=57.81402817, time=0.18936110s
  CPU lapx-batch-jvs     :  cost=57.81402817, time=0.16963148s
  CPU lapx-batch-jvxa    :  cost=57.81402817, time=0.18951726s
  CPU lapx-batch-jvsa    :  cost=57.81402817, time=0.16521573s
  CPU lapx-batch-jvsa64  :  cost=57.81402817, time=0.25324345s
  CPU lapx-loop-jvx      :  cost=57.81402817, time=0.96780610s
  CPU lapx-loop-jvs      :  cost=57.81402817, time=1.20634890s

# 500 x (1000x1000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=820.77561875, time=0.55759573s
  CPU lapx-batch-jvs     :  cost=820.77561875, time=0.56053782s
  CPU lapx-batch-jvxa    :  cost=820.77561875, time=0.55279994s
  CPU lapx-batch-jvsa    :  cost=820.77561875, time=0.56725907s
  CPU lapx-batch-jvsa64  :  cost=820.77561875, time=0.58956695s
  CPU lapx-loop-jvx      :  cost=820.77561875, time=6.52994561s
  CPU lapx-loop-jvs      :  cost=820.77561875, time=7.08902001s
```

</details>

<details><summary>📄 Single-matrix on ubuntu-latest + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18984608559/job/54225293380

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.53 x slower 
 * lapjv : ✅ Passed 🐌 5.17 x slower 
 * lapjvx : ✅ Passed 🐌 2.58 x slower 
 * lapjvxa : ✅ Passed 🐌 1.69 x slower 
 * lapjvs : ✅ Passed 🐌 3.41 x slower 
 * lapjvsa : ✅ Passed 🐌 3.36 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00001055s
   2. lapjvc  	: 0.00001615s
   3. lapjvxa  	: 0.00001785s
   4. lapjvx  	: 0.00002719s
   5. lapjvsa  	: 0.00003547s
   6. lapjvs  	: 0.00003601s
   7. lapjv  	: 0.00005454s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.65 x slower 
 * lapjv : ✅ Passed 🐌 4.75 x slower 
 * lapjvx : ✅ Passed 🐌 2.0 x slower 
 * lapjvxa : ✅ Passed 🐌 1.98 x slower 
 * lapjvs : ✅ Passed 🐌 2.43 x slower 
 * lapjvsa : ✅ Passed 🏆 1.11 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00000672s
   2. scipy ⭐ 	: 0.00000748s
   3. lapjvc  	: 0.00001232s
   4. lapjvxa  	: 0.00001484s
   5. lapjvx  	: 0.00001497s
   6. lapjvs  	: 0.00001819s
   7. lapjv  	: 0.00003557s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.16 x slower 
 * lapjv : ✅ Passed 🐌 9.32 x slower 
 * lapjvx : ✅ Passed 🐌 4.22 x slower 
 * lapjvxa : ✅ Passed 🐌 2.93 x slower 
 * lapjvs : ✅ Passed 🐌 4.38 x slower 
 * lapjvsa : ✅ Passed 🐌 4.89 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000558s
   2. lapjvc  	: 0.00001205s
   3. lapjvxa  	: 0.00001633s
   4. lapjvx  	: 0.00002352s
   5. lapjvs  	: 0.00002447s
   6. lapjvsa  	: 0.00002730s
   7. lapjv  	: 0.00005201s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.41 x slower 
 * lapjv : ✅ Passed 🐌 1.04 x slower 
 * lapjvx : ✅ Passed 🏆 1.42 x faster 
 * lapjvxa : ✅ Passed 🏆 1.77 x faster 
 * lapjvs : ✅ Passed 🏆 1.37 x faster 
 * lapjvsa : ✅ Passed 🏆 1.5 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00003649s
   2. lapjvsa  	: 0.00004314s
   3. lapjvx  	: 0.00004534s
   4. lapjvs  	: 0.00004701s
   5. scipy ⭐ 	: 0.00006450s
   6. lapjv  	: 0.00006738s
   7. lapjvc  	: 0.00009109s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.21 x faster 
 * lapjv : ✅ Passed 🏆 1.03 x faster 
 * lapjvx : ✅ Passed 🏆 1.54 x faster 
 * lapjvxa : ✅ Passed 🏆 2.0 x faster 
 * lapjvs : ✅ Passed 🏆 1.46 x faster 
 * lapjvsa : ✅ Passed 🏆 2.49 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00002653s
   2. lapjvxa  	: 0.00003293s
   3. lapjvx  	: 0.00004293s
   4. lapjvs  	: 0.00004526s
   5. lapjvc  	: 0.00005453s
   6. lapjv  	: 0.00006407s
   7. scipy ⭐ 	: 0.00006601s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.45 x slower 
 * lapjv : ✅ Passed 🏆 1.11 x faster 
 * lapjvx : ✅ Passed 🏆 1.79 x faster 
 * lapjvxa : ✅ Passed 🏆 2.13 x faster 
 * lapjvs : ✅ Passed 🏆 1.73 x faster 
 * lapjvsa : ✅ Passed 🏆 1.41 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00003505s
   2. lapjvx  	: 0.00004173s
   3. lapjvs  	: 0.00004336s
   4. lapjvsa  	: 0.00005296s
   5. lapjv  	: 0.00006746s
   6. scipy ⭐ 	: 0.00007480s
   7. lapjvc  	: 0.00010855s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 3.8 x slower 
 * lapjv : ✅ Passed 🏆 2.17 x faster 
 * lapjvx : ✅ Passed 🏆 3.0 x faster 
 * lapjvxa : ✅ Passed 🏆 4.33 x faster 
 * lapjvs : ✅ Passed 🏆 4.67 x faster 
 * lapjvsa : ✅ Passed 🏆 4.63 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvs  	: 0.00102049s
   2. lapjvsa  	: 0.00102816s
   3. lapjvxa  	: 0.00110050s
   4. lapjvx  	: 0.00158621s
   5. lapjv  	: 0.00219654s
   6. scipy ⭐ 	: 0.00476269s
   7. lapjvc  	: 0.01809850s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.24 x faster 
 * lapjv : ✅ Passed 🏆 1.07 x faster 
 * lapjvx : ✅ Passed 🏆 1.4 x faster 
 * lapjvxa : ✅ Passed 🏆 1.41 x faster 
 * lapjvs : ✅ Passed 🏆 1.43 x faster 
 * lapjvsa : ✅ Passed 🏆 1.44 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00626876s
   2. lapjvs  	: 0.00630340s
   3. lapjvxa  	: 0.00640438s
   4. lapjvx  	: 0.00642594s
   5. lapjvc  	: 0.00729600s
   6. lapjv  	: 0.00845927s
   7. scipy ⭐ 	: 0.00901426s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.58 x slower 
 * lapjv : ✅ Passed 🏆 2.04 x faster 
 * lapjvx : ✅ Passed 🏆 4.01 x faster 
 * lapjvxa : ✅ Passed 🏆 4.14 x faster 
 * lapjvs : ✅ Passed 🏆 4.42 x faster 
 * lapjvsa : ✅ Passed 🏆 4.49 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00114634s
   2. lapjvs  	: 0.00116270s
   3. lapjvxa  	: 0.00124253s
   4. lapjvx  	: 0.00128147s
   5. lapjv  	: 0.00252214s
   6. scipy ⭐ 	: 0.00514199s
   7. lapjvc  	: 0.02353958s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 228.4 x slower 
 * lapjv : ✅ Passed 🏆 1.09 x faster 
 * lapjvx : ✅ Passed 🏆 1.24 x faster 
 * lapjvxa : ✅ Passed 🏆 1.25 x faster 
 * lapjvs : ✅ Passed 🐌 1.1 x slower 
 * lapjvsa : ✅ Passed 🐌 1.12 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.08090518s
   2. lapjvx  	: 0.08157910s
   3. lapjv  	: 0.09252072s
   4. scipy ⭐ 	: 0.10097560s
   5. lapjvs  	: 0.11067445s
   6. lapjvsa  	: 0.11269509s
   7. lapjvc  	: 23.06289135s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.33 x faster 
 * lapjv : ✅ Passed 🐌 1.02 x slower 
 * lapjvx : ✅ Passed 🏆 1.42 x faster 
 * lapjvxa : ✅ Passed 🏆 1.42 x faster 
 * lapjvs : ✅ Passed 🏆 2.3 x faster 
 * lapjvsa : ✅ Passed 🏆 2.3 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.97763377s
   2. lapjvs  	: 0.97772870s
   3. lapjvx  	: 1.58527767s
   4. lapjvxa  	: 1.58615075s
   5. lapjvc  	: 1.69588961s
   6. scipy ⭐ 	: 2.24908994s
   7. lapjv  	: 2.28853597s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 217.35 x slower 
 * lapjv : ✅ Passed 🏆 2.07 x faster 
 * lapjvx : ✅ Passed 🏆 2.4 x faster 
 * lapjvxa : ✅ Passed 🏆 2.42 x faster 
 * lapjvs : ✅ Passed 🏆 1.65 x faster 
 * lapjvsa : ✅ Passed 🏆 1.64 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.16547692s
   2. lapjvx  	: 0.16660061s
   3. lapjv  	: 0.19367327s
   4. lapjvs  	: 0.24263112s
   5. lapjvsa  	: 0.24431215s
   6. scipy ⭐ 	: 0.40064618s
   7. lapjvc  	: 87.08241680s
 ------------------------------- 
```

</details>

<details><summary>📄 Single-matrix on macos-latest (arm) + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18984608559/job/54225293427

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.43 x slower 
 * lapjv : ✅ Passed 🐌 5.19 x slower 
 * lapjvx : ✅ Passed 🐌 2.7 x slower 
 * lapjvxa : ✅ Passed 🐌 1.48 x slower 
 * lapjvs : ✅ Passed 🐌 3.41 x slower 
 * lapjvsa : ✅ Passed 🐌 3.07 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000625s
   2. lapjvxa  	: 0.00000925s
   3. lapjvc  	: 0.00001521s
   4. lapjvx  	: 0.00001688s
   5. lapjvsa  	: 0.00001917s
   6. lapjvs  	: 0.00002129s
   7. lapjv  	: 0.00003242s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 3.64 x slower 
 * lapjv : ✅ Passed 🐌 4.33 x slower 
 * lapjvx : ✅ Passed 🐌 2.05 x slower 
 * lapjvxa : ✅ Passed 🐌 1.41 x slower 
 * lapjvs : ✅ Passed 🐌 2.8 x slower 
 * lapjvsa : ✅ Passed 🏆 1.17 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00000346s
   2. scipy ⭐ 	: 0.00000404s
   3. lapjvxa  	: 0.00000571s
   4. lapjvx  	: 0.00000829s
   5. lapjvs  	: 0.00001133s
   6. lapjvc  	: 0.00001471s
   7. lapjv  	: 0.00001750s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.76 x slower 
 * lapjv : ✅ Passed 🐌 5.61 x slower 
 * lapjvx : ✅ Passed 🐌 2.84 x slower 
 * lapjvxa : ✅ Passed 🐌 2.87 x slower 
 * lapjvs : ✅ Passed 🐌 3.57 x slower 
 * lapjvsa : ✅ Passed 🐌 4.02 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000333s
   2. lapjvc  	: 0.00000921s
   3. lapjvx  	: 0.00000946s
   4. lapjvxa  	: 0.00000958s
   5. lapjvs  	: 0.00001192s
   6. lapjvsa  	: 0.00001342s
   7. lapjv  	: 0.00001871s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.9 x slower 
 * lapjv : ✅ Passed 🏆 1.31 x faster 
 * lapjvx : ✅ Passed 🏆 1.86 x faster 
 * lapjvxa : ✅ Passed 🏆 2.32 x faster 
 * lapjvs : ✅ Passed 🏆 1.63 x faster 
 * lapjvsa : ✅ Passed 🏆 1.91 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00002146s
   2. lapjvsa  	: 0.00002608s
   3. lapjvx  	: 0.00002679s
   4. lapjvs  	: 0.00003046s
   5. lapjv  	: 0.00003796s
   6. scipy ⭐ 	: 0.00004979s
   7. lapjvc  	: 0.00009475s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.61 x slower 
 * lapjv : ✅ Passed 🏆 1.41 x faster 
 * lapjvx : ✅ Passed 🏆 2.05 x faster 
 * lapjvxa : ✅ Passed 🏆 2.66 x faster 
 * lapjvs : ✅ Passed 🏆 1.69 x faster 
 * lapjvsa : ✅ Passed 🏆 2.87 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00001892s
   2. lapjvxa  	: 0.00002046s
   3. lapjvx  	: 0.00002650s
   4. lapjvs  	: 0.00003208s
   5. lapjv  	: 0.00003850s
   6. scipy ⭐ 	: 0.00005437s
   7. lapjvc  	: 0.00008771s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.02 x slower 
 * lapjv : ✅ Passed 🏆 1.27 x faster 
 * lapjvx : ✅ Passed 🏆 1.86 x faster 
 * lapjvxa : ✅ Passed 🏆 2.27 x faster 
 * lapjvs : ✅ Passed 🏆 1.63 x faster 
 * lapjvsa : ✅ Passed 🏆 1.83 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00002217s
   2. lapjvx  	: 0.00002708s
   3. lapjvsa  	: 0.00002746s
   4. lapjvs  	: 0.00003079s
   5. lapjv  	: 0.00003954s
   6. scipy ⭐ 	: 0.00005025s
   7. lapjvc  	: 0.00010162s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 7.42 x slower 
 * lapjv : ✅ Passed 🏆 2.99 x faster 
 * lapjvx : ✅ Passed 🏆 3.78 x faster 
 * lapjvxa : ✅ Passed 🏆 3.7 x faster 
 * lapjvs : ✅ Passed 🏆 2.95 x faster 
 * lapjvsa : ✅ Passed 🏆 3.03 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.00077642s
   2. lapjvxa  	: 0.00079467s
   3. lapjvsa  	: 0.00096896s
   4. lapjv  	: 0.00098104s
   5. lapjvs  	: 0.00099629s
   6. scipy ⭐ 	: 0.00293721s
   7. lapjvc  	: 0.02179187s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.22 x slower 
 * lapjv : ✅ Passed 🏆 2.3 x faster 
 * lapjvx : ✅ Passed 🏆 2.42 x faster 
 * lapjvxa : ✅ Passed 🏆 2.39 x faster 
 * lapjvs : ✅ Passed 🏆 2.04 x faster 
 * lapjvsa : ✅ Passed 🏆 2.17 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.00280804s
   2. lapjvxa  	: 0.00284217s
   3. lapjv  	: 0.00295687s
   4. lapjvsa  	: 0.00313346s
   5. lapjvs  	: 0.00333604s
   6. scipy ⭐ 	: 0.00679725s
   7. lapjvc  	: 0.00829000s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 6.83 x slower 
 * lapjv : ✅ Passed 🏆 2.53 x faster 
 * lapjvx : ✅ Passed 🏆 3.11 x faster 
 * lapjvxa : ✅ Passed 🏆 2.9 x faster 
 * lapjvs : ✅ Passed 🏆 2.57 x faster 
 * lapjvsa : ✅ Passed 🏆 2.52 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.00112583s
   2. lapjvxa  	: 0.00120517s
   3. lapjvs  	: 0.00136033s
   4. lapjv  	: 0.00138454s
   5. lapjvsa  	: 0.00138996s
   6. scipy ⭐ 	: 0.00349771s
   7. lapjvc  	: 0.02389029s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 303.21 x slower 
 * lapjv : ✅ Passed 🐌 4.3 x slower 
 * lapjvx : ✅ Passed 🐌 1.65 x slower 
 * lapjvxa : ✅ Passed 🐌 1.37 x slower 
 * lapjvs : ✅ Passed 🐌 2.67 x slower 
 * lapjvsa : ✅ Passed 🐌 3.06 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.08946058s
   2. lapjvxa  	: 0.12264183s
   3. lapjvx  	: 0.14727325s
   4. lapjvs  	: 0.23845862s
   5. lapjvsa  	: 0.27356104s
   6. lapjv  	: 0.38505029s
   7. lapjvc  	: 27.12492925s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.61 x slower 
 * lapjv : ✅ Passed 🏆 1.6 x faster 
 * lapjvx : ✅ Passed 🏆 1.86 x faster 
 * lapjvxa : ✅ Passed 🏆 1.89 x faster 
 * lapjvs : ✅ Passed 🏆 2.06 x faster 
 * lapjvsa : ✅ Passed 🏆 2.6 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.94210742s
   2. lapjvs  	: 1.19320912s
   3. lapjvxa  	: 1.29491192s
   4. lapjvx  	: 1.32094417s
   5. lapjv  	: 1.53106525s
   6. scipy ⭐ 	: 2.45269650s
   7. lapjvc  	: 3.93988354s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 313.47 x slower 
 * lapjv : ✅ Passed 🐌 1.34 x slower 
 * lapjvx : ✅ Passed 🏆 1.46 x faster 
 * lapjvxa : ✅ Passed 🏆 2.76 x faster 
 * lapjvs : ✅ Passed 🐌 1.47 x slower 
 * lapjvsa : ✅ Passed 🐌 1.38 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.13445975s
   2. lapjvx  	: 0.25395613s
   3. scipy ⭐ 	: 0.37139379s
   4. lapjv  	: 0.49666225s
   5. lapjvsa  	: 0.51077446s
   6. lapjvs  	: 0.54710338s
   7. lapjvc  	: 116.42058821s
 ------------------------------- 
```

</details>

👁️ See newer benchmark results on all platforms [here on GitHub](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml).

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

This [benchmark_tracking.py](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) is specifically designed for ***Object Tracking*** application, with [SciPy](https://pypi.org/project/scipy/) as the baseline.

```
pip install -U lapx
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/benchmarks
python benchmark_tracking.py
```

As shown in the benchmark results below, the new function [`lapjvx()`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) (LAPX LAPJVX in the tables) and the original [`lapjv()`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv) (LAPX LAPJV in the tables) consistently matches the baseline outputs of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html), as indicated by “✓” and ✅ in the tables.

In most scenarios, `lapjvx()` and `lapjv()` demonstrate faster performance than the baseline SciPy's `linear_sum_assignment`, and they remain competitive with other LAPX variants such as [`lapjvc`](https://github.com/rathaROG/lapx#4-the-new-function-lapjvc) (LAPX LAPJVC in the tables). When in-function filtering with `cost_limit` is used, `lapjv()` (LAPX LAPJV-IFT in the tables) experiences a significant performance impact and can produce different outputs compared to SciPy's baseline, as indicated by “✗” and ⚠️ in the tables.

🆕 `lapx` [v0.7.0](https://github.com/rathaROG/lapx/releases/tag/v0.7.0) introduced [`lapjvs()`](https://github.com/rathaROG/lapx#5-the-new-function-lapjvs), a highly competitive solver. Notably, `lapjvs()` outperforms other solvers in terms of speed when the input cost matrix is square, especially for sizes 5000 and above.

💡 To achieve optimal performance of `lapjvx()` or `lapjv()` in object tracking application, follow the implementation in the current [`benchmark_tracking.py`](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) script.

<details><summary>📊 Show the results:</summary><br>

Run on my local Windows 11 i9-13900KS (8 p-core + 8 e-core) + python 3.11.9
```
numpy==2.2.6
scipy==1.16.3
lapx @ git+https://github.com/rathaROG/lapx.git@8e1a5c5cbe1a813d5ee80570b285e316fcc99f7a # 0.9.1
```

```
Microsoft Windows [Version 10.0.26200.7019]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\lapx_all\tmp\lapx\benchmarks>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000056s 3rd  | 0.000056s ✗ 4th | 0.000061s ✓ 6th | 0.000050s ✓ 1st | 0.000060s ✓ 5th | 0.000052s ✓ 2nd
25x20     | 0.000052s 3rd  | 0.000061s ✗ 5th | 0.000061s ✓ 6th | 0.000049s ✓ 1st | 0.000056s ✓ 4th | 0.000051s ✓ 2nd
50x50     | 0.000084s 4th  | 0.000085s ✗ 5th | 0.000072s ✓ 2nd | 0.000063s ✓ 1st | 0.000105s ✓ 6th | 0.000073s ✓ 3rd
100x150   | 0.000148s 4th  | 0.000564s ✓ 5th | 0.000135s ✓ 3rd | 0.000110s ✓ 1st | 0.000671s ✓ 6th | 0.000120s ✓ 2nd
250x250   | 0.001327s 4th  | 0.001399s ✓ 5th | 0.000527s ✓ 2nd | 0.000510s ✓ 1st | 0.001417s ✓ 6th | 0.000579s ✓ 3rd
550x500   | 0.003237s 4th  | 0.011715s ✓ 5th | 0.001379s ✓ 2nd | 0.001344s ✓ 1st | 0.014237s ✓ 6th | 0.001463s ✓ 3rd
1000x1000 | 0.023160s 5th  | 0.020795s ✓ 4th | 0.006882s ✓ 2nd | 0.006875s ✓ 1st | 0.027876s ✓ 6th | 0.008634s ✓ 3rd
2000x2500 | 0.036176s 4th  | 1.683198s ✓ 5th | 0.014039s ✓ 1st | 0.015730s ✓ 2nd | 1.683977s ✓ 6th | 0.023320s ✓ 3rd
5000x5000 | 1.116971s 4th  | 1.807397s ✓ 6th | 0.811022s ✓ 2nd | 0.844260s ✓ 3rd | 1.125310s ✓ 5th | 0.421959s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   456.2515 ms | ✅ | 🥇x1 🥈x3 🥉x5
     2. LAPX LAPJV     :   834.1779 ms | ✅ | 🥇x1 🥈x5 🥉x1 🥴x2
     3. LAPX LAPJVX    :   868.9913 ms | ✅ | 🥇x7 🥈x1 🥉x1
     4. BASELINE SciPy :  1181.2127 ms | ⭐ | 🥉x2 🚩x6 🏳️x1
     5. LAPX LAPJVC    :  2853.7103 ms | ✅ | 🚩x1 🏳️x2 🥴x6
     6. LAPX LAPJV-IFT :  3525.2702 ms | ⚠️ | 🚩x2 🏳️x6 🥴x1
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000058s 6th  | 0.000050s ✗ 5th | 0.000048s ✓ 4th | 0.000039s ✓ 1st | 0.000045s ✓ 3rd | 0.000043s ✓ 2nd
25x20     | 0.000045s 1st  | 0.000064s ✗ 6th | 0.000056s ✓ 5th | 0.000048s ✓ 3rd | 0.000051s ✓ 4th | 0.000048s ✓ 2nd
50x50     | 0.000080s 4th  | 0.000091s ✗ 5th | 0.000077s ✓ 3rd | 0.000068s ✓ 1st | 0.000135s ✓ 6th | 0.000076s ✓ 2nd
100x150   | 0.000149s 4th  | 0.000717s ✓ 6th | 0.000123s ✓ 2nd | 0.000110s ✓ 1st | 0.000659s ✓ 5th | 0.000127s ✓ 3rd
250x250   | 0.001166s 5th  | 0.001069s ✓ 4th | 0.000287s ✓ 2nd | 0.000278s ✓ 1st | 0.002031s ✓ 6th | 0.000369s ✓ 3rd
550x500   | 0.003814s 4th  | 0.011264s ✓ 5th | 0.001395s ✓ 2nd | 0.001389s ✓ 1st | 0.016663s ✓ 6th | 0.001569s ✓ 3rd
1000x1000 | 0.024046s 4th  | 0.040244s ✓ 6th | 0.018605s ✓ 2nd | 0.018562s ✓ 1st | 0.030481s ✓ 5th | 0.020355s ✓ 3rd
2000x2500 | 0.035922s 4th  | 1.732549s ✓ 6th | 0.016267s ✓ 2nd | 0.014801s ✓ 1st | 1.713590s ✓ 5th | 0.023109s ✓ 3rd
5000x5000 | 1.088875s 5th  | 1.248801s ✓ 6th | 0.501658s ✓ 3rd | 0.484758s ✓ 2nd | 1.040230s ✓ 4th | 0.378295s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   423.9891 ms | ✅ | 🥇x1 🥈x3 🥉x5
     2. LAPX LAPJVX    :   520.0521 ms | ✅ | 🥇x7 🥈x1 🥉x1
     3. LAPX LAPJV     :   538.5159 ms | ✅ | 🥈x5 🥉x2 🚩x1 🏳️x1
     4. BASELINE SciPy :  1154.1538 ms | ⭐ | 🥇x1 🚩x5 🏳️x2 🥴x1
     5. LAPX LAPJVC    :  2803.8866 ms | ✅ | 🥉x1 🚩x2 🏳️x3 🥴x3
     6. LAPX LAPJV-IFT :  3034.8488 ms | ⚠️ | 🚩x1 🏳️x3 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000056s 6th  | 0.000045s ✓ 4th | 0.000046s ✓ 5th | 0.000040s ✓ 1st | 0.000044s ✓ 3rd | 0.000041s ✓ 2nd
25x20     | 0.000045s 1st  | 0.000063s ✓ 6th | 0.000058s ✓ 5th | 0.000047s ✓ 2nd | 0.000057s ✓ 4th | 0.000049s ✓ 3rd
50x50     | 0.000082s 4th  | 0.000082s ✓ 5th | 0.000067s ✓ 3rd | 0.000059s ✓ 1st | 0.000102s ✓ 6th | 0.000061s ✓ 2nd
100x150   | 0.000145s 3rd  | 0.000699s ✓ 6th | 0.000153s ✓ 4th | 0.000108s ✓ 1st | 0.000661s ✓ 5th | 0.000117s ✓ 2nd
250x250   | 0.001362s 5th  | 0.001290s ✓ 4th | 0.000435s ✓ 1st | 0.000468s ✓ 2nd | 0.001533s ✓ 6th | 0.000469s ✓ 3rd
550x500   | 0.003384s 4th  | 0.011987s ✓ 5th | 0.001601s ✓ 3rd | 0.001488s ✓ 1st | 0.016294s ✓ 6th | 0.001589s ✓ 2nd
1000x1000 | 0.022760s 4th  | 0.041152s ✓ 6th | 0.017574s ✓ 1st | 0.018122s ✓ 2nd | 0.027452s ✓ 5th | 0.019619s ✓ 3rd
2000x2500 | 0.035389s 4th  | 1.731252s ✓ 6th | 0.016473s ✓ 2nd | 0.015285s ✓ 1st | 1.536600s ✓ 5th | 0.023138s ✓ 3rd
5000x5000 | 1.090672s 5th  | 1.585820s ✓ 6th | 0.698390s ✓ 3rd | 0.681333s ✓ 2nd | 1.086945s ✓ 4th | 0.527087s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   572.1697 ms | ✅ | 🥇x1 🥈x4 🥉x4
     2. LAPX LAPJVX    :   716.9497 ms | ✅ | 🥇x5 🥈x4
     3. LAPX LAPJV     :   734.7961 ms | ✅ | 🥇x2 🥈x1 🥉x3 🚩x1 🏳️x2
     4. BASELINE SciPy :  1153.8943 ms | ⭐ | 🥇x1 🥉x1 🚩x4 🏳️x2 🥴x1
     5. LAPX LAPJVC    :  2669.6871 ms | ✅ | 🥉x1 🚩x2 🏳️x3 🥴x3
     6. LAPX LAPJV-IFT :  3372.3898 ms | ✅ | 🚩x2 🏳️x2 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000040s 3rd  | 0.000046s ✓ 6th | 0.000045s ✓ 5th | 0.000037s ✓ 1st | 0.000042s ✓ 4th | 0.000040s ✓ 2nd
25x20     | 0.000042s 1st  | 0.000117s ✓ 6th | 0.000058s ✓ 4th | 0.000062s ✓ 5th | 0.000056s ✓ 3rd | 0.000051s ✓ 2nd
50x50     | 0.000080s 4th  | 0.000084s ✓ 5th | 0.000062s ✓ 3rd | 0.000055s ✓ 1st | 0.000096s ✓ 6th | 0.000060s ✓ 2nd
100x150   | 0.000142s 4th  | 0.000650s ✓ 6th | 0.000131s ✓ 3rd | 0.000104s ✓ 1st | 0.000586s ✓ 5th | 0.000106s ✓ 2nd
250x250   | 0.001134s 5th  | 0.001073s ✓ 4th | 0.000330s ✓ 2nd | 0.000317s ✓ 1st | 0.001307s ✓ 6th | 0.000389s ✓ 3rd
550x500   | 0.003360s 4th  | 0.010832s ✓ 5th | 0.001444s ✓ 2nd | 0.001410s ✓ 1st | 0.015605s ✓ 6th | 0.001537s ✓ 3rd
1000x1000 | 0.020469s 4th  | 0.023088s ✓ 5th | 0.008001s ✓ 1st | 0.008134s ✓ 2nd | 0.024824s ✓ 6th | 0.010342s ✓ 3rd
2000x2500 | 0.038874s 4th  | 1.661149s ✓ 6th | 0.014831s ✓ 1st | 0.016389s ✓ 2nd | 1.640910s ✓ 5th | 0.022910s ✓ 3rd
5000x5000 | 0.984126s 5th  | 1.032316s ✓ 6th | 0.393411s ✓ 2nd | 0.380302s ✓ 1st | 0.949218s ✓ 4th | 0.401329s ✓ 3rd
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVX    :   406.8110 ms | ✅ | 🥇x6 🥈x2 🏳️x1
     2. LAPX LAPJV     :   418.3143 ms | ✅ | 🥇x2 🥈x3 🥉x2 🚩x1 🏳️x1
     3. LAPX LAPJVS    :   436.7637 ms | ✅ | 🥈x4 🥉x5
     4. BASELINE SciPy :  1048.2659 ms | ⭐ | 🥇x1 🥉x1 🚩x5 🏳️x2
     5. LAPX LAPJVC    :  2632.6435 ms | ✅ | 🥉x1 🚩x2 🏳️x2 🥴x4
     6. LAPX LAPJV-IFT :  2729.3534 ms | ✅ | 🚩x1 🏳️x3 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000051s 6th  | 0.000045s ✓ 4th | 0.000049s ✓ 5th | 0.000037s ✓ 1st | 0.000042s ✓ 3rd | 0.000038s ✓ 2nd
25x20     | 0.000044s 1st  | 0.000057s ✓ 6th | 0.000055s ✓ 4th | 0.000045s ✓ 2nd | 0.000056s ✓ 5th | 0.000046s ✓ 3rd
50x50     | 0.000068s 4th  | 0.000076s ✓ 5th | 0.000064s ✓ 3rd | 0.000055s ✓ 1st | 0.000089s ✓ 6th | 0.000059s ✓ 2nd
100x150   | 0.000152s 4th  | 0.000662s ✓ 5th | 0.000140s ✓ 3rd | 0.000107s ✓ 1st | 0.000692s ✓ 6th | 0.000112s ✓ 2nd
250x250   | 0.001222s 4th  | 0.001813s ✓ 6th | 0.000859s ✓ 2nd | 0.000820s ✓ 1st | 0.001422s ✓ 5th | 0.000873s ✓ 3rd
550x500   | 0.003388s 4th  | 0.010608s ✓ 5th | 0.001394s ✓ 2nd | 0.001381s ✓ 1st | 0.014955s ✓ 6th | 0.001531s ✓ 3rd
1000x1000 | 0.023853s 4th  | 0.036422s ✓ 6th | 0.016408s ✓ 2nd | 0.015504s ✓ 1st | 0.029056s ✓ 5th | 0.017412s ✓ 3rd
2000x2500 | 0.033767s 4th  | 1.643829s ✓ 6th | 0.014560s ✓ 2nd | 0.014478s ✓ 1st | 1.421325s ✓ 5th | 0.022940s ✓ 3rd
5000x5000 | 1.026469s 4th  | 2.122379s ✓ 6th | 0.946314s ✓ 2nd | 0.947657s ✓ 3rd | 1.053784s ✓ 5th | 0.458383s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   501.3927 ms | ✅ | 🥇x1 🥈x3 🥉x5
     2. LAPX LAPJV     :   979.8427 ms | ✅ | 🥈x5 🥉x2 🚩x1 🏳️x1
     3. LAPX LAPJVX    :   980.0842 ms | ✅ | 🥇x7 🥈x1 🥉x1
     4. BASELINE SciPy :  1089.0140 ms | ⭐ | 🥇x1 🚩x7 🥴x1
     5. LAPX LAPJVC    :  2521.4207 ms | ✅ | 🥉x1 🏳️x5 🥴x3
     6. LAPX LAPJV-IFT :  3815.8903 ms | ✅ | 🚩x1 🏳️x3 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉
```

👁️ See more results on various platforms and architectures [here](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml).

</details>
