# Copyright (c) 2026 Ratha SIV | MIT License

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext  # custom build_ext for high-perf flags
from setuptools.command.build import build
from setuptools.command.build_py import build_py
from setuptools.command.editable_wheel import editable_wheel

LICENSE = "MIT"
DESCRIPTION = "Linear assignment problem solvers, including single and batch solvers."
LONG_DESCRIPTION = open("README.md", encoding="utf-8").read()

PACKAGE_NAME = "lapx"
PACKAGE_PATH = "lap"

def get_version_string() -> str:
    with open("lap/__init__.py", encoding="utf-8") as version_file:
        for line in version_file.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError('[!] Unable to find version string.')

def include_numpy():
    import numpy as np
    return np.get_include()

def include_pybind11():
    import pybind11  # type: ignore
    return pybind11.get_include()


def build_rust_enabled():
    """Build both R/H families by default; allow an explicit legacy-only build."""
    import os
    value = os.environ.get('LAPX_BUILD_RUST', '1').strip()
    if value not in ('0', '1'):
        raise RuntimeError('LAPX_BUILD_RUST must be 0 or 1')
    return value == '1'


def has_rust_extension(distribution):
    return any(ext.name == 'lap._lapjv_rh' for ext in distribution.ext_modules or [])


def legacy_initializer(content):
    """Omit native R/H declarations from the legacy wheel's initializer."""
    import ast

    def declarations(source):
        tree = ast.parse(source)
        values = {target.id: node.value for node in tree.body if isinstance(node, ast.Assign)
                  for target in node.targets if isinstance(target, ast.Name)}
        exports_node, public_node = values['_exports'], values['__all__']
        if not isinstance(exports_node, ast.Dict) or not isinstance(public_node, ast.List):
            raise RuntimeError('Expected a literal _exports dictionary and __all__ list in lap/__init__.py')
        return tree, exports_node, public_node

    tree, exports_node, public_node = declarations(content)
    exports = ast.literal_eval(exports_node)
    public = ast.literal_eval(public_node)
    omitted = {name for name, (module, _) in exports.items() if module == 'lap._lapjv_rh'}
    lines = {node.lineno for node in ast.walk(tree)
             if isinstance(node, ast.ImportFrom) and node.module == '_lapjv_rh'}
    lines.update(key.lineno for key in exports_node.keys
                 if key is not None and ast.literal_eval(key) in omitted)
    lines.update(item.lineno for item in public_node.elts if ast.literal_eval(item) in omitted)
    result = ''.join(line for number, line in enumerate(content.splitlines(keepends=True), 1)
                     if number not in lines)
    # Fail rather than drop unrelated exports if declarations are reformatted.
    message = 'Declare R/H imports and exports on separate lines in lap/__init__.py'
    try:
        tree, built_exports, built_public = declarations(result)
    except (SyntaxError, KeyError) as exc:
        raise RuntimeError(message) from exc
    if (ast.literal_eval(built_exports) != {name: value for name, value in exports.items()
                                          if name not in omitted}
            or ast.literal_eval(built_public) != [name for name in public if name not in omitted]
            or any(isinstance(node, ast.Name) and node.id in omitted for node in ast.walk(tree))):
        raise RuntimeError(message)
    return result


def windows_rust_target(platform_name, configured=None):
    """Match Cargo to setuptools, including cibuildwheel ARM64 cross builds."""
    target = {'win-amd64': 'x86_64-pc-windows-msvc',
              'win-arm64': 'aarch64-pc-windows-msvc',
              'win32': 'i686-pc-windows-msvc'}.get(platform_name)
    if target is None or (configured and configured != target):
        raise RuntimeError('Rust target must match the Python extension platform: ' + platform_name)
    return target


