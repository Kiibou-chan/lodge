from pathlib import Path

import pytest

from structure_tree import only, scan


@pytest.mark.parametrize("pkg", ["core", "app"])
@pytest.mark.parametrize(
    "name", ["os", "time", "random", "secrets", "subprocess", "pathlib", "io", "sys"]
)
def test_core_disallowed_module(tmp_path: Path, pkg: str, name: str) -> None:
    only(scan(tmp_path, {f"{pkg}/a.py": f"import {name}\n"}), f"{pkg} may not import {name}")


@pytest.mark.parametrize(
    "code",
    [
        "import datetime as dt\nx = dt.datetime.now()\n",
        "from datetime import date\nx = date.today()\n",
        "from datetime import datetime as D\nx = D.utcnow()\n",
        "import datetime\nx = datetime.datetime.fromtimestamp(0)\n",
        "x = open('f')\n",
        "x = input()\n",
        "print('x')\n",
    ],
)
@pytest.mark.parametrize("pkg", ["core", "app"])
def test_core_banned_name(tmp_path: Path, pkg: str, code: str) -> None:
    only(scan(tmp_path, {f"{pkg}/a.py": code}), f"{pkg} may not use")


def test_clock_port_call_is_not_a_clock_read(tmp_path: Path) -> None:
    src = "def f(clock: object) -> None:\n    clock.now()\n"
    assert scan(tmp_path, {"app/a.py": src}) == []


@pytest.mark.parametrize("code", ["d.now()", "d.today()", "d.utcnow()", "d.fromtimestamp(0)"])
def test_core_names_the_clock_on_any_receiver(tmp_path: Path, code: str) -> None:
    only(scan(tmp_path, {"core/a.py": f"def f(d):\n    return {code}\n"}), "core may not use d.")


def test_subprocess_outside_gitstore(tmp_path: Path) -> None:
    only(scan(tmp_path, {"cli/a.py": "import subprocess\n"}), "process spawning outside gitstore")
    only(
        scan(tmp_path, {"cli/a.py": "from subprocess import run\n"}),
        "process spawning outside gitstore",
    )


SPAWNING = [
    "import os\nos.system('x')\n",
    "import os as o\no.popen('x')\n",
    "import os\nos.execvp('x', [])\n",
    "import os\nos.spawnl(0, 'x')\n",
    "import os\nos.posix_spawn('x', [], {})\n",
    "from os import system\n",
    "import asyncio\nasyncio.create_subprocess_exec('x')\n",
    "from asyncio import create_subprocess_shell\n",
    "from asyncio import subprocess\n",
    "import multiprocessing\n",
    "import pty\n",
]


@pytest.mark.parametrize("path", ["cli/a.py", "viewer/a.py", "hook/a.py", "main.py"])
@pytest.mark.parametrize("code", SPAWNING)
def test_process_spawning_outside_gitstore(tmp_path: Path, path: str, code: str) -> None:
    only(scan(tmp_path, {path: code}), "process spawning outside gitstore")


WRITING = [
    "p.write_text('x')\n",
    "p.write_bytes(b'x')\n",
    "p.mkdir()\n",
    "p.touch()\n",
    "p.unlink()\n",
    "import os\nos.open(p, 0)\n",
    "import os\nos.replace(a, b)\n",
    "from os import remove\n",
    "import shutil\n",
    "import tempfile\n",
    "p.rename(q)\n",
    "p.symlink_to(q)\n",
    "p.hardlink_to(q)\n",
]


@pytest.mark.parametrize("path", ["cli/a.py", "viewer/a.py", "hook/a.py", "main.py"])
@pytest.mark.parametrize("code", WRITING)
def test_file_writing_outside_gitstore(tmp_path: Path, path: str, code: str) -> None:
    found = scan(tmp_path, {path: code})
    assert found and all("file writing outside gitstore" in v for v in found), found


@pytest.mark.parametrize("code", WRITING[:5])
@pytest.mark.parametrize("pkg", ["core", "app"])
def test_pure_packages_do_not_write_files(tmp_path: Path, pkg: str, code: str) -> None:
    only(scan(tmp_path, {f"{pkg}/a.py": code}), "file writing outside gitstore")


