[![GitHub release](https://img.shields.io/github/release/rathaROG/lapx.svg)](https://github.com/rathaROG/lapx/releases)
[![PyPI version](https://badge.fury.io/py/lapx.svg?v=0.9.1)](https://badge.fury.io/py/lapx)
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

📊 Some benchmark results using `lapx` [v0.9.0](https://github.com/rathaROG/lapx/releases/tag/v0.9.0) (2025/10/31):

<details><summary>🗂️ Batch on my local Windows 11 i9-13900KS (8 p-core + 8 e-core) + python 3.11.9:</summary>

```
Microsoft Windows [Version 10.0.26200.7019]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\lapx_all\tmp\lapx\benchmarks>python benchmark_batch.py

# 10 x (4000x4000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=16.48859572, time=0.67588449s
  CPU lapx-batch-jvs     :  cost=16.48859572, time=0.46411657s
  CPU lapx-batch-jvxa    :  cost=16.48859572, time=0.71385884s
  CPU lapx-batch-jvsa    :  cost=16.48859572, time=0.45670390s
  CPU lapx-batch-jvsa64  :  cost=16.48859572, time=0.70847058s
  CPU lapx-loop-jvx      :  cost=16.48859572, time=3.95986462s
  CPU lapx-loop-jvs      :  cost=16.48859572, time=2.66866994s

# 20 x (3000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=16.65042067, time=0.18923616s
  CPU lapx-batch-jvs     :  cost=16.65042067, time=0.17624354s
  CPU lapx-batch-jvxa    :  cost=16.65042067, time=0.18447852s
  CPU lapx-batch-jvsa    :  cost=16.65042067, time=0.18925667s
  CPU lapx-batch-jvsa64  :  cost=16.65042067, time=0.18949389s
  CPU lapx-loop-jvx      :  cost=16.65042067, time=0.85662770s
  CPU lapx-loop-jvs      :  cost=16.65042067, time=1.05569839s

# 50 x (2000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=82.12386385, time=0.56725645s
  CPU lapx-batch-jvs     :  cost=82.12386385, time=0.37664533s
  CPU lapx-batch-jvxa    :  cost=82.12386385, time=0.57265162s
  CPU lapx-batch-jvsa    :  cost=82.12386385, time=0.37772393s
  CPU lapx-batch-jvsa64  :  cost=82.12386385, time=0.61493921s
  CPU lapx-loop-jvx      :  cost=82.12386385, time=4.46092606s
  CPU lapx-loop-jvs      :  cost=82.12386385, time=3.49988031s

# 100 x (1000x2000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=58.19636934, time=0.18971944s
  CPU lapx-batch-jvs     :  cost=58.19636934, time=0.16700149s
  CPU lapx-batch-jvxa    :  cost=58.19636934, time=0.18943620s
  CPU lapx-batch-jvsa    :  cost=58.19636934, time=0.16706610s
  CPU lapx-batch-jvsa64  :  cost=58.19636934, time=0.25204611s
  CPU lapx-loop-jvx      :  cost=58.19636934, time=1.02838278s
  CPU lapx-loop-jvs      :  cost=58.19636934, time=1.21967244s

# 500 x (1000x1000) | n_threads = 24

  CPU lapx-batch-jvx     :  cost=821.97407482, time=0.59273267s
  CPU lapx-batch-jvs     :  cost=821.97407482, time=0.58274126s
  CPU lapx-batch-jvxa    :  cost=821.97407482, time=0.58346224s
  CPU lapx-batch-jvsa    :  cost=821.97407482, time=0.58098578s
  CPU lapx-batch-jvsa64  :  cost=821.97407482, time=0.61520362s
  CPU lapx-loop-jvx      :  cost=821.97407482, time=6.64442897s
  CPU lapx-loop-jvs      :  cost=821.97407482, time=7.03527546s
```

</details>

<details><summary>📄 Single-matrix on ubuntu-latest + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18961613065/job/54149890164

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.64 x slower 
 * lapjv : ✅ Passed 🐌 5.53 x slower 
 * lapjvx : ✅ Passed 🐌 2.68 x slower 
 * lapjvxa : ✅ Passed 🐌 1.81 x slower 
 * lapjvs : ✅ Passed 🐌 3.56 x slower 
 * lapjvsa : ✅ Passed 🐌 3.36 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00001024s
   2. lapjvc  	: 0.00001677s
   3. lapjvxa  	: 0.00001853s
   4. lapjvx  	: 0.00002740s
   5. lapjvsa  	: 0.00003439s
   6. lapjvs  	: 0.00003648s
   7. lapjv  	: 0.00005660s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.03 x slower 
 * lapjv : ✅ Passed 🐌 5.72 x slower 
 * lapjvx : ✅ Passed 🐌 2.28 x slower 
 * lapjvxa : ✅ Passed 🐌 1.75 x slower 
 * lapjvs : ✅ Passed 🐌 2.7 x slower 
 * lapjvsa : ✅ Passed 🐌 1.04 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000664s
   2. lapjvsa  	: 0.00000690s
   3. lapjvxa  	: 0.00001165s
   4. lapjvc  	: 0.00001346s
   5. lapjvx  	: 0.00001517s
   6. lapjvs  	: 0.00001796s
   7. lapjv  	: 0.00003800s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.3 x slower 
 * lapjv : ✅ Passed 🐌 9.53 x slower 
 * lapjvx : ✅ Passed 🐌 3.62 x slower 
 * lapjvxa : ✅ Passed 🐌 3.04 x slower 
 * lapjvs : ✅ Passed 🐌 4.63 x slower 
 * lapjvsa : ✅ Passed 🐌 5.32 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000537s
   2. lapjvc  	: 0.00001233s
   3. lapjvxa  	: 0.00001631s
   4. lapjvx  	: 0.00001947s
   5. lapjvs  	: 0.00002489s
   6. lapjvsa  	: 0.00002857s
   7. lapjv  	: 0.00005116s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.94 x slower 
 * lapjv : ✅ Passed 🐌 1.34 x slower 
 * lapjvx : ✅ Passed 🏆 1.15 x faster 
 * lapjvxa : ✅ Passed 🏆 1.41 x faster 
 * lapjvs : ✅ Passed 🐌 1.98 x slower 
 * lapjvsa : ✅ Passed 🏆 1.13 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00003351s
   2. lapjvx  	: 0.00004110s
   3. lapjvsa  	: 0.00004164s
   4. scipy ⭐ 	: 0.00004721s
   5. lapjv  	: 0.00006310s
   6. lapjvc  	: 0.00009150s
   7. lapjvs  	: 0.00009357s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.43 x faster 
 * lapjv : ✅ Passed 🏆 1.44 x faster 
 * lapjvx : ✅ Passed 🏆 2.25 x faster 
 * lapjvxa : ✅ Passed 🏆 2.94 x faster 
 * lapjvs : ✅ Passed 🏆 2.27 x faster 
 * lapjvsa : ✅ Passed 🏆 3.99 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00002166s
   2. lapjvxa  	: 0.00002932s
   3. lapjvs  	: 0.00003803s
   4. lapjvx  	: 0.00003831s
   5. lapjv  	: 0.00005988s
   6. lapjvc  	: 0.00006028s
   7. scipy ⭐ 	: 0.00008634s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.22 x slower 
 * lapjv : ✅ Passed 🏆 1.07 x faster 
 * lapjvx : ✅ Passed 🏆 1.54 x faster 
 * lapjvxa : ✅ Passed 🏆 1.88 x faster 
 * lapjvs : ✅ Passed 🏆 1.63 x faster 
 * lapjvsa : ✅ Passed 🏆 1.47 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00004026s
   2. lapjvs  	: 0.00004654s
   3. lapjvx  	: 0.00004924s
   4. lapjvsa  	: 0.00005152s
   5. lapjv  	: 0.00007051s
   6. scipy ⭐ 	: 0.00007566s
   7. lapjvc  	: 0.00009201s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.97 x slower 
 * lapjv : ✅ Passed 🏆 2.02 x faster 
 * lapjvx : ✅ Passed 🏆 2.34 x faster 
 * lapjvxa : ✅ Passed 🏆 3.09 x faster 
 * lapjvs : ✅ Passed 🏆 3.95 x faster 
 * lapjvsa : ✅ Passed 🏆 3.89 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvs  	: 0.00116294s
   2. lapjvsa  	: 0.00117967s
   3. lapjvxa  	: 0.00148459s
   4. lapjvx  	: 0.00196006s
   5. lapjv  	: 0.00227485s
   6. scipy ⭐ 	: 0.00458916s
   7. lapjvc  	: 0.02279758s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.46 x faster 
 * lapjv : ✅ Passed 🏆 1.19 x faster 
 * lapjvx : ✅ Passed 🏆 1.19 x faster 
 * lapjvxa : ✅ Passed 🏆 1.21 x faster 
 * lapjvs : ✅ Passed 🏆 1.58 x faster 
 * lapjvsa : ✅ Passed 🏆 1.6 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00610949s
   2. lapjvs  	: 0.00617076s
   3. lapjvc  	: 0.00669765s
   4. lapjvxa  	: 0.00807378s
   5. lapjvx  	: 0.00817340s
   6. lapjv  	: 0.00822582s
   7. scipy ⭐ 	: 0.00976096s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.66 x slower 
 * lapjv : ✅ Passed 🏆 2.07 x faster 
 * lapjvx : ✅ Passed 🏆 3.44 x faster 
 * lapjvxa : ✅ Passed 🏆 3.42 x faster 
 * lapjvs : ✅ Passed 🏆 4.27 x faster 
 * lapjvsa : ✅ Passed 🏆 4.37 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00128856s
   2. lapjvs  	: 0.00131904s
   3. lapjvx  	: 0.00163978s
   4. lapjvxa  	: 0.00164817s
   5. lapjv  	: 0.00272247s
   6. scipy ⭐ 	: 0.00563737s
   7. lapjvc  	: 0.02625532s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 257.47 x slower 
 * lapjv : ✅ Passed 🏆 1.09 x faster 
 * lapjvx : ✅ Passed 🏆 1.09 x faster 
 * lapjvxa : ✅ Passed 🏆 1.08 x faster 
 * lapjvs : ✅ Passed 🐌 1.11 x slower 
 * lapjvsa : ✅ Passed 🐌 1.1 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.09400308s
   2. lapjv  	: 0.09424586s
   3. lapjvxa  	: 0.09509772s
   4. scipy ⭐ 	: 0.10258777s
   5. lapjvsa  	: 0.11241747s
   6. lapjvs  	: 0.11372150s
   7. lapjvc  	: 26.41295845s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.02 x slower 
 * lapjv : ✅ Passed 🐌 1.62 x slower 
 * lapjvx : ✅ Passed 🐌 1.62 x slower 
 * lapjvxa : ✅ Passed 🐌 1.62 x slower 
 * lapjvs : ✅ Passed 🏆 1.76 x faster 
 * lapjvsa : ✅ Passed 🏆 1.76 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvs  	: 1.34793133s
   2. lapjvsa  	: 1.34966543s
   3. scipy ⭐ 	: 2.37237136s
   4. lapjvc  	: 2.41397720s
   5. lapjvxa  	: 3.84284193s
   6. lapjvx  	: 3.84922083s
   7. lapjv  	: 3.85101395s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 273.6 x slower 
 * lapjv : ✅ Passed 🏆 2.03 x faster 
 * lapjvx : ✅ Passed 🏆 2.04 x faster 
 * lapjvxa : ✅ Passed 🏆 2.05 x faster 
 * lapjvs : ✅ Passed 🏆 1.59 x faster 
 * lapjvsa : ✅ Passed 🏆 1.63 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.19721307s
   2. lapjvx  	: 0.19786040s
   3. lapjv  	: 0.19958704s
   4. lapjvsa  	: 0.24835583s
   5. lapjvs  	: 0.25347052s
   6. scipy ⭐ 	: 0.40418303s
   7. lapjvc  	: 110.58635478s
 ------------------------------- 
```

</details>

<details><summary>📄 Single-matrix on macos-latest (arm) + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18961613065/job/54149890234

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.71 x slower 
 * lapjv : ✅ Passed 🐌 5.14 x slower 
 * lapjvx : ✅ Passed 🐌 2.32 x slower 
 * lapjvxa : ✅ Passed 🐌 1.57 x slower 
 * lapjvs : ✅ Passed 🐌 3.57 x slower 
 * lapjvsa : ✅ Passed 🐌 3.25 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000567s
   2. lapjvxa  	: 0.00000888s
   3. lapjvc  	: 0.00000971s
   4. lapjvx  	: 0.00001317s
   5. lapjvsa  	: 0.00001842s
   6. lapjvs  	: 0.00002025s
   7. lapjv  	: 0.00002913s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.83 x slower 
 * lapjv : ✅ Passed 🐌 4.14 x slower 
 * lapjvx : ✅ Passed 🐌 1.83 x slower 
 * lapjvxa : ✅ Passed 🐌 1.59 x slower 
 * lapjvs : ✅ Passed 🐌 2.01 x slower 
 * lapjvsa : ✅ Passed 🏆 1.32 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00000283s
   2. scipy ⭐ 	: 0.00000375s
   3. lapjvxa  	: 0.00000596s
   4. lapjvc  	: 0.00000687s
   5. lapjvx  	: 0.00000687s
   6. lapjvs  	: 0.00000754s
   7. lapjv  	: 0.00001554s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.66 x slower 
 * lapjv : ✅ Passed 🐌 5.96 x slower 
 * lapjvx : ✅ Passed 🐌 3.03 x slower 
 * lapjvxa : ✅ Passed 🐌 2.6 x slower 
 * lapjvs : ✅ Passed 🐌 3.77 x slower 
 * lapjvsa : ✅ Passed 🐌 4.37 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.00000292s
   2. lapjvxa  	: 0.00000758s
   3. lapjvc  	: 0.00000775s
   4. lapjvx  	: 0.00000883s
   5. lapjvs  	: 0.00001100s
   6. lapjvsa  	: 0.00001275s
   7. lapjv  	: 0.00001738s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.19 x slower 
 * lapjv : ✅ Passed 🏆 1.34 x faster 
 * lapjvx : ✅ Passed 🏆 1.83 x faster 
 * lapjvxa : ✅ Passed 🏆 2.24 x faster 
 * lapjvs : ✅ Passed 🏆 1.74 x faster 
 * lapjvsa : ✅ Passed 🏆 1.22 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00001796s
   2. lapjvx  	: 0.00002200s
   3. lapjvs  	: 0.00002308s
   4. lapjv  	: 0.00002992s
   5. lapjvsa  	: 0.00003283s
   6. scipy ⭐ 	: 0.00004017s
   7. lapjvc  	: 0.00008783s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.16 x faster 
 * lapjv : ✅ Passed 🏆 2.13 x faster 
 * lapjvx : ✅ Passed 🏆 2.69 x faster 
 * lapjvxa : ✅ Passed 🏆 3.29 x faster 
 * lapjvs : ✅ Passed 🏆 2.35 x faster 
 * lapjvsa : ✅ Passed 🏆 3.41 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.00002146s
   2. lapjvxa  	: 0.00002221s
   3. lapjvx  	: 0.00002721s
   4. lapjvs  	: 0.00003108s
   5. lapjv  	: 0.00003437s
   6. lapjvc  	: 0.00006300s
   7. scipy ⭐ 	: 0.00007317s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.31 x slower 
 * lapjv : ✅ Passed 🏆 1.15 x faster 
 * lapjvx : ✅ Passed 🏆 1.54 x faster 
 * lapjvxa : ✅ Passed 🏆 1.89 x faster 
 * lapjvs : ✅ Passed 🏆 1.47 x faster 
 * lapjvsa : ✅ Passed 🏆 1.53 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00001904s
   2. lapjvx  	: 0.00002342s
   3. lapjvsa  	: 0.00002350s
   4. lapjvs  	: 0.00002458s
   5. lapjv  	: 0.00003133s
   6. scipy ⭐ 	: 0.00003604s
   7. lapjvc  	: 0.00008329s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 6.57 x slower 
 * lapjv : ✅ Passed 🏆 3.31 x faster 
 * lapjvx : ✅ Passed 🏆 3.69 x faster 
 * lapjvxa : ✅ Passed 🏆 3.81 x faster 
 * lapjvs : ✅ Passed 🏆 2.86 x faster 
 * lapjvsa : ✅ Passed 🏆 3.05 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00073746s
   2. lapjvx  	: 0.00076150s
   3. lapjv  	: 0.00085017s
   4. lapjvsa  	: 0.00092200s
   5. lapjvs  	: 0.00098329s
   6. scipy ⭐ 	: 0.00281312s
   7. lapjvc  	: 0.01849563s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.37 x slower 
 * lapjv : ✅ Passed 🏆 1.09 x faster 
 * lapjvx : ✅ Passed 🏆 1.11 x faster 
 * lapjvxa : ✅ Passed 🏆 1.18 x faster 
 * lapjvs : ✅ Passed 🏆 1.06 x faster 
 * lapjvsa : ✅ Passed 🏆 1.04 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.00629000s
   2. lapjvx  	: 0.00669658s
   3. lapjv  	: 0.00680446s
   4. lapjvs  	: 0.00702367s
   5. lapjvsa  	: 0.00716958s
   6. scipy ⭐ 	: 0.00744075s
   7. lapjvc  	: 0.01022246s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 5.87 x slower 
 * lapjv : ✅ Passed 🏆 2.05 x faster 
 * lapjvx : ✅ Passed 🏆 3.86 x faster 
 * lapjvxa : ✅ Passed 🏆 2.83 x faster 
 * lapjvs : ✅ Passed 🏆 3.29 x faster 
 * lapjvsa : ✅ Passed 🏆 3.35 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx  	: 0.00102792s
   2. lapjvsa  	: 0.00118358s
   3. lapjvs  	: 0.00120550s
   4. lapjvxa  	: 0.00140042s
   5. lapjv  	: 0.00192958s
   6. scipy ⭐ 	: 0.00396425s
   7. lapjvc  	: 0.02326779s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 349.67 x slower 
 * lapjv : ✅ Passed 🐌 3.52 x slower 
 * lapjvx : ✅ Passed 🐌 1.43 x slower 
 * lapjvxa : ✅ Passed 🐌 1.45 x slower 
 * lapjvs : ✅ Passed 🐌 3.18 x slower 
 * lapjvsa : ✅ Passed 🐌 2.84 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. scipy ⭐ 	: 0.07873675s
   2. lapjvx  	: 0.11293429s
   3. lapjvxa  	: 0.11401713s
   4. lapjvsa  	: 0.22370100s
   5. lapjvs  	: 0.25039458s
   6. lapjv  	: 0.27737229s
   7. lapjvc  	: 27.53160242s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.35 x slower 
 * lapjv : ✅ Passed 🏆 2.36 x faster 
 * lapjvx : ✅ Passed 🏆 2.15 x faster 
 * lapjvxa : ✅ Passed 🏆 2.23 x faster 
 * lapjvs : ✅ Passed 🏆 2.52 x faster 
 * lapjvsa : ✅ Passed 🏆 2.89 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvsa  	: 0.90473763s
   2. lapjvs  	: 1.03581571s
   3. lapjv  	: 1.10758192s
   4. lapjvxa  	: 1.17104621s
   5. lapjvx  	: 1.21566396s
   6. scipy ⭐ 	: 2.61083117s
   7. lapjvc  	: 3.53453567s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 308.42 x slower 
 * lapjv : ✅ Passed 🐌 2.1 x slower 
 * lapjvx : ✅ Passed 🏆 1.32 x faster 
 * lapjvxa : ✅ Passed 🏆 1.87 x faster 
 * lapjvs : ✅ Passed 🐌 2.3 x slower 
 * lapjvsa : ✅ Passed 🐌 1.98 x slower 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa  	: 0.18422821s
   2. lapjvx  	: 0.26109171s
   3. scipy ⭐ 	: 0.34502992s
   4. lapjvsa  	: 0.68365575s
   5. lapjv  	: 0.72371579s
   6. lapjvs  	: 0.79274062s
   7. lapjvc  	: 106.41484879s
 ------------------------------- 
```

</details>

👁️ See newer benchmark results on all platforms [here on GitHub](https://github.com/rathaROG/lapx/actions/workflows/benchmark_single.yaml).

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

This [benchmark_tracking.py](https://github.com/rathaROG/lapx/blob/main/benchmarks/benchmark_tracking.py) is specifically desinged for ***Object Tracking*** application, with [SciPy](https://pypi.org/project/scipy/) as the baseline.

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
lapx @ git+https://github.com/rathaROG/lapx.git@ca0bbee8e319fe005c557d5a2bcce1148d89797c
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
10x10     | 0.000063s 4th  | 0.000057s ✓ 2nd | 0.000063s ✓ 5th | 0.000069s ✓ 6th | 0.000061s ✓ 3rd | 0.000057s ✓ 1st
25x20     | 0.000058s 4th  | 0.000104s ✗ 6th | 0.000062s ✓ 5th | 0.000052s ✓ 2nd | 0.000058s ✓ 3rd | 0.000051s ✓ 1st
50x50     | 0.000083s 4th  | 0.000086s ✗ 5th | 0.000068s ✓ 3rd | 0.000058s ✓ 1st | 0.000103s ✓ 6th | 0.000063s ✓ 2nd
100x150   | 0.000131s 2nd  | 0.000828s ✗ 6th | 0.000132s ✓ 3rd | 0.000144s ✓ 4th | 0.000680s ✓ 5th | 0.000123s ✓ 1st
250x250   | 0.001126s 4th  | 0.001218s ✓ 5th | 0.000557s ✓ 2nd | 0.000537s ✓ 1st | 0.001516s ✓ 6th | 0.000605s ✓ 3rd
550x500   | 0.003531s 4th  | 0.011714s ✓ 5th | 0.001424s ✓ 2nd | 0.001358s ✓ 1st | 0.017545s ✓ 6th | 0.001511s ✓ 3rd
1000x1000 | 0.022934s 4th  | 0.026359s ✓ 5th | 0.010415s ✓ 2nd | 0.010320s ✓ 1st | 0.031669s ✓ 6th | 0.012068s ✓ 3rd
2000x2500 | 0.034198s 4th  | 1.627013s ✓ 6th | 0.013647s ✓ 1st | 0.015660s ✓ 2nd | 1.531048s ✓ 5th | 0.022275s ✓ 3rd
5000x5000 | 1.095034s 3rd  | 2.335637s ✓ 6th | 1.082954s ✓ 2nd | 1.103870s ✓ 4th | 1.140890s ✓ 5th | 0.496765s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   533.5186 ms | ✅ | 🥇x4 🥈x1 🥉x4
     2. LAPX LAPJV     :  1109.3228 ms | ✅ | 🥇x1 🥈x4 🥉x2 🏳️x2
     3. LAPX LAPJVX    :  1132.0674 ms | ✅ | 🥇x4 🥈x2 🚩x2 🥴x1
     4. BASELINE SciPy :  1157.1577 ms | ⭐ | 🥈x1 🥉x1 🚩x7
     5. LAPX LAPJVC    :  2723.5708 ms | ✅ | 🥉x2 🏳️x3 🥴x4
     6. LAPX LAPJV-IFT :  4003.0145 ms | ⚠️ | 🥈x1 🏳️x4 🥴x4
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000048s 2nd  | 0.000055s ✗ 5th | 0.000048s ✓ 3rd | 0.000039s ✓ 1st | 0.000054s ✓ 4th | 0.000055s ✓ 6th
25x20     | 0.000048s 3rd  | 0.000058s ✗ 6th | 0.000055s ✓ 4th | 0.000047s ✓ 2nd | 0.000055s ✓ 5th | 0.000047s ✓ 1st
50x50     | 0.000077s 4th  | 0.000080s ✗ 6th | 0.000057s ✓ 3rd | 0.000048s ✓ 1st | 0.000078s ✓ 5th | 0.000051s ✓ 2nd
100x150   | 0.000112s 3rd  | 0.000635s ✓ 6th | 0.000123s ✓ 4th | 0.000092s ✓ 1st | 0.000588s ✓ 5th | 0.000093s ✓ 2nd
250x250   | 0.000991s 4th  | 0.001352s ✓ 6th | 0.000536s ✓ 1st | 0.000536s ✓ 2nd | 0.001200s ✓ 5th | 0.000591s ✓ 3rd
550x500   | 0.003480s 4th  | 0.010844s ✓ 5th | 0.001426s ✓ 2nd | 0.001311s ✓ 1st | 0.016003s ✓ 6th | 0.001447s ✓ 3rd
1000x1000 | 0.023240s 4th  | 0.026984s ✓ 5th | 0.009923s ✓ 2nd | 0.009682s ✓ 1st | 0.027498s ✓ 6th | 0.011329s ✓ 3rd
2000x2500 | 0.034578s 4th  | 1.563681s ✓ 5th | 0.014135s ✓ 2nd | 0.014121s ✓ 1st | 1.596397s ✓ 6th | 0.022706s ✓ 3rd
5000x5000 | 1.070328s 2nd  | 3.315799s ✓ 6th | 1.622128s ✓ 4th | 1.628149s ✓ 5th | 1.100956s ✓ 3rd | 0.537018s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   573.3374 ms | ✅ | 🥇x2 🥈x2 🥉x4 🥴x1
     2. BASELINE SciPy :  1132.9018 ms | ⭐ | 🥈x2 🥉x2 🚩x5
     3. LAPX LAPJV     :  1648.4320 ms | ✅ | 🥇x1 🥈x3 🥉x2 🚩x3
     4. LAPX LAPJVX    :  1654.0251 ms | ✅ | 🥇x6 🥈x2 🏳️x1
     5. LAPX LAPJVC    :  2742.8296 ms | ✅ | 🥉x1 🚩x1 🏳️x4 🥴x3
     6. LAPX LAPJV-IFT :  4919.4888 ms | ⚠️ | 🏳️x4 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000051s 6th  | 0.000045s ✓ 5th | 0.000045s ✓ 4th | 0.000040s ✓ 2nd | 0.000043s ✓ 3rd | 0.000039s ✓ 1st
25x20     | 0.000043s 1st  | 0.000055s ✓ 6th | 0.000054s ✓ 4th | 0.000046s ✓ 2nd | 0.000054s ✓ 5th | 0.000046s ✓ 3rd
50x50     | 0.000070s 4th  | 0.000076s ✓ 5th | 0.000060s ✓ 3rd | 0.000049s ✓ 1st | 0.000089s ✓ 6th | 0.000054s ✓ 2nd
100x150   | 0.000113s 4th  | 0.000646s ✓ 6th | 0.000103s ✓ 3rd | 0.000095s ✓ 2nd | 0.000616s ✓ 5th | 0.000095s ✓ 1st
250x250   | 0.001064s 4th  | 0.001522s ✓ 6th | 0.000643s ✓ 2nd | 0.000591s ✓ 1st | 0.001448s ✓ 5th | 0.000673s ✓ 3rd
550x500   | 0.003672s 4th  | 0.010797s ✓ 5th | 0.001429s ✓ 2nd | 0.001405s ✓ 1st | 0.015196s ✓ 6th | 0.001497s ✓ 3rd
1000x1000 | 0.019571s 4th  | 0.027457s ✓ 6th | 0.010368s ✓ 1st | 0.011375s ✓ 3rd | 0.024061s ✓ 5th | 0.010495s ✓ 2nd
2000x2500 | 0.038530s 4th  | 1.654156s ✓ 6th | 0.015500s ✓ 2nd | 0.014464s ✓ 1st | 1.561805s ✓ 5th | 0.022967s ✓ 3rd
5000x5000 | 0.969325s 5th  | 1.507703s ✓ 6th | 0.668259s ✓ 3rd | 0.656468s ✓ 2nd | 0.954102s ✓ 4th | 0.475278s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   511.1457 ms | ✅ | 🥇x3 🥈x2 🥉x4
     2. LAPX LAPJVX    :   684.5318 ms | ✅ | 🥇x4 🥈x4 🥉x1
     3. LAPX LAPJV     :   696.4601 ms | ✅ | 🥇x1 🥈x3 🥉x3 🚩x2
     4. BASELINE SciPy :  1032.4388 ms | ⭐ | 🥇x1 🚩x6 🏳️x1 🥴x1
     5. LAPX LAPJVC    :  2557.4136 ms | ✅ | 🥉x1 🚩x1 🏳️x5 🥴x2
     6. LAPX LAPJV-IFT :  3202.4579 ms | ✅ | 🏳️x3 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000049s 6th  | 0.000046s ✓ 4th | 0.000046s ✓ 5th | 0.000038s ✓ 1st | 0.000044s ✓ 3rd | 0.000041s ✓ 2nd
25x20     | 0.000040s 1st  | 0.000055s ✓ 6th | 0.000052s ✓ 5th | 0.000043s ✓ 2nd | 0.000051s ✓ 4th | 0.000045s ✓ 3rd
50x50     | 0.000067s 4th  | 0.000074s ✓ 5th | 0.000058s ✓ 3rd | 0.000053s ✓ 2nd | 0.000081s ✓ 6th | 0.000053s ✓ 1st
100x150   | 0.000117s 2nd  | 0.000752s ✓ 6th | 0.000123s ✓ 3rd | 0.000126s ✓ 4th | 0.000721s ✓ 5th | 0.000098s ✓ 1st
250x250   | 0.001063s 4th  | 0.001545s ✓ 6th | 0.000447s ✓ 2nd | 0.000445s ✓ 1st | 0.001303s ✓ 5th | 0.000477s ✓ 3rd
550x500   | 0.003711s 4th  | 0.011309s ✓ 5th | 0.001524s ✓ 2nd | 0.001460s ✓ 1st | 0.016480s ✓ 6th | 0.001558s ✓ 3rd
1000x1000 | 0.019167s 1st  | 0.053561s ✓ 6th | 0.025616s ✓ 3rd | 0.025778s ✓ 4th | 0.023447s ✓ 2nd | 0.027353s ✓ 5th
2000x2500 | 0.035676s 4th  | 1.579856s ✓ 5th | 0.014502s ✓ 2nd | 0.014438s ✓ 1st | 1.699035s ✓ 6th | 0.023144s ✓ 3rd
5000x5000 | 1.214213s 5th  | 1.230595s ✓ 6th | 0.511229s ✓ 2nd | 0.514490s ✓ 3rd | 1.144982s ✓ 4th | 0.452692s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   505.4603 ms | ✅ | 🥇x3 🥈x1 🥉x4 🏳️x1
     2. LAPX LAPJV     :   553.5970 ms | ✅ | 🥈x4 🥉x3 🏳️x2
     3. LAPX LAPJVX    :   556.8710 ms | ✅ | 🥇x4 🥈x2 🥉x1 🚩x2
     4. BASELINE SciPy :  1274.1026 ms | ⭐ | 🥇x2 🥈x1 🚩x4 🏳️x1 🥴x1
     5. LAPX LAPJV-IFT :  2877.7913 ms | ✅ | 🚩x1 🏳️x3 🥴x5
     6. LAPX LAPJVC    :  2886.1434 ms | ✅ | 🥈x1 🥉x1 🚩x2 🏳️x2 🥴x3
 🎉 ------------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000055s 6th  | 0.000048s ✓ 5th | 0.000046s ✓ 4th | 0.000037s ✓ 1st | 0.000043s ✓ 3rd | 0.000040s ✓ 2nd
25x20     | 0.000043s 1st  | 0.000059s ✓ 6th | 0.000053s ✓ 4th | 0.000045s ✓ 2nd | 0.000055s ✓ 5th | 0.000046s ✓ 3rd
50x50     | 0.000074s 4th  | 0.000080s ✓ 5th | 0.000063s ✓ 3rd | 0.000054s ✓ 1st | 0.000088s ✓ 6th | 0.000058s ✓ 2nd
100x150   | 0.000146s 4th  | 0.000647s ✓ 5th | 0.000107s ✓ 3rd | 0.000095s ✓ 1st | 0.000714s ✓ 6th | 0.000103s ✓ 2nd
250x250   | 0.000964s 4th  | 0.001495s ✓ 6th | 0.000565s ✓ 1st | 0.000603s ✓ 2nd | 0.001220s ✓ 5th | 0.000636s ✓ 3rd
550x500   | 0.003138s 4th  | 0.010879s ✓ 5th | 0.001294s ✓ 1st | 0.001329s ✓ 2nd | 0.016092s ✓ 6th | 0.001405s ✓ 3rd
1000x1000 | 0.020857s 3rd  | 0.042133s ✓ 6th | 0.019502s ✓ 2nd | 0.019448s ✓ 1st | 0.023370s ✓ 5th | 0.021119s ✓ 4th
2000x2500 | 0.032293s 4th  | 1.575432s ✓ 6th | 0.014037s ✓ 1st | 0.014037s ✓ 2nd | 1.482075s ✓ 5th | 0.022823s ✓ 3rd
5000x5000 | 0.974974s 4th  | 1.340142s ✓ 6th | 0.564158s ✓ 2nd | 0.570803s ✓ 3rd | 1.116583s ✓ 5th | 0.442339s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉
     1. LAPX LAPJVS    :   488.5671 ms | ✅ | 🥇x1 🥈x3 🥉x4 🚩x1
     2. LAPX LAPJV     :   599.8239 ms | ✅ | 🥇x3 🥈x2 🥉x2 🚩x2
     3. LAPX LAPJVX    :   606.4511 ms | ✅ | 🥇x4 🥈x4 🥉x1
     4. BASELINE SciPy :  1032.5424 ms | ⭐ | 🥇x1 🥉x1 🚩x6 🥴x1
     5. LAPX LAPJVC    :  2640.2397 ms | ✅ | 🥉x1 🏳️x5 🥴x3
     6. LAPX LAPJV-IFT :  2970.9133 ms | ✅ | 🏳️x4 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉
```

👁️ See more results on various platforms and architectures [here](https://github.com/rathaROG/lapx/actions/workflows/benchmark_tracking.yaml).

</details>
