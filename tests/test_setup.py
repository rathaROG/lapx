"""Check build configuration and compiler option selection without a native compiler."""

import ast
import os
import re
import runpy
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("setuptools")
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext
from setuptools.errors import CompileError, LinkError


class ProbeCompiler:
    shared_lib_extension = ".so"

    def __init__(self, compiler_type, compile_failures=(), link_failures=()):
        self.compiler_type = compiler_type
        self.compile_failures = compile_failures
        self.link_failures = link_failures
        self.compiles = []
        self.links = []
        self.temp_dirs = []

    def compile(self, sources, output_dir=None, extra_postargs=(), **kwargs):
        self.compiles.extend(extra_postargs)
        self.temp_dirs.append(Path(output_dir or Path.cwd()))
        if any(flag in self.compile_failures for flag in extra_postargs):
            raise CompileError("Unsupported compiler flag")
        obj = Path(output_dir or Path(sources[0]).parent) / "flagcheck.obj"
        obj.write_bytes(b"object")
        return [str(obj)]

    def link_shared_object(self, objects, output_filename, extra_postargs=(), **kwargs):
        assert all(Path(obj).is_file() for obj in objects)
        assert kwargs["target_lang"] == "c++"
        self.links.extend(extra_postargs)
        if any(flag in self.link_failures for flag in extra_postargs):
            raise LinkError("LTO linker support is unavailable")
        Path(output_filename).write_bytes(b"library")


@pytest.fixture
def build_command(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    namespace = runpy.run_path(str(root / "setup.py"))
    for name in ("LAPX_BASEOPTS", "LAPX_LTO", "LAPX_FASTMATH", "LAPX_NATIVE"):
        monkeypatch.delenv(name, raising=False)
    # Exercise option selection and the probes, without building LAPX itself.
    monkeypatch.setattr(build_ext, "build_extensions", lambda self: None)
    cmd = namespace["BuildExt"](Distribution())
    cmd.ensure_finalized()
    cmd.extensions = [Extension("lap.probe", ["probe.cpp"])]
    return cmd


@pytest.mark.parametrize(
    "compiler_type,compile_failures,link_failures,expected_compile,expected_link",
    [
        ("msvc", (), (), "/GL", "/LTCG"),
        ("msvc", ("/GL",), (), "/GL-", "/LTCG:OFF"),
        ("msvc", (), ("/LTCG",), "/GL-", "/LTCG:OFF"),
        ("unix", (), (), "-flto=thin", "-flto=thin"),
        ("unix", ("-flto=thin",), (), "-flto", "-flto"),
        ("unix", (), ("-flto=thin",), "-flto", "-flto"),
        ("unix", (), ("-flto=thin", "-flto"), "-fno-lto", "-fno-lto"),
    ],
)
def test_lto_requires_compile_and_link_support(
    build_command, compiler_type, compile_failures, link_failures,
    expected_compile, expected_link,
):
    compiler = ProbeCompiler(compiler_type, compile_failures, link_failures)
    build_command.compiler = compiler
    build_command.build_extensions()
    ext = build_command.extensions[0]
    assert expected_compile in ext.extra_compile_args
    assert ext.extra_link_args == [expected_link]
    assert ("/O2" if compiler_type == "msvc" else "-O3") in ext.extra_compile_args
    if expected_link not in ("/LTCG:OFF", "-fno-lto"):
        assert expected_link in compiler.links
    assert all(not path.exists() for path in compiler.temp_dirs)


@pytest.mark.parametrize("compiler_type", ["msvc", "unix"])
@pytest.mark.parametrize("switch", ["LAPX_LTO", "LAPX_BASEOPTS"])
def test_disabled_lto_overrides_existing_flags(build_command, monkeypatch, compiler_type, switch):
    monkeypatch.setenv(switch, "0")
    compiler = ProbeCompiler(compiler_type)
    build_command.compiler = compiler
    ext = build_command.extensions[0]
    # Existing arguments, like compiler defaults, must precede the off switches.
    compile_on, link_on, compile_off, link_off = (
        ("/GL", "/LTCG", "/GL-", "/LTCG:OFF") if compiler_type == "msvc"
        else ("-flto", "-flto", "-fno-lto", "-fno-lto")
    )
    ext.extra_compile_args = [compile_on]
    ext.extra_link_args = [link_on]
    build_command.build_extensions()
    assert ext.extra_compile_args[0] == compile_on
    assert ext.extra_compile_args[-1] == compile_off
    assert ext.extra_link_args == [link_on, link_off]
    assert not compiler.links
    assert not {"/GL", "-flto", "-flto=thin"}.intersection(compiler.compiles)
    assert all(not path.exists() for path in compiler.temp_dirs)

def test_optional_rust_build_uses_separate_library_directory(tmp_path):
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'setup.py'))
    def configured(extension, explicit=None):
        command = namespace['Build'](Distribution({'ext_modules': [Extension(extension, ['probe.cpp'])]}))
        command.build_base = str(tmp_path)
        command.build_lib = explicit
        command.ensure_finalized()
        return command.build_lib
    default = configured('lap._lapjvx')
    optional = configured('lap._lapjv_rh')
    assert default != optional
    assert configured('lap._lapjvx') == default
    explicit = str(tmp_path / 'explicit')
    assert configured('lap._lapjv_rh', explicit) == explicit


