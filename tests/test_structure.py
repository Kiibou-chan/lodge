from pathlib import Path

import pytest

from structure_rules import MAX_LINES, modules, violations
from structure_tree import PACKAGES, only, scan


def test_core_importing_app(tmp_path: Path) -> None:
    only(scan(tmp_path, {"core/a.py": "from lodge.app import Lodge\n"}), "core may not import app")


def test_adapter_importing_adapter(tmp_path: Path) -> None:
    found = scan(tmp_path, {"cli/a.py": "from lodge.gitstore import open_store\n"})
    only(found, "cli may not import gitstore")


def test_import_past_front_door(tmp_path: Path) -> None:
    files = {"core/check.py": "", "app/a.py": "from lodge.core.check import run\n"}
    only(scan(tmp_path, files), "lodge.core.check past the front door lodge.core")


def test_submodule_through_front_door(tmp_path: Path) -> None:
    files = {"core/check.py": "", "app/a.py": "from lodge.core import check\n"}
    only(scan(tmp_path, files), "lodge.core.check past the front door lodge.core")


def test_from_lodge_import_package(tmp_path: Path) -> None:
    only(
        scan(tmp_path, {"cli/a.py": "from lodge import gitstore\n"}), "cli may not import gitstore"
    )


def test_import_statement_form(tmp_path: Path) -> None:
    files = {"gitstore/git.py": "", "cli/a.py": "import lodge.gitstore.git as g\n"}
    only(scan(tmp_path, files), "cli may not import gitstore")


def test_relative_import(tmp_path: Path) -> None:
    only(scan(tmp_path, {"cli/a.py": "from ..gitstore import x\n"}), "relative import")


def test_import_inside_function(tmp_path: Path) -> None:
    src = "def f() -> None:\n    from lodge.core import x\n"
    only(scan(tmp_path, {"app/a.py": src}), "import inside a function")


@pytest.mark.parametrize(
    "code",
    [
        "import importlib\nimportlib.import_module('x')\n",
        "__import__('x')\n",
        "from importlib import import_module as im\n",
        "import importlib\ngetattr(importlib, 'import_module')('x')\n",
    ],
)
def test_dynamic_import(tmp_path: Path, code: str) -> None:
    only(scan(tmp_path, {"viewer/a.py": code}), "dynamic import")


def test_own_front_door_import(tmp_path: Path) -> None:
    only(
        scan(tmp_path, {"core/check.py": "from lodge.core import Snapshot\n"}),
        "imports its own front door lodge.core",
    )


def test_unknown_package(tmp_path: Path) -> None:
    only(scan(tmp_path, {"importer/__init__.py": ""}), "unknown package importer")


@pytest.mark.parametrize(
    "code",
    [
        "from lodge.core import x\n",
        "import os\n",
        "from os import path\n",
        "import yaml\n",
        "from . import x\n",
    ],
)
def test_root_imports_nothing(tmp_path: Path, code: str) -> None:
    only(scan(tmp_path, {"__init__.py": code}), "root imports nothing")


def test_missing_front_door(tmp_path: Path) -> None:
    only(
        scan(tmp_path, {"core/__init__.py": None, "core/x.py": ""}),
        "lodge/core/__init__.py: missing front door",
    )


def test_package_directory_without_init(tmp_path: Path) -> None:
    only(scan(tmp_path, {"core/sub/x.py": ""}), "no __init__.py")


@pytest.mark.parametrize("where", ["src", "tests"])
def test_source_that_is_not_utf8_names_the_file(tmp_path: Path, where: str) -> None:
    if where == "src":
        found = scan(tmp_path, {"core/a.py": b"x = '\xff'\n"})
        only(found, "core/a.py: not UTF-8")
    else:
        found = scan(tmp_path, {}, {"test_a.py": b"x = '\xff'\n"})
        only(found, "tests/test_a.py: not UTF-8")


def test_import_cycle(tmp_path: Path) -> None:
    files = {
        "core/a.py": "from lodge.core.b import y\n",
        "core/b.py": "from lodge.core.a import x\n",
    }
    only(scan(tmp_path, files), "import cycle")


def test_import_cycle_through_init(tmp_path: Path) -> None:
    files = {"core/__init__.py": "from lodge.core.a import x\n", "core/a.py": "import lodge.core\n"}
    found = scan(tmp_path, files)
    assert [v for v in found if "import cycle" in v and "lodge.core.a" in v], found


@pytest.mark.parametrize("pkg", ["core", "app", "cli"])
@pytest.mark.parametrize("code", ["exec('x')\n", "eval('x')\n", "compile('x', 'f', 'exec')\n"])
def test_dynamic_code(tmp_path: Path, pkg: str, code: str) -> None:
    only(scan(tmp_path, {f"{pkg}/a.py": code}), "dynamic code")


@pytest.mark.parametrize("where", ["src", "tests"])
def test_long_module(tmp_path: Path, where: str) -> None:
    text = "x = 1\n" * (MAX_LINES + 1)
    if where == "src":
        only(scan(tmp_path, {"core/a.py": text}), f"{MAX_LINES + 1} lines")
    else:
        only(scan(tmp_path, {}, {"test_a.py": text}), f"{MAX_LINES + 1} lines")


def test_module_at_the_limit_passes(tmp_path: Path) -> None:
    assert scan(tmp_path, {"core/a.py": "x = 1\n" * MAX_LINES}) == []


def test_syntax_error_is_reported(tmp_path: Path) -> None:
    only(scan(tmp_path, {"core/a.py": "def (\n"}), "cannot parse")


def test_real_tree_is_clean() -> None:
    root = Path(__file__).parents[1]
    assert violations(root / "src", root / "tests") == []
    assert {f"lodge.{p}" for p in PACKAGES} <= modules(root / "src").keys()
