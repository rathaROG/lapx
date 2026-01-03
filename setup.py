# Copyright (c) 2025 Ratha SIV | MIT License

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext  # custom build_ext for high-perf flags

LICENSE = "MIT"
DESCRIPTION = "Linear assignment problem solvers, including single and batch solvers."
LONG_DESCRIPTION = open("README.md", encoding="utf-8").read()

PACKAGE_NAME = "lapx"
PACKAGE_PATH = "lap"

def get_version_string() -> str:
    with open("lap/__init__.py") as version_file:
        for line in version_file.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError('[!] Unable to find version string.')

def include_numpy():
    import numpy as np
    return np.get_include()

def include_pybind11():
    import pybind11
    return pybind11.get_include()

class BuildExt(build_ext):
    """
    Add portable, high-performance compiler/linker flags and allow
    optional opt-ins via env vars:
      - LAPX_BASEOPTS=0  -> disable base optimizations (/O2, -O3, -DNDEBUG, LTO, etc.)
      - LAPX_FASTMATH=1  -> -ffast-math (or /fp:fast)
      - LAPX_NATIVE=1    -> -march=native -mtune=native
      - LAPX_LTO=0       -> disable LTO if needed (only considered when base opts are enabled)
    """
    def has_flag(self, flag):
        import tempfile, os
        with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False) as f:
            f.write("int main(){return 0;}")
            fname = f.name
        try:
            self.compiler.compile([fname], extra_postargs=[flag])
        except Exception:
            try: os.remove(fname)
            except OSError: pass
            return False
        try: os.remove(fname)
        except OSError: pass
        return True

    def build_extensions(self):
        import os, sys

        base_enabled = (os.environ.get('LAPX_BASEOPTS', '1').strip() != '0')
        env_fastmath = (os.environ.get('LAPX_FASTMATH', '').strip() == '1')
        env_native   = (os.environ.get('LAPX_NATIVE',   '').strip() == '1')
        env_lto_on   = (os.environ.get('LAPX_LTO',      '1').strip() == '1')

        print("\n[+] LAPX -> Build options")
        print(f"    - LAPX_BASEOPTS  :  {'Enabled' if base_enabled else 'Disabled'}")
        print(f"    - LAPX_FASTMATH  :  {'Enabled' if env_fastmath else 'Disabled'}")
        print(f"    - LAPX_NATIVE    :  {'Enabled' if env_native else 'Disabled'}")
        print(f"    - LTO LAPX_LTO   :  {'Enabled' if (base_enabled and env_lto_on) else 'Disabled'}\n")

        ctype = self.compiler.compiler_type
        is_msvc = (ctype == 'msvc')

        compile_opts = []
        link_opts = []

        if is_msvc:
            # Base optimizations on MSVC
            if base_enabled:
                compile_opts += ['/O2', '/DNDEBUG']
                # Respect LAPX_LTO on MSVC when base opts are enabled
                if env_lto_on and self.has_flag('/GL'):
                    compile_opts += ['/GL']
                    link_opts += ['/LTCG']
            # Optional fast-math (opt-in)
            if env_fastmath:
                compile_opts += ['/fp:fast']
        else:
            # Base optimizations on GCC/Clang
            if base_enabled:
                compile_opts += ['-O3', '-DNDEBUG']
                if sys.version_info >= (3, 9) and self.has_flag('-fvisibility=hidden'):
                    compile_opts += ['-fvisibility=hidden']
                if self.has_flag('-fno-math-errno'):
                    compile_opts += ['-fno-math-errno']
                # Link-time optimization (prefer ThinLTO when available)
                if env_lto_on:
                    if self.has_flag('-flto=thin'):
                        compile_opts += ['-flto=thin']; link_opts += ['-flto=thin']
                    elif self.has_flag('-flto'):
                        compile_opts += ['-flto']; link_opts += ['-flto']
                # Minor call overhead reduction on Linux/glibc (if supported)
                if sys.platform.startswith('linux') and self.has_flag('-fno-plt'):
                    compile_opts += ['-fno-plt']
            # Optional fast-math (opt-in)
            if env_fastmath and self.has_flag('-ffast-math'):
                compile_opts += ['-ffast-math']
            # Optional native tuning (opt-in; avoid for portable wheels)
            if env_native:
                if self.has_flag('-march=native'):
                    compile_opts += ['-march=native']
                if self.has_flag('-mtune=native'):
                    compile_opts += ['-mtune=native']

        # Apply to all extensions (always)
        for ext in self.extensions:
            prev_cargs = list(getattr(ext, 'extra_compile_args', []) or [])
            prev_largs = list(getattr(ext, 'extra_link_args', []) or [])
            ext.extra_compile_args = prev_cargs + compile_opts
            ext.extra_link_args = prev_largs + link_opts
        
        # Show final compiler/linker args for debugging
        for ext in self.extensions:
            print(f"\n[+] LAPX -> Extension << {ext.name} >>")
            print(f"    - extra_compile_args : {ext.extra_compile_args}")
            print(f"    - extra_link_args    : {ext.extra_link_args}")
            if ext == self.extensions[-1]:
                print()

        super().build_extensions()

