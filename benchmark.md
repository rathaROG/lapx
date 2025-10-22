# 🏆 Quick Benchmark

`lapx` focuses more on real-world applications, and the [benchmark.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark.py) is **not** 
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

See newer benchmark results on all platforms [here on GitHub](https://github.com/rathaROG/lapx/actions/workflows/benchmark.yaml).

## 🕵️‍♂️ Other Benchmarks

### 👣 Object Tracking

This [benchmark_tracking.py](https://github.com/rathaROG/lapx/blob/main/.github/test/benchmark_tracking.py) is specifically desinged for the Object Tracking applications, with [SciPy](https://pypi.org/project/scipy/) as the baseline in the benchmark.

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

👁️ See more results on various platforms and architectures [here](https://github.com/rathaROG/lapx/actions/runs/18668517507).

<details><summary>Show the results:</summary>

```
#################################################################
# Benchmark with threshold (cost_limit) = 0.05
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000270s 6th  | 0.000086s ✗ 1st | 0.000117s ✓ 3rd | 0.000093s ✓ 2nd | 0.000145s ✓ 4th | 0.000156s ✓ 5th
25x20     | 0.000134s 6th  | 0.000096s ✗ 1st | 0.000104s ✓ 4th | 0.000098s ✓ 2nd | 0.000109s ✓ 5th | 0.000103s ✓ 3rd
50x50     | 0.000216s 6th  | 0.000161s ✗ 4th | 0.000130s ✓ 2nd | 0.000135s ✓ 3rd | 0.000163s ✓ 5th | 0.000128s ✓ 1st
100x150   | 0.000314s 4th  | 0.001181s ✓ 6th | 0.000307s ✓ 3rd | 0.000304s ✓ 2nd | 0.001002s ✓ 5th | 0.000292s ✓ 1st
250x250   | 0.001926s 4th  | 0.002400s ✓ 6th | 0.001819s ✓ 3rd | 0.001703s ✓ 2nd | 0.002221s ✓ 5th | 0.001585s ✓ 1st
550x500   | 0.005211s 1st  | 0.046236s ✓ 6th | 0.010141s ✓ 4th | 0.009736s ✓ 3rd | 0.031337s ✓ 5th | 0.009591s ✓ 2nd
1000x1000 | 0.035298s 4th  | 0.062979s ✓ 6th | 0.030774s ✓ 3rd | 0.029720s ✓ 2nd | 0.037911s ✓ 5th | 0.014011s ✓ 1st
2000x2500 | 0.047353s 4th  | 2.537366s ✓ 6th | 0.017684s ✓ 1st | 0.019768s ✓ 2nd | 2.133186s ✓ 5th | 0.023504s ✓ 3rd
5000x5000 | 1.923870s 5th  | 3.216478s ✓ 6th | 1.527883s ✓ 3rd | 1.501829s ✓ 2nd | 1.720995s ✓ 4th | 0.879582s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :   928.9522 ms | ✅ | 🥇x5 🥈x1 🥉x2 🏳️x1
     2. LAPX LAPJVX    :  1563.3861 ms | ✅ | 🥈x7 🥉x2
     3. LAPX LAPJV     :  1588.9597 ms | ✅ | 🥇x1 🥈x1 🥉x5 🚩x2
     4. BASELINE SciPy :  2014.5920 ms | ⭐ | 🥇x1 🚩x4 🏳️x1 🥴x3
     5. LAPX LAPJVC    :  3927.0696 ms | ✅ | 🚩x2 🏳️x7
     6. LAPX LAPJV-IFT :  5866.9837 ms | ⚠️ | 🥇x2 🚩x1 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 0.1
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000181s 6th  | 0.000080s ✗ 1st | 0.000091s ✓ 4th | 0.000083s ✓ 2nd | 0.000101s ✓ 5th | 0.000084s ✓ 3rd
25x20     | 0.000122s 6th  | 0.000092s ✗ 1st | 0.000100s ✓ 2nd | 0.000100s ✓ 3rd | 0.000107s ✓ 5th | 0.000103s ✓ 4th
50x50     | 0.000218s 6th  | 0.000149s ✗ 4th | 0.000133s ✓ 1st | 0.000140s ✓ 2nd | 0.000183s ✓ 5th | 0.000141s ✓ 3rd
100x150   | 0.000350s 4th  | 0.001086s ✓ 5th | 0.000258s ✓ 1st | 0.000279s ✓ 3rd | 0.001142s ✓ 6th | 0.000273s ✓ 2nd
250x250   | 0.001713s 5th  | 0.001953s ✓ 6th | 0.000978s ✓ 2nd | 0.000998s ✓ 3rd | 0.001682s ✓ 4th | 0.000929s ✓ 1st
550x500   | 0.005035s 1st  | 0.113739s ✓ 6th | 0.010219s ✓ 4th | 0.010151s ✓ 3rd | 0.029781s ✓ 5th | 0.010025s ✓ 2nd
1000x1000 | 0.032870s 3rd  | 0.076641s ✓ 6th | 0.037077s ✓ 5th | 0.035340s ✓ 4th | 0.031529s ✓ 1st | 0.031647s ✓ 2nd
2000x2500 | 0.050076s 4th  | 2.552992s ✓ 6th | 0.017056s ✓ 1st | 0.020267s ✓ 2nd | 2.110527s ✓ 5th | 0.022934s ✓ 3rd
5000x5000 | 2.035414s 5th  | 3.376261s ✓ 6th | 1.640862s ✓ 4th | 1.622361s ✓ 3rd | 1.534738s ✓ 2nd | 0.910615s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :   976.7508 ms | ✅ | 🥇x2 🥈x3 🥉x3 🚩x1
     2. LAPX LAPJVX    :  1689.7199 ms | ✅ | 🥈x3 🥉x5 🚩x1
     3. LAPX LAPJV     :  1706.7731 ms | ✅ | 🥇x3 🥈x2 🚩x3 🏳️x1
     4. BASELINE SciPy :  2125.9788 ms | ⭐ | 🥇x1 🥉x1 🚩x2 🏳️x2 🥴x3
     5. LAPX LAPJVC    :  3709.7903 ms | ✅ | 🥇x1 🥈x1 🚩x1 🏳️x5 🥴x1
     6. LAPX LAPJV-IFT :  6122.9942 ms | ⚠️ | 🥇x2 🚩x1 🏳️x1 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 0.5
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000167s 6th  | 0.000119s ✓ 5th | 0.000092s ✓ 2nd | 0.000093s ✓ 3rd | 0.000105s ✓ 4th | 0.000085s ✓ 1st
25x20     | 0.000105s 6th  | 0.000097s ✓ 3rd | 0.000096s ✓ 2nd | 0.000096s ✓ 1st | 0.000102s ✓ 5th | 0.000099s ✓ 4th
50x50     | 0.000192s 5th  | 0.000158s ✓ 3rd | 0.000142s ✓ 1st | 0.000150s ✓ 2nd | 0.000171s ✓ 4th | 0.000193s ✓ 6th
100x150   | 0.000319s 4th  | 0.001089s ✓ 6th | 0.000302s ✓ 3rd | 0.000268s ✓ 1st | 0.001078s ✓ 5th | 0.000271s ✓ 2nd
250x250   | 0.001877s 6th  | 0.001662s ✓ 4th | 0.000832s ✓ 2nd | 0.000866s ✓ 3rd | 0.001686s ✓ 5th | 0.000810s ✓ 1st
550x500   | 0.004962s 1st  | 0.173261s ✓ 6th | 0.010107s ✓ 4th | 0.010075s ✓ 3rd | 0.021147s ✓ 5th | 0.009892s ✓ 2nd
1000x1000 | 0.034665s 5th  | 0.050879s ✓ 6th | 0.024332s ✓ 3rd | 0.023485s ✓ 2nd | 0.030950s ✓ 4th | 0.021152s ✓ 1st
2000x2500 | 0.050928s 4th  | 2.503577s ✓ 6th | 0.017477s ✓ 1st | 0.019962s ✓ 2nd | 2.087273s ✓ 5th | 0.027349s ✓ 3rd
5000x5000 | 2.111693s 5th  | 3.396578s ✓ 6th | 1.693776s ✓ 4th | 1.685035s ✓ 3rd | 1.567221s ✓ 2nd | 1.058214s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :  1118.0646 ms | ✅ | 🥇x4 🥈x2 🥉x1 🚩x1 🥴x1
     2. LAPX LAPJVX    :  1740.0298 ms | ✅ | 🥇x2 🥈x3 🥉x4
     3. LAPX LAPJV     :  1747.1555 ms | ✅ | 🥇x2 🥈x3 🥉x2 🚩x2
     4. BASELINE SciPy :  2204.9078 ms | ⭐ | 🥇x1 🚩x2 🏳️x3 🥴x3
     5. LAPX LAPJVC    :  3709.7338 ms | ✅ | 🥈x1 🚩x3 🏳️x5
     6. LAPX LAPJV-IFT :  6127.4199 ms | ✅ | 🥉x2 🚩x1 🏳️x1 🥴x5
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 1.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000168s 6th  | 0.000087s ✓ 1st | 0.000090s ✓ 2nd | 0.000118s ✓ 5th | 0.000104s ✓ 4th | 0.000092s ✓ 3rd
25x20     | 0.000102s 4th  | 0.000113s ✓ 6th | 0.000099s ✓ 1st | 0.000099s ✓ 2nd | 0.000107s ✓ 5th | 0.000099s ✓ 3rd
50x50     | 0.000181s 4th  | 0.000226s ✓ 6th | 0.000154s ✓ 1st | 0.000162s ✓ 2nd | 0.000164s ✓ 3rd | 0.000210s ✓ 5th
100x150   | 0.000321s 4th  | 0.001070s ✓ 5th | 0.000267s ✓ 2nd | 0.000265s ✓ 1st | 0.001108s ✓ 6th | 0.000267s ✓ 3rd
250x250   | 0.001731s 4th  | 0.003008s ✓ 6th | 0.001673s ✓ 3rd | 0.001625s ✓ 2nd | 0.001995s ✓ 5th | 0.001460s ✓ 1st
550x500   | 0.004940s 1st  | 0.168662s ✓ 6th | 0.009288s ✓ 4th | 0.009245s ✓ 3rd | 0.030654s ✓ 5th | 0.009174s ✓ 2nd
1000x1000 | 0.034701s 5th  | 0.051617s ✓ 6th | 0.024396s ✓ 3rd | 0.023235s ✓ 2nd | 0.033910s ✓ 4th | 0.021512s ✓ 1st
2000x2500 | 0.050450s 4th  | 2.519313s ✓ 6th | 0.017596s ✓ 1st | 0.018210s ✓ 2nd | 2.104154s ✓ 5th | 0.027215s ✓ 3rd
5000x5000 | 2.027199s 5th  | 3.501020s ✓ 6th | 1.753403s ✓ 4th | 1.732642s ✓ 3rd | 1.517909s ✓ 2nd | 0.815372s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :   875.4009 ms | ✅ | 🥇x3 🥈x1 🥉x4 🏳️x1
     2. LAPX LAPJVX    :  1785.6020 ms | ✅ | 🥇x1 🥈x5 🥉x2 🏳️x1
     3. LAPX LAPJV     :  1806.9635 ms | ✅ | 🥇x3 🥈x2 🥉x2 🚩x2
     4. BASELINE SciPy :  2119.7929 ms | ⭐ | 🥇x1 🚩x5 🏳️x2 🥴x1
     5. LAPX LAPJVC    :  3690.1060 ms | ✅ | 🥈x1 🥉x1 🚩x2 🏳️x4 🥴x1
     6. LAPX LAPJV-IFT :  6245.1169 ms | ✅ | 🥇x1 🏳️x1 🥴x7
 🎉 ------------------------------------------------------------------------- 🎉 


#################################################################
# Benchmark with threshold (cost_limit) = 1000000000.0
#################################################################

-----------------------------------------------------------------------------------------------------------------------
Size      | BASELINE SciPy | LAPX LAPJV-IFT  | LAPX LAPJV      | LAPX LAPJVX     | LAPX LAPJVC     | LAPX LAPJVS    
-----------------------------------------------------------------------------------------------------------------------
10x10     | 0.000170s 6th  | 0.000079s ✓ 1st | 0.000092s ✓ 4th | 0.000085s ✓ 3rd | 0.000108s ✓ 5th | 0.000084s ✓ 2nd
25x20     | 0.000120s 5th  | 0.000144s ✓ 6th | 0.000101s ✓ 1st | 0.000102s ✓ 3rd | 0.000116s ✓ 4th | 0.000101s ✓ 2nd
50x50     | 0.000185s 6th  | 0.000139s ✓ 4th | 0.000127s ✓ 1st | 0.000135s ✓ 3rd | 0.000158s ✓ 5th | 0.000135s ✓ 2nd
100x150   | 0.000337s 4th  | 0.001089s ✓ 6th | 0.000264s ✓ 1st | 0.000296s ✓ 3rd | 0.001083s ✓ 5th | 0.000276s ✓ 2nd
250x250   | 0.001832s 6th  | 0.001699s ✓ 5th | 0.000847s ✓ 2nd | 0.000866s ✓ 3rd | 0.001471s ✓ 4th | 0.000813s ✓ 1st
550x500   | 0.005429s 1st  | 0.175252s ✓ 6th | 0.010315s ✓ 4th | 0.010249s ✓ 2nd | 0.032756s ✓ 5th | 0.010292s ✓ 3rd
1000x1000 | 0.040797s 5th  | 0.052160s ✓ 6th | 0.025452s ✓ 3rd | 0.024602s ✓ 2nd | 0.036510s ✓ 4th | 0.021898s ✓ 1st
2000x2500 | 0.048694s 4th  | 2.440901s ✓ 6th | 0.016812s ✓ 1st | 0.018195s ✓ 2nd | 2.064631s ✓ 5th | 0.028164s ✓ 3rd
5000x5000 | 2.152508s 5th  | 3.529325s ✓ 6th | 1.664839s ✓ 4th | 1.645120s ✓ 3rd | 1.626812s ✓ 2nd | 0.897383s ✓ 1st
-----------------------------------------------------------------------------------------------------------------------

Note: LAPJV-IFT uses in-function filtering lap.lapjv(cost_limit=thresh).

 🎉 ---------------------------  OVERALL RANKING  --------------------------- 🎉 
     1. LAPX LAPJVS    :   959.1463 ms | ✅ | 🥇x3 🥈x4 🥉x2
     2. LAPX LAPJVX    :  1699.6506 ms | ✅ | 🥈x3 🥉x6
     3. LAPX LAPJV     :  1718.8494 ms | ✅ | 🥇x4 🥈x1 🥉x1 🚩x3
     4. BASELINE SciPy :  2250.0724 ms | ⭐ | 🥇x1 🚩x2 🏳️x3 🥴x3
     5. LAPX LAPJVC    :  3763.6443 ms | ✅ | 🥈x1 🚩x3 🏳️x5
     6. LAPX LAPJV-IFT :  6200.7878 ms | ✅ | 🥇x1 🚩x1 🏳️x1 🥴x6
 🎉 ------------------------------------------------------------------------- 🎉 
```

</details>