def configure_macos_rust_build():
    """Keep the Python extension and Rust archive on the same architecture."""
    import os, platform, re, sys, sysconfig
    if sys.platform != 'darwin' or not build_rust_enabled():
        return
    flags = os.environ.get('ARCHFLAGS', '-arch ' + platform.machine())
    architectures = set(re.findall(r'-arch\s+(\S+)', flags))
    if len(architectures) != 1 or not architectures <= {'x86_64', 'arm64'}:
        raise RuntimeError('Build LAPJVR separately for each macOS architecture; universal2 is unsupported')
    architecture = architectures.pop()
    target_triple = {'x86_64': 'x86_64-apple-darwin', 'arm64': 'aarch64-apple-darwin'}[architecture]
    if os.environ.get('CARGO_BUILD_TARGET', target_triple) != target_triple:
        raise RuntimeError('Rust target must match the macOS extension architecture')
    os.environ['CARGO_BUILD_TARGET'] = target_triple
    os.environ['ARCHFLAGS'] = flags
    minimum = (11, 0) if architecture == 'arm64' else (10, 12)
    configured = os.environ.get('MACOSX_DEPLOYMENT_TARGET') or sysconfig.get_config_var(
        'MACOSX_DEPLOYMENT_TARGET') or '0.0'
    target = max(minimum, tuple(int(part) for part in configured.split('.')))
    deployment_target = '.'.join(str(part) for part in target)
    os.environ['MACOSX_DEPLOYMENT_TARGET'] = deployment_target
    platform_name = 'macosx-{}-{}'.format(deployment_target, architecture)
    host_platform = os.environ.get('_PYTHON_HOST_PLATFORM', platform_name)
    # cibuildwheel keeps a baseline OS version in this tag (10.9 on Intel),
    # even when MACOSX_DEPLOYMENT_TARGET is newer. Validate the architecture,
    # then align the wheel tag with the deployment target used by C++ and Rust.
    if not re.fullmatch(r'macosx-\d+(?:\.\d+)*-' + architecture, host_platform):
        raise RuntimeError('LAPJVR wheel platform must match the macOS extension architecture')
    os.environ['_PYTHON_HOST_PLATFORM'] = platform_name

class Build(build):
    """Keep optional extension artifacts out of subsequent default wheels."""

    def finalize_options(self):
        explicit_library_dir = self.build_lib is not None
        super().finalize_options()
        if not explicit_library_dir and has_rust_extension(self.distribution):
            self.build_lib += '-rh'


class BuildPy(build_py):
    """Match the wheel's public API to its compiled solver families."""

    def run(self):
        if self.editable_mode and not has_rust_extension(self.distribution):
            # Strict editable installs copy generated files and link ordinary sources.
            self.build_packages()
            self.build_package_data()
        else:
            super().run()

    def get_output_mapping(self):
        mapping = super().get_output_mapping()
        if self.editable_mode and not has_rust_extension(self.distribution):
            # The filtered initializer is generated, so do not link its source.
            mapping.pop(self.get_module_outfile(self.build_lib, [PACKAGE_PATH], '__init__'), None)
        return mapping

    def get_outputs(self, include_bytecode=True):
        outputs = super().get_outputs(include_bytecode)
        if self.editable_mode and not has_rust_extension(self.distribution):
            outputs.append(self.get_module_outfile(self.build_lib, [PACKAGE_PATH], '__init__'))
        return outputs

    def find_data_files(self, package, src_dir):
        from pathlib import Path
        files = super().find_data_files(package, src_dir)
        if package == PACKAGE_PATH and not has_rust_extension(self.distribution):
            files = [filename for filename in files if Path(filename).name != '_lapjv_rh.pyi']
        return files

    def build_module(self, module, module_file, package):
        from pathlib import Path
        is_init = package == PACKAGE_PATH and module == '__init__'
        if is_init:
            target = Path(self.build_lib) / PACKAGE_PATH / '__init__.py'
            if target.resolve() == Path(module_file).resolve():
                raise RuntimeError('Build LAPX into a directory separate from the source package')
        output, copied = super().build_module(module, module_file, package)
        if is_init and not self.dry_run:
            content = Path(module_file).read_text(encoding='utf-8')
            if not has_rust_extension(self.distribution):
                content = legacy_initializer(content)
            # Always derive this file from source, including on incremental builds.
            if Path(output).read_text(encoding='utf-8') != content:
                Path(output).write_text(content, encoding='utf-8')
                copied = True
        return output, copied

    def build_package_data(self):
        from pathlib import Path
        super().build_package_data()
        if not self.dry_run:
            # Remove obsolete modules from incremental builds.
            patterns = ['_lapjvr.pyi', '_lapjvr*.pyd', '_lapjvr*.so',
                        '_lapjv_wp.py', '_lapjvx_wp.py', '_lapjvc_wp.py']
            if not has_rust_extension(self.distribution):
                patterns += ['_lapjv_rh.pyi', '_lapjv_rh*.pyd', '_lapjv_rh*.so']
            for pattern in patterns:
                for artifact in (Path(self.build_lib) / PACKAGE_PATH).glob(pattern):
                    artifact.unlink()


