# Copyright (c) 2025 Ratha SIV | MIT License

from setuptools import Extension, setup, find_packages

LICENSE = "MIT"
DESCRIPTION = "Linear Assignment Problem solver (LAPJV/LAPMOD)."
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

def main_setup():
    import os
    from Cython.Build import cythonize

    # Source directories
    SRC_DIR_JV = os.path.join('src', '_lapjv')
    SRC_DIR_JVC = os.path.join('src', '_lapjvc')

    # Source files for lapjv/lapmod
    lapjvcpp = os.path.join(SRC_DIR_JV, 'lapjv.cpp')
    lapmodcpp = os.path.join(SRC_DIR_JV, 'lapmod.cpp')
    _lapjvpyx = os.path.join(SRC_DIR_JV, '_lapjv.pyx')

    # Source file for lapjvx/lapjvxa
    _lapjvxpyx = os.path.join(SRC_DIR_JV, '_lapjvx.pyx')

    # Source file for lapjvc
    lapjvccpp = os.path.join(SRC_DIR_JVC, 'lapjvc.cpp')

    # Extension for lapjv/lapmod
    ext_jv = Extension(
        name='lap._lapjv',
        sources=[_lapjvpyx, lapjvcpp, lapmodcpp],
        include_dirs=[include_numpy(), SRC_DIR_JV, PACKAGE_PATH],
        language='c++',
        extra_compile_args=['-std=c++17'],
    )

    # Extension for lapjvx/lapjvxa
    ext_jvx = Extension(
        name='lap._lapjvx',
        sources=[_lapjvxpyx, lapjvcpp],
        include_dirs=[include_numpy(), SRC_DIR_JV, PACKAGE_PATH],
        language='c++',
        extra_compile_args=['-std=c++17'],
    )

    # Extension for lapjvc
    ext_jvc = Extension(
        name='lap._lapjvc',
        sources=[lapjvccpp],
        include_dirs=[include_pybind11(), SRC_DIR_JVC, PACKAGE_PATH],
        language='c++',
        extra_compile_args=['-std=c++17'],
    )

    ext_modules = cythonize([ext_jv, ext_jvx]) + [ext_jvc]

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
                  'Jonker-Volgenant Algorithm', 'LAPJV', 'LAPMOD', 
                  'lap', 'lapx', 'lapjvx', 'lapjvxa', 'lapjvc'],
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
    )

if __name__ == "__main__":
    """
    Recommend using :py:mod:`build` to build the package as it does not 
    disrupt your current environment.

    >>> pip install wheel build
    >>> python -m build --sdist
    >>> python -m build --wheel
    """ 
    main_setup()
