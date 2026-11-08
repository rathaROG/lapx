# Installation and build options

For the standard PyPI installation, see the
[README](https://github.com/rathaROG/lapx/blob/main/README.md#-installation).
This guide covers source builds, optional solver families, and compiler settings.

## Other installation options

### Python 3.7 and 3.8 (source builds only):

Python 3.7 and 3.8 no longer receive prebuilt wheels or automated testing.
Source installation remains available with compatible build dependencies and
the required C++ and current Rust toolchains:

```bash
python -m pip install --no-binary=lapx lapx
```

### Install from GitHub (requires C++ and current Rust toolchains):

```bash
python -m pip install git+https://github.com/rathaROG/lapx.git
```

### Build and install (requires C++ and current Rust toolchains):

```bash
git clone https://github.com/rathaROG/lapx.git
cd lapx
python -m pip install .
cd ..
```

Run examples outside the checkout so Python loads the installed package.

## `lapjvr` and `lapjvh` families

Source builds include both families by default. Set `LAPX_BUILD_RUST=0`
to build only the other solvers without a Rust toolchain.

See the [R/H API and build guide](https://github.com/rathaROG/lapx/blob/main/src/_lapjvr/README.md).

## Extra performance

Since [v0.9.1](https://github.com/rathaROG/lapx/releases/tag/v0.9.1), `lapx` enables safe base optimizations by default.
For source builds, environment variables control these optimizations and optional compiler flags. The optional flags might improve performance:

- `LAPX_BASEOPTS=0` disables the base optimization flags that LAPX adds and link-time optimization (LTO).
  Other compiler defaults may still apply. This switch is available since [v0.9.2](https://github.com/rathaROG/lapx/releases/tag/v0.9.2).
- `LAPX_FASTMATH=1` enables fast-math. This option may change numerical results and the treatment of NaN or infinity.
  R/H retains strict floating-point rules.
- `LAPX_NATIVE=1` enables CPU-specific tuning for GCC/Clang and Rust. Do not distribute these builds.
- `LAPX_LTO=0` disables LTO, including inherited LTO defaults.

The build enables LTO by default when the compiler and linker support it.
`LAPX_BASEOPTS=0` does not guarantee an unoptimized or debug build.
Fast-math and native tuning are independent options. Both options are disabled by default.
Keep both options disabled for portable release wheels.

See [setup.py](https://github.com/rathaROG/lapx/blob/main/setup.py) for more details.