class EditableWheel(editable_wheel):
    """Expose the filtered package in legacy-only editable installs."""

    def finalize_options(self):
        super().finalize_options()
        if not has_rust_extension(self.distribution):
            # Lenient/compat modes expose source files that still declare R/H.
            self.mode = 'strict'


class BuildExt(build_ext):
    """Add portable optimization flags for the compiler and linker.

    Environment variables control these options:
    - LAPX_BASEOPTS=0 disables the base flags that LAPX adds and link-time
      optimization (LTO). Other compiler defaults may still apply.
    - LAPX_FASTMATH=1 enables -ffast-math or /fp:fast.
    - LAPX_NATIVE=1 enables -march=native -mtune=native.
    - LAPX_LTO=0 disables LTO, including inherited LTO defaults.

    LAPX_BASEOPTS=0 does not guarantee an unoptimized or debug build.
    Fast-math and native tuning are independent options. Both are disabled by default.
    """
    def has_flag(self, flag, link_flag=None):
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = os.path.join(tmpdir, 'flagcheck.cpp')
            with open(fname, 'w') as f:
                f.write("int main(){return 0;}")
            try:
                objects = self.compiler.compile(
                    [fname], output_dir=tmpdir, extra_postargs=[flag], debug=self.debug)
                if link_flag is not None:
                    self.compiler.link_shared_object(
                        objects,
                        os.path.join(tmpdir, 'flagcheck' + self.compiler.shared_lib_extension),
                        extra_postargs=[link_flag], target_lang='c++', debug=self.debug)
            except Exception:
                return False
        return True

    def build_extensions(self):
        import os, sys

        rust_extensions = [ext for ext in self.extensions if ext.name == 'lap._lapjv_rh']
        if rust_extensions:
            import subprocess
            from pathlib import Path
            manifest = Path(__file__).resolve().parent / 'src/_lapjvr/Cargo.toml'
            target_dir = Path(self.build_temp).resolve() / 'lapjv-rh'
            rust_env = os.environ.copy()
            if sys.platform == 'win32':
                rust_env['CARGO_BUILD_TARGET'] = windows_rust_target(
                    self.plat_name, rust_env.get('CARGO_BUILD_TARGET'))
            if os.environ.get('LAPX_BASEOPTS', '1').strip() == '0':
                rust_env['CARGO_PROFILE_RELEASE_OPT_LEVEL'] = '0'
                rust_env['CARGO_PROFILE_RELEASE_LTO'] = 'false'
            elif os.environ.get('LAPX_LTO', '1').strip() == '0':
                rust_env['CARGO_PROFILE_RELEASE_LTO'] = 'false'
            if os.environ.get('LAPX_NATIVE', '').strip() == '1':
                rust_env['RUSTFLAGS'] = rust_env.get('RUSTFLAGS', '') + ' -C target-cpu=native'
            try:
                if sys.platform.startswith('linux'):
                    version = subprocess.check_output(['rustc', '-vV'], text=True, env=rust_env)
                    host = next(line.split(': ', 1)[1] for line in version.splitlines()
                                if line.startswith('host: '))
                    if 'musl' in rust_env.get('CARGO_BUILD_TARGET', host):
                        # A Python shared library must use the process's libc.
                        rust_env['RUSTFLAGS'] = rust_env.get('RUSTFLAGS', '') + (
                            ' -C target-feature=-crt-static -C relocation-model=pic')
                subprocess.run(['cargo', 'build', '--release', '--locked',
                                '--manifest-path', str(manifest), '--target-dir', str(target_dir),
                                '--features', 'cpp-completion'],
                               check=True, env=rust_env)
            except FileNotFoundError as exc:
                raise RuntimeError('Building LAPJVR/LAPJVH requires current Rust and Cargo. '
                                   'Install Rust or set LAPX_BUILD_RUST=0 for existing solvers only.') from exc
            rust_target = rust_env.get('CARGO_BUILD_TARGET')
            library_dir = target_dir / rust_target / 'release' if rust_target else target_dir / 'release'
            library = library_dir / ('lapjvr_core.lib' if sys.platform == 'win32' else 'liblapjvr_core.a')
            for ext in rust_extensions:
                ext.extra_objects = list(ext.extra_objects or []) + [str(library)]
                ext.depends = list(ext.depends or []) + [str(library)]
                ext.libraries = list(ext.libraries or []) + (
                    ['ws2_32', 'userenv', 'advapi32', 'ntdll', 'bcrypt'] if sys.platform == 'win32'
                    else (['pthread', 'dl', 'm', 'rt', 'util'] if sys.platform.startswith('linux') else ['pthread', 'm']))

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
        lto_enabled = False

        if is_msvc:
            # Base optimizations on MSVC
            if base_enabled:
                compile_opts += ['/O2', '/DNDEBUG']
                # Respect LAPX_LTO on MSVC when base opts are enabled
                if env_lto_on and self.has_flag('/GL', '/LTCG'):
                    compile_opts += ['/GL']
                    link_opts += ['/LTCG']
                    lto_enabled = True
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
                    if self.has_flag('-flto=thin', '-flto=thin'):
                        compile_opts += ['-flto=thin']; link_opts += ['-flto=thin']
                        lto_enabled = True
                    elif self.has_flag('-flto', '-flto'):
                        compile_opts += ['-flto']; link_opts += ['-flto']
                        lto_enabled = True
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

        # Override inherited LTO defaults when disabled or when the probe fails.
        if not lto_enabled:
            compile_opts += ['/GL-' if is_msvc else '-fno-lto']
            link_opts += ['/LTCG:OFF' if is_msvc else '-fno-lto']

        # Apply to all extensions (always)
        for ext in self.extensions:
            prev_cargs = list(getattr(ext, 'extra_compile_args', []) or [])
            prev_largs = list(getattr(ext, 'extra_link_args', []) or [])
            ext.extra_compile_args = prev_cargs + compile_opts
            ext.extra_link_args = prev_largs + link_opts
            if ext.name == 'lap._lapjv_rh':
                # Conversion and forbidden-edge checks require strict arithmetic.
                ext.extra_compile_args += ['/fp:precise' if is_msvc else '-fno-fast-math']
                if sys.platform.startswith('linux'):
                    # Keep the bundled Rust runtime private to this extension.
                    ext.extra_link_args += ['-Wl,--exclude-libs,ALL']
        
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
    if 'LAPX_RUST_CPP' in os.environ:
        import warnings
        warnings.warn('LAPX_RUST_CPP is obsolete: LAPJVR and LAPJVH now coexist. '
                      'Call lapjvh explicitly for C++ completion.', stacklevel=2)
    configure_macos_rust_build()
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
        # MSVC 14.44: /std:c++17 is neutral or faster for most solvers, but
        # lapjvs/lapjvsa are up to ~8% faster with /std:c++latest.
        extra_compile_args = ["/std:c++17"]
        jvs_compile_args = ["/std:c++latest"]
    else:
        extra_compile_args = ["-std=c++17"]
        jvs_compile_args = extra_compile_args

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
        extra_compile_args=jvs_compile_args,
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

    if build_rust_enabled():
        rust_dir = os.path.join('src', '_lapjvr')
        ext_rust = Extension(
            name='lap._lapjv_rh', sources=[os.path.join(rust_dir, '_lapjv_rh.pyx')],
            include_dirs=[include_numpy(), rust_dir], language='c++',
            extra_compile_args=extra_compile_args,
        )
        ext_modules += cythonize([ext_rust], compiler_directives=cython_directives)

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
                  'lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch',
                  'lapjvr', 'lapjvh', 'lapjvr_batch', 'lapjvh_batch',
                  'lapmod_batch'],
        packages=find_packages(include=[PACKAGE_PATH, f"{PACKAGE_PATH}.*"]),
        include_package_data=True,
        exclude_package_data={'lap': ['_lapjvr*.pyd', '_lapjvr*.so',
                                      '_lapjv_rh*.pyd', '_lapjv_rh*.so']},
        license_files=['LICENSE', 'NOTICE'] + (
            ['src/_lapjvr/LICENSE', 'src/_lapjvr/THIRD_PARTY_NOTICES']
            if build_rust_enabled() else []),
        install_requires=['numpy>=1.21.6',],
        # Keep source installation available on older Python versions.
        python_requires=">=3.7",
        classifiers=['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Education',
                     'Intended Audience :: Science/Research',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Programming Language :: Python :: 3.11',
                     'Programming Language :: Python :: 3.12',
                     'Programming Language :: Python :: 3.13',
                     'Programming Language :: Python :: 3.14',
                     'Programming Language :: Python :: 3.15',
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
        cmdclass={
            'build': Build,
            'build_py': BuildPy,
            'build_ext': BuildExt,
            'editable_wheel': EditableWheel
        },
    )