def test_wheel_typing_matches_families_across_rebuilds(tmp_path):
    root = Path(__file__).resolve().parents[1]
    namespace = runpy.run_path(str(root / 'setup.py'))
    source = tmp_path / 'source' / 'lap'
    source.mkdir(parents=True)
    originals = {name: (root / 'lap' / name).read_bytes()
                 for name in ('__init__.py', '_lapjv_rh.pyi', 'py.typed')}
    for name, content in originals.items():
        (source / name).write_bytes(content)
    output = tmp_path / 'wheel'
    (output / 'lap').mkdir(parents=True)
    former_artifacts = ('_lapjvr.pyi', '_lapjvr.cp311-win_amd64.pyd',
                        '_lapjvr.cpython-311-x86_64-linux-gnu.so')
    for name in former_artifacts:
        (output / 'lap' / name).write_bytes(b'stale artifact')
    for enabled in (True, False, False, True):
        distribution = Distribution({
            'packages': ['lap'], 'package_dir': {'lap': str(source)},
            'package_data': {'lap': ['*.pyi', 'py.typed']},
            'ext_modules': [Extension('lap._lapjv_rh', ['probe.cpp'])] if enabled else [],
        })
        distribution.script_name = str(root / 'setup.py')
        command = namespace['BuildPy'](distribution)
        command.build_lib = str(output)
        command.ensure_finalized()
        command.run()
        built_init = (output / 'lap' / '__init__.py').read_text(encoding='utf-8')
        declarations = {target.id: ast.literal_eval(node.value)
                        for node in ast.parse(built_init).body if isinstance(node, ast.Assign)
                        for target in node.targets if isinstance(target, ast.Name)
                        and target.id in ('_exports', '__all__')}
        imports_rh = any(isinstance(node, ast.ImportFrom) and node.module == '_lapjv_rh'
                         for node in ast.walk(ast.parse(built_init)))
        assert imports_rh is enabled
        for name in ('lapjvr', 'lapjvh', 'lapjvr_batch', 'lapjvh_batch'):
            assert (name in declarations['_exports']) is enabled
            assert (name in declarations['__all__']) is enabled
        for name in ('lapjv', 'lapjvx', 'lapjvs', 'lapmod', 'lapmod_batch'):
            assert name in declarations['_exports'] and name in declarations['__all__']
        assert (output / 'lap' / '_lapjv_rh.pyi').exists() is enabled
        assert not any((output / 'lap' / name).exists() for name in former_artifacts)
        assert (output / 'lap' / 'py.typed').read_bytes() == originals['py.typed']
        assert all((source / name).read_bytes() == content
                   for name, content in originals.items())
        if enabled:
            assert built_init == originals['__init__.py'].decode('utf-8').replace('\r\n', '\n')
            assert (output / 'lap' / '_lapjv_rh.pyi').read_bytes() == originals['_lapjv_rh.pyi']


def test_legacy_initializer_rejects_removing_unrelated_exports():
    root = Path(__file__).resolve().parents[1]
    namespace = runpy.run_path(str(root / 'setup.py'))
    source = (root / 'lap/__init__.py').read_text(encoding='utf-8')
    source = source.replace("    'lapjvr', 'lapjvh',", "    'lapjvr', 'lapjvh', 'other_solver',")
    with pytest.raises(RuntimeError, match='separate lines'):
        namespace['legacy_initializer'](source)


