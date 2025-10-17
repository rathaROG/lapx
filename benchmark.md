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

As shown in the results below, the new function [`lapjvx()`](https://github.com/rathaROG/lapx#2-the-new-function-lapjvx) (LAPX JVX in the benchmark) consistently produces the same outputs as the baseline SciPy (See the column: Diff From Scipy), and it also outperforms the old [`lapjv()`](https://github.com/rathaROG/lapx#1-the-original-function-lapjv) and even SciPy in most cases. To achieve the best performance with `lapjvx()`, follow [the implementation in the benchmark_tracking.py script](https://github.com/rathaROG/lapx/blob/d736c9f5258905605d3ead5ce77a829698607ad6/.github/test/benchmark_tracking.py#L32).

<details><summary>Show the results:</summary>

```
Microsoft Windows [Version 10.0.26200.6899]
(c) Microsoft Corporation. All rights reserved.

D:\DEV\new\tmp\lapx\.github\test>python benchmark_tracking.py

# Benchmark with threshold (cost_limit) = 1000000.0

      Size |    LAPX JV |   LAPX JVX |   LAPX JVC |      SciPy | Diff From SciPy
--------------------------------------------------------------------------------
   10x10   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | -
   25x25   |     0.00ms |     0.00ms |     0.20ms |     0.00ms | -
   50x50   |     0.20ms |     0.00ms |     0.00ms |     0.00ms | -
  100x150  |     0.40ms |     0.00ms |     0.89ms |     0.08ms | -
  200x200  |     1.20ms |     0.40ms |     0.68ms |     0.61ms | -
  550x500  |    94.35ms |     6.86ms |    22.80ms |     3.84ms | -
 1000x1000 |    35.04ms |    16.17ms |    26.89ms |    24.25ms | -
 5000x5000 |  1396.36ms |   600.57ms |  1219.04ms |   999.22ms | -

# Benchmark with threshold (cost_limit) = 0.1

      Size |    LAPX JV |   LAPX JVX |   LAPX JVC |      SciPy | Diff From SciPy
--------------------------------------------------------------------------------
   10x10   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | JV
   25x25   |     0.00ms |     0.00ms |     0.00ms |     0.20ms | JV
   50x50   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | JV
  100x150  |     0.61ms |     0.20ms |     0.80ms |     0.00ms | -
  200x200  |     1.23ms |     0.40ms |     0.73ms |     0.20ms | -
  550x500  |    60.28ms |     6.83ms |    20.19ms |     3.73ms | -
 1000x1000 |    29.94ms |    15.74ms |    27.60ms |    24.97ms | -
 5000x5000 |  1604.68ms |   747.57ms |  1396.55ms |  1179.87ms | -

# Benchmark with threshold (cost_limit) = 0.5

      Size |    LAPX JV |   LAPX JVX |   LAPX JVC |      SciPy | Diff From SciPy
--------------------------------------------------------------------------------
   10x10   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | JV
   25x25   |     0.00ms |     0.00ms |     0.20ms |     0.00ms | -
   50x50   |     0.00ms |     0.00ms |     0.20ms |     0.20ms | -
  100x150  |     0.60ms |     0.00ms |     0.80ms |     0.43ms | -
  200x200  |     0.69ms |     0.97ms |     0.50ms |     0.76ms | -
  550x500  |    95.65ms |     6.99ms |    20.57ms |     3.72ms | -
 1000x1000 |    36.31ms |    17.40ms |    25.91ms |    23.94ms | -
 5000x5000 |  2059.24ms |   949.81ms |  1319.86ms |  1035.32ms | -

# Benchmark with threshold (cost_limit) = 0.7

      Size |    LAPX JV |   LAPX JVX |   LAPX JVC |      SciPy | Diff From SciPy
--------------------------------------------------------------------------------
   10x10   |     0.00ms |     0.20ms |     0.00ms |     0.00ms | -
   25x25   |     0.20ms |     0.00ms |     0.00ms |     0.00ms | -
   50x50   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | -
  100x150  |     0.30ms |     0.20ms |     0.80ms |     0.40ms | -
  200x200  |     0.80ms |     0.20ms |     1.20ms |     0.83ms | -
  550x500  |    94.60ms |     6.61ms |    18.70ms |     2.90ms | -
 1000x1000 |    40.26ms |    18.22ms |    27.11ms |    24.45ms | -
 5000x5000 |  1714.89ms |   805.16ms |  1217.87ms |  1200.52ms | -

# Benchmark with threshold (cost_limit) = 0.9

      Size |    LAPX JV |   LAPX JVX |   LAPX JVC |      SciPy | Diff From SciPy
--------------------------------------------------------------------------------
   10x10   |     0.00ms |     0.00ms |     1.16ms |     0.00ms | -
   25x25   |     0.00ms |     0.00ms |     0.00ms |     0.00ms | -
   50x50   |     0.00ms |     0.00ms |     0.00ms |     0.20ms | -
  100x150  |     0.80ms |     0.20ms |     0.70ms |     0.00ms | -
  200x200  |     1.12ms |     0.60ms |     0.61ms |     0.80ms | -
  550x500  |    96.03ms |     5.57ms |    24.35ms |     4.16ms | -
 1000x1000 |    43.43ms |    20.97ms |    28.05ms |    23.46ms | -
 5000x5000 |  2023.39ms |   927.44ms |  1183.65ms |  1076.82ms | -

D:\DEV\new\tmp\lapx\.github\test>
```

</details>