def main_setup():
    import os
    import sys
    from Cython.Build import cythonize

    # Source directories
    SRC_DIR_JV = os.path.join('src', '_lapjv')
    SRC_DIR_JVC = os.path.join('src', '_lapjvc')
    SRC_DIR_JVS = os.path.join('src', '_lapjvs')

    # Source files for lapjv/lapmod
    lapjvcpp = os.path.join(SRC_DIR_JV, 'lapjv.cpp')
    lapmodcpp = os.path.join(SRC_DIR_JV, 'lapmod.cpp')
    _lapjvpyx = os.path.join(SRC_DIR_JV, '_lapjv.pyx')

    # Source file for lapjvx/lapjvxa
    _lapjvxpyx = os.path.join(SRC_DIR_JV, '_lapjvx.pyx')

    # Source file for lapjvc
    lapjvccpp = os.path.join(SRC_DIR_JVC, 'lapjvc.cpp')

    # Source file for lapjvs
    lapjvscpp = os.path.join(SRC_DIR_JVS, 'lapjvs.cpp')

    # C++ standard on different platforms
    if sys.platform == "win32":
        # extra_compile_args = ["/std:c++17"]
        extra_compile_args = ["/std:c++latest"]
    else:
        extra_compile_args = ["-std=c++17"]

    # Extension for lapjv/lapmod
    ext_jv = Extension(
        name='lap._lapjv',
        sources=[_lapjvpyx, lapjvcpp, lapmodcpp],
        include_dirs=[include_numpy(), SRC_DIR_JV, PACKAGE_PATH],
        language='c++',
        extra_compile_args=extra_compile_args,
    )

    # Extension for lapjvx/lapjvxa
    ext_jvx = Extension(
        name='lap._lapjvx',
        sources=[_lapjvxpyx, lapjvcpp],
        include_dirs=[include_numpy(), SRC_DIR_JV, PACKAGE_PATH],
        language='c++',
        extra_compile_args=extra_compile_args,
    )

    # Extension for lapjvc
    ext_jvc = Extension(
        name='lap._lapjvc',
        sources=[lapjvccpp],
        include_dirs=[include_pybind11(), SRC_DIR_JVC, PACKAGE_PATH],
        language='c++',
        extra_compile_args=extra_compile_args,
    )

    # Extension for lapjvs
    ext_jvs = Extension(
        name='lap._lapjvs',
        sources=[lapjvscpp],
        include_dirs=[include_numpy(), SRC_DIR_JVS, PACKAGE_PATH],
        language='c++',
        extra_compile_args=extra_compile_args,
    )

    # Safe, high-performance Cython directives
    cython_directives = dict(
        language_level=3,
        boundscheck=False,
        wraparound=False,
        nonecheck=False,
        initializedcheck=False,
        cdivision=True,
        infer_types=True,
        profile=False,
        linetrace=False,
    )

    # Merge all extensions
    ext_modules = cythonize([ext_jv, ext_jvx], compiler_directives=cython_directives) + [ext_jvc, ext_jvs]

    setup(
        name=PACKAGE_NAME,
        version=get_version_string(),
        description=DESCRIPTION,
        license=LICENSE,
        author="Ratha SIV",
        maintainer="rathaROG",
        url="https://github.com/rathaROG/lapx",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        keywords=['Linear Assignment Problem Solver', 'LAP solver',
                  'Jonker-Volgenant Algorithm', 'LAPJV', 'LAPMOD', 'lap',
                  'lapx', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa',
                  'lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch'],
        packages=find_packages(include=[PACKAGE_PATH, f"{PACKAGE_PATH}.*"]),
        include_package_data=True,
        install_requires=['numpy>=1.21.6',],
        python_requires=">=3.7",
        classifiers=['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Education',
                     'Intended Audience :: Science/Research',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Programming Language :: Python :: 3.11',
                     'Programming Language :: Python :: 3.12',
                     'Programming Language :: Python :: 3.13',
                     'Programming Language :: Python :: 3.14',
                     'Topic :: Education',
                     'Topic :: Education :: Testing',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Mathematics',
                     'Topic :: Software Development',
                     'Topic :: Software Development :: Libraries',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: POSIX',
                     'Operating System :: Unix',
                     'Operating System :: MacOS',],
        ext_modules=ext_modules,
        cmdclass={'build_ext': BuildExt},
    )

if __name__ == "__main__":
    """
    Recommend using :py:mod:`build` to build the package as it does not
    disrupt your current environment.

    >>> pip install wheel build
    >>> python -m build --sdist
    >>> python -m build --wheel

    Base optimizations are safe and applied automatically (e.g., optimized 
    build [/O2 on MSVC or -O3 on GCC/Clang], -DNDEBUG, and LTO when supported).

    Extra opt-ins can be enabled via environment variables:
      - LAPX_BASEOPTS=0  -> disables base optimizations entirely
      - LAPX_FASTMATH=1  -> enables fast-math (/fp:fast on MSVC, -ffast-math on GCC/Clang)
      - LAPX_NATIVE=1    -> enables -march=native -mtune=native (GCC/Clang only)
      - LAPX_LTO=0       -> disables LTO if needed (only considered when base opts are enabled)

    For example, to build with fast-math enabled on Linux/macOS:
    >>> LAPX_FASTMATH=1 python -m build --wheel

    For example, to build with fast-math enabled on Windows terminal (CMD):
    >>> set "LAPX_FASTMATH=1" && python -m build --wheel

    Note: Cython compiler directives (boundscheck=False, wraparound=False, cdivision=True, etc.)
    are enabled by default for Cython modules.
    """
    main_setup()