@pytest.fixture
def packaging_project(tmp_path):
    """Exercise the real packaging commands with Python stand-ins for native solvers."""
    root = Path(__file__).resolve().parents[1]
    project = tmp_path / 'project'
    package = project / 'lap'
    package.mkdir(parents=True)
    for name in ('README.md', 'MANIFEST.in', 'pyproject.toml'):
        shutil.copy2(root / name, project / name)
    for name in ('__init__.py', '_lapjv_rh.pyi', 'py.typed'):
        shutil.copy2(root / 'lap' / name, package / name)

    tree = ast.parse((package / '__init__.py').read_text(encoding='utf-8'))
    exports = next(ast.literal_eval(node.value) for node in tree.body
                   if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == '_exports' for t in node.targets))
    modules = {}
    for module, attr in exports.values():
        if module != 'lap._lapjv_rh':
            modules.setdefault(module.split('.')[-1], []).append(attr)
    for module, attributes in modules.items():
        content = '\n'.join(attr + ' = 1\n' if attr.endswith('_') else
                            "def {}():\n    return 'original'\n".format(attr)
                            for attr in attributes)
        (package / (module + '.py')).write_text(content, encoding='utf-8')
    # Switching from a full in-place build must not expose its stale R/H binaries.
    from importlib.machinery import EXTENSION_SUFFIXES
    for module in ('_lapjvr', '_lapjv_rh'):
        (package / (module + EXTENSION_SUFFIXES[0])).write_bytes(b'stale binary')
    (project / 'tests').mkdir()
    shutil.copy2(root / 'tests/check_rh_wheel.py', project / 'tests/check_rh_wheel.py')
    (project / 'tests/test_omitted.py').write_text('raise AssertionError\n', encoding='utf-8')
    native = project / 'src/_lapjvr'
    native.mkdir(parents=True)
    shutil.copy2(root / 'src/_lapjvr/_lapjv_rh.pyx', native / '_lapjv_rh.pyx')
    (native / '_lapjv_rh.cpp').write_text('generated', encoding='utf-8')
    (native / 'target').mkdir()
    (native / 'target/artifact').write_text('compiled', encoding='utf-8')

    # Read the real registration and exclusions so the fixture cannot mask a
    # missing command registration, while avoiding Cython and native compilation.
    setup_tree = ast.parse((root / 'setup.py').read_text(encoding='utf-8'))
    setup_call = next(node for node in ast.walk(setup_tree) if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Name) and node.func.id == 'setup')
    options = {kw.arg: kw.value for kw in setup_call.keywords}
    commands = {ast.literal_eval(key): value.id
                for key, value in zip(options['cmdclass'].keys, options['cmdclass'].values)}
    kwargs = dict(name='lapx-packaging-probe', version='0.0', packages=['lap'],
                  include_package_data=True, package_data={'lap': ['*.pyi', 'py.typed']},
                  exclude_package_data=ast.literal_eval(options['exclude_package_data']))
    (project / 'setup.py').write_text(
        'import runpy\nfrom setuptools import setup\n'
        'namespace = runpy.run_path({!r})\n'.format(str(root / 'setup.py')) +
        'kwargs = {!r}\n'.format(kwargs) +
        'kwargs["cmdclass"] = {{name: namespace[cls] for name, cls in {!r}.items()}}\n'.format(commands) +
        'setup(**kwargs)\n', encoding='utf-8')
    return project


