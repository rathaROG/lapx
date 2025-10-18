# 🏆 Quick Benchmark

`lapx` focuses more on real-world applications, and the [benchmark.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark.py) is **not** 
intended for scientific research or competitive evaluation. Instead, it provides a quick and accessible way for 
you to run benchmark tests on your own machine. Below, you will also find a collection of interesting results 
gathered from various major platforms and architectures.

## 💡 Run the quick benchmark

To see some quick benchmark results for these functions, simply run:

```
pip install "lapx>=0.6.0"
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/.github/test
python benchmark.py
```

Note: [SciPy](https://pypi.org/project/scipy/) is used as the baseline in the benchmark.

### 📊 See some results

Using `lapx` [v0.6.0](https://github.com/rathaROG/lapx/releases/tag/v0.6.0) (2025/10/16):

<details><summary>A quick benchmark on my local Windows AMD64 + Python 3.11:</summary>

```
D:\DEV\new\tmp\lapx\.github\test>python benchmark.py
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.91 x slower
 * lapjv : ✅ Passed 🐌 4.22 x slower
 * lapjvx : ✅ Passed 🐌 1.73 x slower
 * lapjvxa : ✅ Passed 🏆 1.48 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00000870s
   2. scipy     : 0.00001290s
   3. lapjvx    : 0.00002230s
   4. lapjvc    : 0.00003750s
   5. lapjv     : 0.00005450s
 -------------------------------

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.24 x slower
 * lapjv : ✅ Passed 🏆 1.27 x faster
 * lapjvx : ✅ Passed 🐌 1.08 x slower
 * lapjvxa : ✅ Passed 🏆 2.2 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00000540s
   2. lapjv     : 0.00000940s
   3. scipy     : 0.00001190s
   4. lapjvx    : 0.00001280s
   5. lapjvc    : 0.00001480s
 -------------------------------

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.94 x slower
 * lapjv : ✅ Passed 🐌 2.79 x slower
 * lapjvx : ✅ Passed 🐌 1.94 x slower
 * lapjvxa : ✅ Passed 🐌 1.23 x slower

 ----- 🎉 SPEED RANKING 🎉 -----
   1. scipy     : 0.00000520s
   2. lapjvxa   : 0.00000640s
   3. lapjvc    : 0.00001010s
   4. lapjvx    : 0.00001010s
   5. lapjv     : 0.00001450s
 -------------------------------

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.73 x slower
 * lapjv : ✅ Passed 🐌 1.14 x slower
 * lapjvx : ✅ Passed 🏆 1.37 x faster
 * lapjvxa : ✅ Passed 🏆 2.68 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00001480s
   2. lapjvx    : 0.00002900s
   3. scipy     : 0.00003960s
   4. lapjv     : 0.00004500s
   5. lapjvc    : 0.00006860s
 -------------------------------

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.13 x slower
 * lapjv : ✅ Passed 🏆 1.21 x faster
 * lapjvx : ✅ Passed 🏆 1.15 x faster
 * lapjvxa : ✅ Passed 🏆 1.83 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00003420s
   2. lapjv     : 0.00005180s
   3. lapjvx    : 0.00005460s
   4. scipy     : 0.00006260s
   5. lapjvc    : 0.00007080s
 -------------------------------

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.77 x slower
 * lapjv : ✅ Passed 🐌 1.18 x slower
 * lapjvx : ✅ Passed 🏆 1.32 x faster
 * lapjvxa : ✅ Passed 🏆 2.59 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00001860s
   2. lapjvx    : 0.00003650s
   3. scipy     : 0.00004810s
   4. lapjv     : 0.00005670s
   5. lapjvc    : 0.00008530s
 -------------------------------

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.87 x slower
 * lapjv : ✅ Passed 🏆 2.66 x faster
 * lapjvx : ✅ Passed 🏆 2.91 x faster
 * lapjvxa : ✅ Passed 🏆 3.25 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00070970s
   2. lapjvx    : 0.00079410s
   3. lapjv     : 0.00086630s
   4. scipy     : 0.00230730s
   5. lapjvc    : 0.01124800s
 -------------------------------

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.3 x slower
 * lapjv : ✅ Passed 🏆 3.18 x faster
 * lapjvx : ✅ Passed 🏆 3.76 x faster
 * lapjvxa : ✅ Passed 🏆 4.12 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00116460s
   2. lapjvx    : 0.00127410s
   3. lapjv     : 0.00150640s
   4. scipy     : 0.00479300s
   5. lapjvc    : 0.00623980s
 -------------------------------

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.73 x slower
 * lapjv : ✅ Passed 🏆 2.63 x faster
 * lapjvx : ✅ Passed 🏆 2.79 x faster
 * lapjvxa : ✅ Passed 🏆 3.11 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.00092210s
   2. lapjvx    : 0.00102750s
   3. lapjv     : 0.00109070s
   4. scipy     : 0.00286380s
   5. lapjvc    : 0.01354680s
 -------------------------------

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 188.14 x slower
 * lapjv : ✅ Passed 🐌 1.03 x slower
 * lapjvx : ✅ Passed 🐌 1.19 x slower
 * lapjvxa : ✅ Passed 🐌 1.05 x slower

 ----- 🎉 SPEED RANKING 🎉 -----
   1. scipy     : 0.05701800s
   2. lapjv     : 0.05896500s
   3. lapjvxa   : 0.05976270s
   4. lapjvx    : 0.06800490s
   5. lapjvc    : 10.72719050s
 -------------------------------

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.1 x slower
 * lapjv : ✅ Passed 🏆 1.35 x faster
 * lapjvx : ✅ Passed 🏆 1.36 x faster
 * lapjvxa : ✅ Passed 🏆 1.44 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.76239620s
   2. lapjvx    : 0.80476540s
   3. lapjv     : 0.81221330s
   4. scipy     : 1.09645880s
   5. lapjvc    : 1.20319810s
 -------------------------------

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 218.31 x slower
 * lapjv : ✅ Passed 🏆 1.41 x faster
 * lapjvx : ✅ Passed 🏆 1.49 x faster
 * lapjvxa : ✅ Passed 🏆 1.6 x faster

 ----- 🎉 SPEED RANKING 🎉 -----
   1. lapjvxa   : 0.12820320s
   2. lapjvx    : 0.13753590s
   3. lapjv     : 0.14516780s
   4. scipy     : 0.20494090s
   5. lapjvc    : 44.73986530s
 -------------------------------
```

</details>

<details><summary>A quick benchmark on GitHub ubuntu-24.04-arm + Python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18569524446/job/52939508934

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.37 x slower 
 * lapjv : ✅ Passed 🐌 2.69 x slower 
 * lapjvx : ✅ Passed 🐌 1.13 x slower 
 * lapjvxa : ✅ Passed 🏆 1.71 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00001602s
   2. scipy 	: 0.00002745s
   3. lapjvx 	: 0.00003089s
   4. lapjvc 	: 0.00006492s
   5. lapjv 	: 0.00007387s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.83 x slower 
 * lapjv : ✅ Passed 🐌 1.17 x slower 
 * lapjvx : ✅ Passed 🐌 1.45 x slower 
 * lapjvxa : ✅ Passed 🏆 1.14 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00000748s
   2. scipy 	: 0.00000850s
   3. lapjv 	: 0.00000993s
   4. lapjvx 	: 0.00001229s
   5. lapjvc 	: 0.00001552s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 2.64 x faster 
 * lapjv : ✅ Passed 🏆 1.43 x faster 
 * lapjvx : ✅ Passed 🏆 2.13 x faster 
   2. lapjvx 	: 0.00125891s
   3. lapjv 	: 0.00136634s
   4. scipy 	: 0.00408691s
   5. lapjvc 	: 0.01745379s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.36 x slower 
 * lapjv : ✅ Passed 🐌 1.0 x slower 
 * lapjvx : ✅ Passed 🏆 1.25 x faster 
 * lapjvxa : ✅ Passed 🏆 2.7 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00001934s
   2. lapjvx 	: 0.00004170s
   3. scipy 	: 0.00005215s
   4. lapjv 	: 0.00005229s
   5. lapjvc 	: 0.00007079s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.14 x faster 
 * lapjv : ✅ Passed 🏆 1.59 x faster 
 * lapjvx : ✅ Passed 🏆 1.64 x faster 
 * lapjvxa : ✅ Passed 🏆 4.01 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00001652s
   2. lapjvx 	: 0.00004044s
   3. lapjv 	: 0.00004173s
   4. lapjvc 	: 0.00005790s
   5. scipy 	: 0.00006618s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.57 x slower 
 * lapjv : ✅ Passed 🏆 1.09 x faster 
 * lapjvx : ✅ Passed 🏆 1.36 x faster 
 * lapjvxa : ✅ Passed 🏆 2.7 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00002514s
   2. lapjvx 	: 0.00004973s
   3. lapjv 	: 0.00006224s
   4. scipy 	: 0.00006787s
   5. lapjvc 	: 0.00010661s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.44 x slower 
 * lapjv : ✅ Passed 🏆 1.74 x faster 
 * lapjvx : ✅ Passed 🏆 2.32 x faster 
 * lapjvxa : ✅ Passed 🏆 3.44 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00093354s
   2. lapjvx 	: 0.00138716s
   3. lapjv 	: 0.00184813s
   4. scipy 	: 0.00321414s
   5. lapjvc 	: 0.01426200s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.08 x faster 
 * lapjv : ✅ Passed 🏆 2.13 x faster 
 * lapjvx : ✅ Passed 🏆 2.16 x faster 
 * lapjvxa : ✅ Passed 🏆 2.32 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00286471s
   2. lapjvx 	: 0.00307023s
   3. lapjv 	: 0.00311945s
   4. lapjvc 	: 0.00613955s
   5. scipy 	: 0.00663450s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.27 x slower 
 * lapjv : ✅ Passed 🏆 2.99 x faster 
 * lapjvx : ✅ Passed 🏆 3.25 x faster 
 * lapjvxa : ✅ Passed 🏆 4.14 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00098620s
   2. lapjvx 	: 0.00125891s
   3. lapjv 	: 0.00136634s
   4. scipy 	: 0.00408691s
   5. lapjvc 	: 0.01745379s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 253.72 x slower 
 * lapjv : ✅ Passed 🐌 1.02 x slower 
 * lapjvx : ✅ Passed 🏆 1.03 x faster 
 * lapjvxa : ✅ Passed 🏆 1.04 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.07292434s
   2. lapjvx 	: 0.07376017s
   3. scipy 	: 0.07572614s
   4. lapjv 	: 0.07745444s
   5. lapjvc 	: 19.21297550s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🏆 1.22 x faster 
 * lapjv : ✅ Passed 🏆 1.38 x faster 
 * lapjvx : ✅ Passed 🏆 1.36 x faster 
 * lapjvxa : ✅ Passed 🏆 1.41 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 1.55721226s
   2. lapjv 	: 1.59465879s
   3. lapjvx 	: 1.62343664s
   4. lapjvc 	: 1.80744283s
   5. scipy 	: 2.20289654s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 286.09 x slower 
 * lapjv : ✅ Passed 🏆 1.82 x faster 
 * lapjvx : ✅ Passed 🏆 1.8 x faster 
 * lapjvxa : ✅ Passed 🏆 1.82 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.15763765s
   2. lapjv 	: 0.15809694s
   3. lapjvx 	: 0.16012727s
   4. scipy 	: 0.28752362s
   5. lapjvc 	: 82.25884137s
 ------------------------------- 
```

</details>

<details><summary>A quick benchmark on GitHub macos-latest (arm) + python 3.14:</summary>

https://github.com/rathaROG/lapx/actions/runs/18569524446/job/52939508983

```
-----------------------------------------
Test (4, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 9.17 x slower 
 * lapjv : ✅ Passed 🐌 5.8 x slower 
 * lapjvx : ✅ Passed 🐌 1.78 x slower 
 * lapjvxa : ✅ Passed 🏆 1.88 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00001083s
   2. scipy 	: 0.00002042s
   3. lapjvx 	: 0.00003642s
   4. lapjv 	: 0.00011850s
   5. lapjvc 	: 0.00018725s
 ------------------------------- 

-----------------------------------------
Test (5, 5)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.0 x slower 
 * lapjv : ✅ Passed 🐌 1.01 x slower 
 * lapjvx : ✅ Passed 🐌 1.28 x slower 
 * lapjvxa : ✅ Passed 🏆 1.32 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00000508s
   2. scipy 	: 0.00000671s
   3. lapjv 	: 0.00000679s
   4. lapjvx 	: 0.00000858s
   5. lapjvc 	: 0.00001342s
 ------------------------------- 

-----------------------------------------
Test (5, 6)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.64 x slower 
 * lapjv : ✅ Passed 🐌 2.71 x slower 
 * lapjvx : ✅ Passed 🐌 1.71 x slower 
 * lapjvxa : ✅ Passed 🐌 1.09 x slower 
   3. lapjv 	: 0.00147846s
   4. scipy 	: 0.00379913s
   5. lapjvc 	: 0.01882146s
 ------------------------------- 

-----------------------------------------
Test (45, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 5.88 x slower 
 * lapjv : ✅ Passed 🐌 3.87 x slower 
 * lapjvx : ✅ Passed 🐌 2.25 x slower 
 * lapjvxa : ✅ Passed 🏆 1.4 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00003196s
   2. scipy 	: 0.00004483s
   3. lapjvx 	: 0.00010071s
   4. lapjv 	: 0.00017346s
   5. lapjvc 	: 0.00026346s
 ------------------------------- 

-----------------------------------------
Test (50, 50)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.04 x slower 
 * lapjv : ✅ Passed 🏆 1.85 x faster 
 * lapjvx : ✅ Passed 🏆 1.25 x faster 
 * lapjvxa : ✅ Passed 🏆 2.74 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00002338s
   2. lapjv 	: 0.00003467s
   3. lapjvx 	: 0.00005137s
   4. scipy 	: 0.00006404s
   5. lapjvc 	: 0.00006692s
 ------------------------------- 

-----------------------------------------
Test (50, 55)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 2.15 x slower 
 * lapjv : ✅ Passed 🐌 1.16 x slower 
 * lapjvx : ✅ Passed 🐌 1.7 x slower 
 * lapjvxa : ✅ Passed 🏆 3.02 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00004450s
   2. scipy 	: 0.00013425s
   3. lapjv 	: 0.00015537s
   4. lapjvx 	: 0.00022804s
   5. lapjvc 	: 0.00028850s
 ------------------------------- 

-----------------------------------------
Test (450, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 5.07 x slower 
 * lapjv : ✅ Passed 🏆 3.85 x faster 
 * lapjvx : ✅ Passed 🏆 5.07 x faster 
 * lapjvxa : ✅ Passed 🏆 5.86 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00084317s
   2. lapjvx 	: 0.00097429s
   3. lapjv 	: 0.00128471s
   4. scipy 	: 0.00494200s
   5. lapjvc 	: 0.02504121s
 ------------------------------- 

-----------------------------------------
Test (500, 500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.58 x slower 
 * lapjv : ✅ Passed 🏆 1.57 x faster 
 * lapjvx : ✅ Passed 🏆 2.31 x faster 
 * lapjvxa : ✅ Passed 🏆 2.45 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00306717s
   2. lapjvx 	: 0.00324108s
   3. lapjv 	: 0.00478496s
   4. scipy 	: 0.00750079s
   5. lapjvc 	: 0.01186579s
 ------------------------------- 

-----------------------------------------
Test (500, 550)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 4.95 x slower 
 * lapjv : ✅ Passed 🏆 2.57 x faster 
 * lapjvx : ✅ Passed 🏆 3.09 x faster 
 * lapjvxa : ✅ Passed 🏆 3.8 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.00100012s
   2. lapjvx 	: 0.00122762s
   3. lapjv 	: 0.00147846s
   4. scipy 	: 0.00379913s
   5. lapjvc 	: 0.01882146s
 ------------------------------- 

-----------------------------------------
Test (2500, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 249.66 x slower 
 * lapjv : ✅ Passed 🐌 1.75 x slower 
 * lapjvx : ✅ Passed 🐌 1.44 x slower 
 * lapjvxa : ✅ Passed 🏆 1.17 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.07092317s
   2. scipy 	: 0.08262608s
   3. lapjvx 	: 0.11884879s
   4. lapjv 	: 0.14426917s
   5. lapjvc 	: 20.62802196s
 ------------------------------- 

-----------------------------------------
Test (5000, 5000)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 1.89 x slower 
 * lapjv : ✅ Passed 🏆 1.65 x faster 
 * lapjvx : ✅ Passed 🏆 1.65 x faster 
 * lapjvxa : ✅ Passed 🏆 1.61 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvx 	: 1.10220804s
   2. lapjv 	: 1.10794012s
   3. lapjvxa 	: 1.13026450s
   4. scipy 	: 1.82365146s
   5. lapjvc 	: 3.44077729s
 ------------------------------- 

-----------------------------------------
Test (5000, 7500)
-----------------------------------------
 * lapjvc : ✅ Passed 🐌 342.0 x slower 
 * lapjv : ✅ Passed 🐌 2.16 x slower 
 * lapjvx : ✅ Passed 🐌 1.28 x slower 
 * lapjvxa : ✅ Passed 🏆 1.43 x faster 

 ----- 🎉 SPEED RANKING 🎉 ----- 
   1. lapjvxa 	: 0.21074092s
   2. scipy 	: 0.30162325s
   3. lapjvx 	: 0.38491017s
   4. lapjv 	: 0.65042508s
   5. lapjvc 	: 103.15502925s
 ------------------------------- 
```

</details>

### 🔍 See more results

See more benchmark results on all platforms [here on GitHub](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml).

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

This [benchmark_tracking.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_tracking.py) is specifically desinged for the Object Tracking applications, with [SciPy](https://pypi.org/project/scipy/) as the baseline in the benchmark.

```
pip install "lapx>=0.6.0"
pip install scipy
git clone https://github.com/rathaROG/lapx.git
cd lapx/.github/test
python benchmark_tracking.py
```

As shown in the updated benchmark results below, the new function [`lapjvx()`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) (LAPX LAPJVX in the tables) and the original [`lapjv()`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv) (LAPX LAPJV in the tables) consistently matches the baseline outputs of SciPy's [`linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html), as indicated by “✓” and ✅ in the tables.

In most scenarios, `lapjvx()` and `lapjv()` demonstrate faster performance than the baseline SciPy's `linear_sum_assignment`, and they remain competitive with other LAPX variants such as [`lapjvc`](https://github.com/rathaROG/lapx#4-the-new-function-lapjvc) (LAPX LAPJVC in the tables). When in-function filtering with `cost_limit` is used, `lapjv()` (LAPX LAPJV-IFT in the tables) experiences a significant performance impact and can produce different outputs compared to SciPy's baseline, as indicated by “✗” and ⚠️ in the tables.

To achieve optimal performance of `lapjvx()` or `lapjv()` in object tracking application, follow the implementation in the current [`benchmark_tracking.py`](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_tracking.py) script.

<details><summary>Show the results:</summary>

```
Microsoft Windows [Version 10.0.26200.6899]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\temp\lapx\.github\test>python benchmark_tracking.py

#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

-----------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC
-----------------------------------------------------------------------------------------------------
10x10     | 0.000153s 5th  | 0.000148s ✗ 4th | 0.000056s ✓ 1st | 0.000132s ✓ 3rd | 0.000084s ✓ 2nd
25x20     | 0.000071s 5th  | 0.000064s ✗ 4th | 0.000057s ✓ 2nd | 0.000057s ✓ 1st | 0.000061s ✓ 3rd
50x50     | 0.000159s 5th  | 0.000106s ✗ 3rd | 0.000075s ✓ 1st | 0.000082s ✓ 2nd | 0.000109s ✓ 4th
100x150   | 0.000190s 3rd  | 0.000574s ✗ 4th | 0.000132s ✓ 1st | 0.000149s ✓ 2nd | 0.000747s ✓ 5th
250x250   | 0.001269s 4th  | 0.001361s ✗ 5th | 0.000542s ✓ 2nd | 0.000519s ✓ 1st | 0.001181s ✓ 3rd
550x500   | 0.003452s 1st  | 0.028483s ✓ 5th | 0.006140s ✓ 3rd | 0.005663s ✓ 2nd | 0.021576s ✓ 4th
1000x1000 | 0.024557s 4th  | 0.023403s ✓ 3rd | 0.008724s ✓ 1st | 0.013036s ✓ 2nd | 0.026147s ✓ 5th
2000x2500 | 0.037717s 3rd  | 1.823954s ✓ 5th | 0.016659s ✓ 2nd | 0.016489s ✓ 1st | 1.580175s ✓ 4th
5000x5000 | 1.047033s 3rd  | 1.628817s ✓ 5th | 0.736356s ✓ 1st | 0.766828s ✓ 2nd | 1.349702s ✓ 4th
-----------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉
     1. LAPX LAPJV     :   768.7409 ms | ✅ | 🥇x5 🥈x3 🥉x1
     2. LAPX LAPJVX    :   802.9538 ms | ✅ | 🥇x3 🥈x5 🥉x1
     3. BASELINE SciPy :  1114.6007 ms | ⭐ | 🥇x1 🥉x3 🚩x2 🏳️x3
     4. LAPX LAPJVC    :  2979.7809 ms | ✅ | 🥈x1 🥉x2 🚩x4 🏳️x2
     5. LAPX LAPJV-IFT :  3506.9110 ms | ⚠️ | 🥉x2 🚩x3 🏳️x4
 🎉 ------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC
-----------------------------------------------------------------------------------------------------
10x10     | 0.000116s 5th  | 0.000042s ✓ 1st | 0.000048s ✓ 3rd | 0.000045s ✓ 2nd | 0.000060s ✓ 4th
25x20     | 0.000052s 1st  | 0.000056s ✗ 3rd | 0.000056s ✓ 4th | 0.000054s ✓ 2nd | 0.000062s ✓ 5th
50x50     | 0.000105s 5th  | 0.000104s ✗ 4th | 0.000070s ✓ 1st | 0.000072s ✓ 2nd | 0.000091s ✓ 3rd
100x150   | 0.000169s 3rd  | 0.000882s ✓ 5th | 0.000168s ✓ 1st | 0.000168s ✓ 2nd | 0.000690s ✓ 4th
250x250   | 0.001306s 1st  | 0.007618s ✓ 5th | 0.002725s ✓ 3rd | 0.002842s ✓ 4th | 0.001719s ✓ 2nd
550x500   | 0.003593s 1st  | 0.054599s ✓ 5th | 0.006124s ✓ 2nd | 0.006191s ✓ 3rd | 0.023443s ✓ 4th
1000x1000 | 0.026108s 3rd  | 0.029221s ✓ 4th | 0.010913s ✓ 1st | 0.011607s ✓ 2nd | 0.031362s ✓ 5th
2000x2500 | 0.041879s 3rd  | 1.971637s ✓ 5th | 0.016502s ✓ 1st | 0.017959s ✓ 2nd | 1.622495s ✓ 4th
5000x5000 | 1.197406s 3rd  | 1.463887s ✓ 5th | 0.642493s ✓ 2nd | 0.638527s ✓ 1st | 1.317815s ✓ 4th
-----------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉
     1. LAPX LAPJVX    :   677.4637 ms | ✅ | 🥇x1 🥈x6 🥉x1 🚩x1
     2. LAPX LAPJV     :   679.1001 ms | ✅ | 🥇x4 🥈x2 🥉x2 🚩x1
     3. BASELINE SciPy :  1270.7361 ms | ⭐ | 🥇x3 🥉x4 🏳️x2
     4. LAPX LAPJVC    :  2997.7366 ms | ✅ | 🥈x1 🥉x1 🚩x5 🏳️x2
     5. LAPX LAPJV-IFT :  3528.0464 ms | ⚠️ | 🥇x1 🥉x1 🚩x2 🏳️x5
 🎉 ------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC
-----------------------------------------------------------------------------------------------------
10x10     | 0.000118s 5th  | 0.000049s ✓ 3rd | 0.000047s ✓ 2nd | 0.000045s ✓ 1st | 0.000058s ✓ 4th
25x20     | 0.000054s 2nd  | 0.000064s ✓ 5th | 0.000058s ✓ 3rd | 0.000054s ✓ 1st | 0.000061s ✓ 4th
50x50     | 0.000092s 3rd  | 0.000101s ✓ 4th | 0.000081s ✓ 2nd | 0.000078s ✓ 1st | 0.000102s ✓ 5th
100x150   | 0.000195s 3rd  | 0.000710s ✓ 5th | 0.000157s ✓ 2nd | 0.000147s ✓ 1st | 0.000647s ✓ 4th
250x250   | 0.001387s 4th  | 0.001640s ✓ 5th | 0.000840s ✓ 2nd | 0.000802s ✓ 1st | 0.001287s ✓ 3rd
550x500   | 0.004195s 1st  | 0.095603s ✓ 5th | 0.006292s ✓ 3rd | 0.006094s ✓ 2nd | 0.022542s ✓ 4th
1000x1000 | 0.024699s 3rd  | 0.037791s ✓ 5th | 0.017332s ✓ 1st | 0.017360s ✓ 2nd | 0.030512s ✓ 4th
2000x2500 | 0.038131s 3rd  | 1.946517s ✓ 5th | 0.016853s ✓ 2nd | 0.016679s ✓ 1st | 1.694409s ✓ 4th
5000x5000 | 1.132641s 3rd  | 1.679415s ✓ 5th | 0.771842s ✓ 2nd | 0.724689s ✓ 1st | 1.162723s ✓ 4th
-----------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉
     1. LAPX LAPJVX    :   765.9472 ms | ✅ | 🥇x7 🥈x2
     2. LAPX LAPJV     :   813.5027 ms | ✅ | 🥇x1 🥈x6 🥉x2
     3. BASELINE SciPy :  1201.5123 ms | ⭐ | 🥇x1 🥈x1 🥉x5 🚩x1 🏳️x1
     4. LAPX LAPJVC    :  2912.3413 ms | ✅ | 🥉x1 🚩x7 🏳️x1
     5. LAPX LAPJV-IFT :  3761.8895 ms | ✅ | 🥉x1 🚩x1 🏳️x7
 🎉 ------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC
-----------------------------------------------------------------------------------------------------
10x10     | 0.000121s 5th  | 0.000046s ✓ 1st | 0.000051s ✓ 3rd | 0.000049s ✓ 2nd | 0.000060s ✓ 4th
25x20     | 0.000055s 1st  | 0.000073s ✓ 5th | 0.000058s ✓ 3rd | 0.000058s ✓ 2nd | 0.000072s ✓ 4th
50x50     | 0.000104s 4th  | 0.000097s ✓ 3rd | 0.000076s ✓ 1st | 0.000088s ✓ 2nd | 0.000109s ✓ 5th
100x150   | 0.000190s 3rd  | 0.000723s ✓ 5th | 0.000174s ✓ 2nd | 0.000153s ✓ 1st | 0.000708s ✓ 4th
250x250   | 0.001418s 4th  | 0.001791s ✓ 5th | 0.000917s ✓ 2nd | 0.000879s ✓ 1st | 0.001381s ✓ 3rd
550x500   | 0.004009s 1st  | 0.094516s ✓ 5th | 0.006915s ✓ 2nd | 0.007350s ✓ 3rd | 0.025237s ✓ 4th
1000x1000 | 0.022408s 2nd  | 0.046482s ✓ 5th | 0.022091s ✓ 1st | 0.023886s ✓ 3rd | 0.030067s ✓ 4th
2000x2500 | 0.038188s 3rd  | 1.932233s ✓ 5th | 0.017298s ✓ 1st | 0.019071s ✓ 2nd | 1.627810s ✓ 4th
5000x5000 | 1.198616s 3rd  | 1.933270s ✓ 5th | 0.972903s ✓ 2nd | 0.925173s ✓ 1st | 1.355138s ✓ 4th
-----------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉
     1. LAPX LAPJVX    :   976.7065 ms | ✅ | 🥇x3 🥈x4 🥉x2
     2. LAPX LAPJV     :  1020.4816 ms | ✅ | 🥇x3 🥈x4 🥉x2
     3. BASELINE SciPy :  1265.1097 ms | ⭐ | 🥇x2 🥈x1 🥉x3 🚩x2 🏳️x1
     4. LAPX LAPJVC    :  3040.5820 ms | ✅ | 🥉x1 🚩x7 🏳️x1
     5. LAPX LAPJV-IFT :  4009.2317 ms | ✅ | 🥇x1 🥉x1 🏳️x7
 🎉 ------------------------------------------------------------------- 🎉


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC
-----------------------------------------------------------------------------------------------------
10x10     | 0.000121s 5th  | 0.000048s ✓ 1st | 0.000050s ✓ 3rd | 0.000049s ✓ 2nd | 0.000062s ✓ 4th
25x20     | 0.000058s 1st  | 0.000086s ✓ 5th | 0.000063s ✓ 3rd | 0.000060s ✓ 2nd | 0.000072s ✓ 4th
50x50     | 0.000102s 3rd  | 0.000120s ✓ 5th | 0.000085s ✓ 1st | 0.000088s ✓ 2nd | 0.000111s ✓ 4th
100x150   | 0.000187s 3rd  | 0.000713s ✓ 4th | 0.000183s ✓ 2nd | 0.000154s ✓ 1st | 0.000719s ✓ 5th
250x250   | 0.001286s 4th  | 0.001058s ✓ 3rd | 0.000481s ✓ 2nd | 0.000435s ✓ 1st | 0.001345s ✓ 5th
550x500   | 0.004404s 1st  | 0.098839s ✓ 5th | 0.007206s ✓ 3rd | 0.006994s ✓ 2nd | 0.022169s ✓ 4th
1000x1000 | 0.025491s 3rd  | 0.028937s ✓ 4th | 0.013111s ✓ 1st | 0.013985s ✓ 2nd | 0.030395s ✓ 5th
2000x2500 | 0.039780s 3rd  | 1.999674s ✓ 5th | 0.018199s ✓ 1st | 0.020531s ✓ 2nd | 1.556668s ✓ 4th
5000x5000 | 1.142951s 4th  | 1.586818s ✓ 5th | 0.720062s ✓ 1st | 0.723589s ✓ 2nd | 1.141216s ✓ 3rd
-----------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ------------------------  OVERALL RANKING  ------------------------ 🎉
     1. LAPX LAPJV     :   759.4403 ms | ✅ | 🥇x4 🥈x2 🥉x3
     2. LAPX LAPJVX    :   765.8850 ms | ✅ | 🥇x2 🥈x7
     3. BASELINE SciPy :  1214.3801 ms | ⭐ | 🥇x2 🥉x4 🚩x2 🏳️x1
     4. LAPX LAPJVC    :  2752.7570 ms | ✅ | 🥉x1 🚩x5 🏳️x3
     5. LAPX LAPJV-IFT :  3716.2938 ms | ✅ | 🥇x1 🥉x1 🚩x2 🏳️x5
 🎉 ------------------------------------------------------------------- 🎉


D:\DEV\temp\lapx\.github\test>
```

</details>
