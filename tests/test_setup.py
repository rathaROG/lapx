"""Check for regressions in link-time optimization (LTO) selection without a native compiler."""

import runpy
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