def build_packaging_project(project, kind, settings=None):
    result = subprocess.run(
        [sys.executable, '-c', 'from setuptools import build_meta; '
         'build_meta.build_{}("dist", config_settings={!r})'.format(kind, settings)],
        cwd=str(project), env=dict(os.environ, LAPX_BUILD_RUST='0'),
        capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    archives = list((project / 'dist').glob('*.tar.gz' if kind == 'sdist' else '*.whl'))
    assert len(archives) == 1
    return archives[0]


@pytest.mark.parametrize('mode', [None, 'strict', 'compat'])
def test_legacy_editable_matches_wheel_and_keeps_python_edits(packaging_project, tmp_path, mode):
    project = packaging_project
    originals = {name: (project / 'lap' / name).read_bytes()
                 for name in ('__init__.py', '_lapjv_rh.pyi', 'py.typed')}
    settings = {'editable_mode': mode} if mode else None
    wheel = build_packaging_project(project, 'editable', settings)
    installed = tmp_path / 'site'
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(installed)
    probe = '''
import importlib.util
from pathlib import Path
import site
import sys
site.addsitedir(sys.argv[1])
import lap
assert Path(lap.__file__).resolve() != Path(sys.argv[2]).resolve()
assert Path(lap.__file__).with_name('py.typed').is_file()
assert not Path(lap.__file__).with_name('_lapjv_rh.pyi').exists()
assert importlib.util.find_spec('lap._lapjv_rh') is None
assert importlib.util.find_spec('lap._lapjvr') is None
for name in ('lapjvr', 'lapjvh', 'lapjvr_batch', 'lapjvh_batch'):
    assert name not in lap.__all__ and name not in dir(lap)
    assert name not in lap._exports and not hasattr(lap, name)
namespace = {}
exec('from lap import *', namespace)
assert set(lap.__all__) <= set(namespace)
assert lap.lapjvx() == sys.argv[3]
'''
    for expected in ('original', 'edited-source'):
        result = subprocess.run(
            [sys.executable, '-S', '-c', probe, str(installed),
             str(project / 'lap/__init__.py'), expected],
            cwd=str(tmp_path), capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        wrapper = project / 'lap/_lapjvx_wp.py'
        wrapper.write_text(wrapper.read_text(encoding='utf-8').replace('original', 'edited-source'),
                           encoding='utf-8')
    assert all((project / 'lap' / name).read_bytes() == content
               for name, content in originals.items())


def test_source_archive_contains_wheel_checks_and_full_rh_sources(packaging_project):
    project = packaging_project
    archive = build_packaging_project(project, 'sdist')
    with tarfile.open(archive) as source:
        prefix = source.getnames()[0].split('/')[0] + '/'
        contents = {name[len(prefix):]: source.extractfile(name).read()
                    for name in source.getnames() if source.getmember(name).isfile()}
    config = contents['pyproject.toml'].decode('utf-8')
    commands = re.findall(r'^test-command = "([^"]+)"', config, re.MULTILINE)
    assert len(commands) == 2 and any('--legacy-only' in command for command in commands)
    for command in commands:
        script = re.search(r'\{project\}/(\S+\.py)', command).group(1)
        assert contents[script] == (project / script).read_bytes()
    assert {name for name in contents if name.startswith('tests/')} == {'tests/check_rh_wheel.py'}
    for name in ('lap/__init__.py', 'lap/_lapjv_rh.pyi', 'src/_lapjvr/_lapjv_rh.pyx'):
        assert contents[name] == (project / name).read_bytes()
    assert 'src/_lapjvr/_lapjv_rh.cpp' not in contents
    assert not any(name.startswith('src/_lapjvr/target/') for name in contents)


@pytest.mark.parametrize('value,expected', [(None, True), ('1', True), ('0', False)])
def test_rh_families_are_built_together_by_default(monkeypatch, value, expected):
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'setup.py'))
    monkeypatch.delenv('LAPX_BUILD_RUST', raising=False)
    if value is not None:
        monkeypatch.setenv('LAPX_BUILD_RUST', value)
    assert namespace['build_rust_enabled']() is expected


@pytest.mark.parametrize('platform,target', [
    ('win-amd64', 'x86_64-pc-windows-msvc'),
    ('win-arm64', 'aarch64-pc-windows-msvc'),
    ('win32', 'i686-pc-windows-msvc'),
])
def test_rust_archive_matches_windows_extension_architecture(platform, target):
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'setup.py'))
    choose = namespace['windows_rust_target']
    assert choose(platform) == choose(platform, target) == target
    with pytest.raises(RuntimeError, match='must match'):
        choose(platform, 'wrong-target')


@pytest.fixture
def macos_rust_build(monkeypatch):
    import os
    import platform
    import sys
    import sysconfig
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'setup.py'))
    # The build helper writes directly to os.environ; isolate those writes too.
    monkeypatch.setattr(os, 'environ', dict(os.environ))
    for name in ('LAPX_BUILD_RUST', 'CARGO_BUILD_TARGET', 'ARCHFLAGS', '_PYTHON_HOST_PLATFORM',
                 'MACOSX_DEPLOYMENT_TARGET'):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setattr(platform, 'machine', lambda: 'x86_64')
    monkeypatch.setattr(sysconfig, 'get_config_var', lambda _: '10.9')
    return namespace['configure_macos_rust_build']