@pytest.mark.parametrize(
    "code",
    [
        "open(p, 'w')\n",
        "open(p, mode='a')\n",
        "open(p, 'rb+')\n",
        "open(p, mode)\n",
        "p.open('w')\n",
        "p.open(mode='x')\n",
        "io.open(p, 'w')\n",
        "io.FileIO(p, 'w')\n",
        "from io import FileIO\nFileIO(p, mode='a')\n",
    ],
)
def test_open_for_writing_outside_gitstore(tmp_path: Path, code: str) -> None:
    only(scan(tmp_path, {"cli/a.py": code}), "file writing outside gitstore")


@pytest.mark.parametrize(
    "code",
    [
        "x = open('f')\n",
        "x = p.read_text()\n",
        "x = p.read_bytes()\n",
        "x = p.open()\n",
        "r = open\n",
        "import fileinput\n",
        "import pkgutil\n",
        "from pkgutil import get_data\n",
    ],
)
def test_open_outside_gitstore_and_cli(tmp_path: Path, code: str) -> None:
    only(scan(tmp_path, {"viewer/a.py": code}), "file reading outside gitstore and cli")


PACKAGE_DATA = [
    "from importlib.resources import files\nx = files('lodge.v').joinpath('s.css').read_text()\n",
    "from importlib.resources import files\nx = files('lodge.v').joinpath('s.css').read_bytes()\n",
    "from importlib.resources import files\nx = files('lodge.v').joinpath('s.css').open('r')\n",
    "from importlib.resources import files\nx = (files('lodge.v') / 's.css').read_text()\n",
    "from importlib.resources import files\nROOT = files('lodge.v')\n"
    "x = ROOT.joinpath('s.css').read_text(encoding='utf-8')\n",
    "import importlib.resources as ir\nx = ir.files('lodge.v').joinpath('s.css').read_bytes()\n",
]


@pytest.mark.parametrize("pkg", ["cli", "viewer"])
@pytest.mark.parametrize("code", PACKAGE_DATA)
def test_package_data_may_be_read_through_importlib_resources(
    tmp_path: Path, pkg: str, code: str
) -> None:
    assert scan(tmp_path, {f"{pkg}/a.py": code}) == []


@pytest.mark.parametrize("pkg", ["viewer", "hook"])
@pytest.mark.parametrize(
    "code",
    [
        "x = Path('s.css').read_text()\n",
        "x = p.joinpath('s.css').read_text()\n",
        "ROOT = Path('d')\nx = ROOT.joinpath('s.css').read_bytes()\n",
    ],
)
def test_plain_path_read_outside_cli_still_fails(tmp_path: Path, pkg: str, code: str) -> None:
    only(scan(tmp_path, {f"{pkg}/a.py": code}), "file reading outside gitstore and cli")


def test_package_data_read_in_hook_still_fails(tmp_path: Path) -> None:
    code = "import importlib\nx = importlib.resources.files('x').joinpath('s').read_text()\n"
    found = scan(tmp_path, {"hook/a.py": code})
    assert any("file reading outside gitstore and cli" in v for v in found), found


@pytest.mark.parametrize("pkg", ["cli", "viewer", "hook"])
def test_webbrowser_open_is_not_a_file_open(tmp_path: Path, pkg: str) -> None:
    code = "import webbrowser\nwebbrowser.open('http://localhost:8000/')\nwebbrowser.open(url)\n"
    assert scan(tmp_path, {f"{pkg}/a.py": code}) == []


def test_resources_outside_cli_and_viewer(tmp_path: Path) -> None:
    codes = (
        "from importlib import resources\n",
        "import importlib.resources\n",
        "import importlib\nimportlib.resources.files('x')\n",
    )
    for code in codes:
        only(scan(tmp_path, {"hook/a.py": code}), "importlib.resources outside cli and viewer")


def test_confined_io_is_allowed_where_ruled(tmp_path: Path) -> None:
    files = {
        "gitstore/a.py": (
            "import subprocess, shutil, os\nos.system('x')\nopen(p, 'w')\np.write_text('x')\n"
        ),
        "cli/a.py": (
            "from importlib import resources\nx = open('f')\ny = open(p, 'rb')\n"
            "z = p.open(mode='r')\ncursor.execute('x')\ns = 'a'.replace('a', 'b')\n"
        ),
        "viewer/a.py": "import importlib.resources\n",
        "app/a.py": "import datetime\n\n\ndef f(d):\n    return d.now()\n",
        "core/a.py": "from collections.abc import Mapping\nimport yaml\n",
        "core/b.py": "from lodge.core.a import Mapping\n",
        "main.py": "from lodge import app, cli, core, gitstore, hook, viewer\n",
    }
    assert scan(tmp_path, files) == []