if __name__ == "__main__":
    """Use :py:mod:`build` to build the package without changes to the current environment.

    >>> pip install wheel build
    >>> python -m build --sdist
    >>> python -m build --wheel

    The build applies safe base optimizations automatically:
    - /O2 on MSVC or -O3 on GCC and Clang enables compiler optimizations.
    - -DNDEBUG disables debug assertions.
    - Link-time optimization (LTO) applies when the compiler and linker support it.

    Environment variables control additional options:
    - LAPX_BASEOPTS=0 disables the base flags that LAPX adds and LTO.
      Other compiler defaults may still apply.
    - LAPX_FASTMATH=1 enables fast-math with /fp:fast on MSVC or -ffast-math on GCC and Clang.
    - LAPX_NATIVE=1 enables -march=native -mtune=native on GCC and Clang only.
    - LAPX_LTO=0 disables LTO, including inherited LTO defaults.

    LAPX_BASEOPTS=0 does not guarantee an unoptimized or debug build.
    Fast-math and native tuning are independent options. Both are disabled by default.
    Keep both options disabled for portable release wheels.
    Fast-math may change numerical results and the treatment of NaN or infinity.

    To build with fast-math on Linux or macOS, use this command:
    >>> LAPX_FASTMATH=1 python -m build --wheel

    To build with fast-math in the Windows command prompt (CMD), use this command:
    >>> set "LAPX_FASTMATH=1" && python -m build --wheel

    The build applies Cython compiler directives by default for Cython modules.
    Examples include boundscheck=False, wraparound=False, and cdivision=True.
    """
    main_setup()