@pytest.mark.parametrize('architecture,flags,expected', [
    ('x86_64', '-arch x86_64', 'x86_64-apple-darwin'),
    ('x86_64', '-arch arm64', 'aarch64-apple-darwin'),
    ('arm64', '-arch x86_64', 'x86_64-apple-darwin'),
    ('arm64', '-arch arm64 -arch x86_64', None),
])
def test_macos_single_architecture_rust_target(
    monkeypatch, macos_rust_build, architecture, flags, expected,
):
    import os
    import platform
    monkeypatch.setattr(platform, 'machine', lambda: architecture)
    monkeypatch.setenv('ARCHFLAGS', flags)
    if expected is None:
        with pytest.raises(RuntimeError, match='universal2'):
            macos_rust_build()
    else:
        macos_rust_build()
        assert os.environ['CARGO_BUILD_TARGET'] == expected
        target_arch = 'arm64' if expected.startswith('aarch64') else 'x86_64'
        assert os.environ['_PYTHON_HOST_PLATFORM'].endswith('-' + target_arch)
        assert os.environ['MACOSX_DEPLOYMENT_TARGET'] == ('11.0' if target_arch == 'arm64' else '10.12')


@pytest.mark.parametrize('architecture,host_platform,deployment,expected', [
    ('x86_64', 'macosx-10.9-x86_64', '10.12', '10.12'),
    ('x86_64', 'macosx-10.9-x86_64', '10.13', '10.13'),
    ('x86_64', 'macosx-10.9-x86_64', '10.15', '10.15'),
    ('x86_64', 'macosx-10.9-x86_64', None, '10.12'),
    ('x86_64', 'macosx-10.12-x86_64', '10.12', '10.12'),
    ('arm64', 'macosx-11.0-arm64', '10.12', '11.0'),
    ('arm64', 'macosx-11.0-arm64', '12.0', '12.0'),
])
def test_macos_wheel_platform_tracks_deployment_target(
    monkeypatch, macos_rust_build, architecture, host_platform, deployment, expected,
):
    import os
    # cibuildwheel's platform tag keeps its default OS version even when the
    # deployment target is raised by the project or a newer Python version.
    monkeypatch.setenv('ARCHFLAGS', '-arch ' + architecture)
    monkeypatch.setenv('_PYTHON_HOST_PLATFORM', host_platform)
    if deployment is not None:
        monkeypatch.setenv('MACOSX_DEPLOYMENT_TARGET', deployment)
    macos_rust_build()
    assert os.environ['MACOSX_DEPLOYMENT_TARGET'] == expected
    assert os.environ['_PYTHON_HOST_PLATFORM'] == 'macosx-{}-{}'.format(expected, architecture)
    assert os.environ['CARGO_BUILD_TARGET'] == (
        'x86_64-apple-darwin' if architecture == 'x86_64' else 'aarch64-apple-darwin')
    assert os.environ['ARCHFLAGS'] == '-arch ' + architecture
    # Repeated setup hooks must accept the normalized platform as well.
    macos_rust_build()
    assert os.environ['_PYTHON_HOST_PLATFORM'] == 'macosx-{}-{}'.format(expected, architecture)


@pytest.mark.parametrize('architecture,host_platform', [
    ('x86_64', 'macosx-11.0-arm64'),
    ('arm64', 'macosx-10.12-x86_64'),
    ('x86_64', 'macosx-10.9-universal2'),
    ('x86_64', 'linux-x86_64'),
])
def test_macos_wheel_platform_rejects_incompatible_architecture(
    monkeypatch, macos_rust_build, architecture, host_platform,
):
    monkeypatch.setenv('ARCHFLAGS', '-arch ' + architecture)
    monkeypatch.setenv('_PYTHON_HOST_PLATFORM', host_platform)
    with pytest.raises(RuntimeError, match='wheel platform must match'):
        macos_rust_build()


def test_macos_rust_target_rejects_incompatible_architecture(monkeypatch, macos_rust_build):
    monkeypatch.setenv('ARCHFLAGS', '-arch x86_64')
    monkeypatch.setenv('CARGO_BUILD_TARGET', 'aarch64-apple-darwin')
    with pytest.raises(RuntimeError, match='Rust target must match'):
        macos_rust_build()
