# Task 1 report: skeleton, structure test, gate script

## Built

- `pyproject.toml` (uv_build backend, `lodge = "lodge.main:main"`, Ruff, mypy strict, Vulture config; Ruff's format excludes `docs`, `README.md`, `CLAUDE.md` because Ruff 0.15 formats Markdown code blocks), `uv.lock`, `scripts/check.sh`, `vulture_allow.py`, `.gitignore` additions.
- `src/lodge/{core,app,gitstore,cli,viewer,hook}/__init__.py` (empty), `src/lodge/main.py` (`main(argv) -> int`, `argparse`, version from `importlib.metadata`).
- `tests/structure_rules.py` (`ALLOWED`, `CORE_MODULES`, `MAX_LINES`, `modules`, `violations`), `tests/test_structure.py`, `tests/test_entry_point.py`.
- Rules: allowed-import table, front doors (including `from P import n` and `from lodge import pkg` resolution), own-front-door import, relative and in-function imports, dynamic imports, unknown packages, root imports nothing, module cycles (Tarjan, `__init__` modules are nodes), 300-line limit in `src` and `tests`, `core`/`app` module allow-list, clock and console names in `core`/`app`, `subprocess` only in `gitstore`, file reading (`open`, `read_text`, `read_bytes`, `.open`) only in `gitstore` and `cli`, `importlib.resources` only in `cli` and `viewer`.

## Red before code

`uv run pytest tests/test_structure.py` with no `structure_rules.py`: `ModuleNotFoundError: No module named 'structure_rules'` (collection error).
With a stub (`ALLOWED = {}`, `violations` returning `[]`): 54 failed, 4 passed (the four are the clean-tree tests: `test_module_at_the_limit_passes`, `test_clock_port_call_is_not_a_clock_read`, `test_confined_io_is_allowed_where_ruled`, `test_real_tree_is_clean`), each failing at `only(...)`: `assert len(found) == 1 and fragment in found[0]` with `found == []`:
every test of `test_core_importing_app`, `test_adapter_importing_adapter`, `test_import_past_front_door`, `test_submodule_through_front_door`, `test_from_lodge_import_package`, `test_import_statement_form`, `test_relative_import`, `test_import_inside_function`, `test_dynamic_import[2]`, `test_own_front_door_import`, `test_unknown_package`, `test_root_imports_nothing`, `test_import_cycle`, `test_import_cycle_through_init`, `test_long_module[src|tests]`, `test_core_disallowed_module[8 x 2]`, `test_core_banned_name[7 x 2]`, `test_subprocess_outside_gitstore`, `test_open_outside_gitstore_and_cli[4]`, `test_resources_outside_cli_and_viewer`, `test_syntax_error_is_reported`.
After the implementation: 58 passed.
`tests/test_entry_point.py::test_version`: `ImportError: cannot import name 'main' from 'lodge.main'`; with a first `main` that let argparse exit: `SystemExit: 0`; fixed by returning argparse's exit code from `main`; passes.

## Gate

`sh scripts/check.sh`: ruff format (17 files unchanged), ruff check passed, mypy strict no issues (11 files), vulture clean, pytest 59 passed.
`uv run lodge --version` prints `lodge 0.1.0.dev0`.

## Concerns

1. Literal ban on naming `now` would reject the plan's own port call `clock.now()` in `app` (plan Task 5: `class Clock(Protocol): def now(...)`, `clock.now()`). Ruling: `now`, `today`, `utcnow`, `fromtimestamp` are banned only as attributes of the `datetime` module's `datetime`/`date` (resolved through the file's imports); `open`, `input`, `print` are banned as any name in `core` and `app`; cost if wrong: an aliased class (`d = datetime; d.now()`) slips through, the `core`/`app` module allow-list still keeps `time`, `os`, and `secrets` out.
2. `vulture_allow.py` holds only the console-script entry point; Vulture also scans `tests`, which uses `main`, so the entry is not yet load-bearing.
3. `.open` as a read attribute is exempt only for a receiver named `webbrowser`; any other `.open()` outside `gitstore` and `cli` is flagged (including `webbrowser.open` via another alias).
4. `uv sync` resolved CPython 3.13.5 here; the tests assume 3.12 or later only.

## Fix round 1 (review `task-1-review.md`, head e447243)

Layout after the split (each module under 300 lines; largest `structure_calls.py`, 202): `tests/structure_tables.py` (tables, `modules`, `package_of`), `tests/structure_imports.py` (edges, front doors, allow-list, import-level I/O and process rules, cycles), `tests/structure_calls.py` (purity, dynamic code, I/O and process calls), `tests/structure_rules.py` (`violations`, layout, size and decoding; re-exports `ALLOWED`, `CORE_MODULES`, `MAX_LINES`, `modules`); tests split into `test_structure.py` (imports, layout, size) and `test_structure_io.py` (purity, I/O, process), helper `tests/structure_tree.py`.
The split was done first as a pure move (gate green, 59 passed); the new tests were then added and run against the unchanged rules: 131 failed, 56 passed (`-o addopts=""`). Failing lines before the code: `AssertionError: []` for every planted violation below, plus `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff` for the two non-UTF-8 tests and, for the root cases, `['lodge/__init__.py:1: root may not import core']` and `['lodge/__init__.py:1: relative import']` (message and rule not yet "root imports nothing").

| Finding | Covering tests (each failed before) |
| --- | --- |
| I1 root imports nothing | `test_root_imports_nothing` (`from lodge.core import x`, `import os`, `from os import path`, `import yaml`, `from . import x`) |
| I2 process spawning only in `gitstore` | `test_process_spawning_outside_gitstore` (11 forms: `os.system`, `os.popen` via alias, `os.execvp`, `os.spawnl`, `os.posix_spawn`, `from os import system`, `asyncio.create_subprocess_exec`, `from asyncio import create_subprocess_shell`, `from asyncio import subprocess`, `multiprocessing`, `pty`; in `cli`, `viewer`, `hook`, `main.py`), `test_subprocess_outside_gitstore` (message now `process spawning outside gitstore: <target>`) |
| I3 file writing only in `gitstore` | `test_file_writing_outside_gitstore` (10 forms: `write_text`, `write_bytes`, `mkdir`, `touch`, `unlink`, `os.open`, `os.replace`, `from os import remove`, `shutil`, `tempfile`; in four packages), `test_pure_packages_do_not_write_files`, `test_open_for_writing_outside_gitstore` (`open` with `w`, `a`, `+`, a computed mode, `Path.open('w')`, `io.open`) |
| M1 `core` names the clock on any receiver | `test_core_names_the_clock_on_any_receiver` (`d.now()`, `d.today()`, `d.utcnow()`, `d.fromtimestamp(0)`); `test_confined_io_is_allowed_where_ruled` keeps `d.now()` legal in `app` |
| M2 dynamic code | `test_dynamic_code` (`exec`, `eval`, `compile` in `core`, `app`, `cli`), `test_dynamic_import` (new: `from importlib import import_module as im`, `getattr(importlib, 'import_module')`) |
| M3 missing front door | `test_missing_front_door`, `test_package_directory_without_init`; `test_real_tree_is_clean` asserts each `lodge.<pkg>` is a module |
| M4 non-UTF-8 source | `test_source_that_is_not_utf8_names_the_file` (`src` and `tests`) |
| M5 indirect I/O | `test_open_outside_gitstore_and_cli` (new: `r = open`, `fileinput`, `pkgutil`, `from pkgutil import get_data`), `test_resources_outside_cli_and_viewer` (new: `importlib.resources.files(...)` as an attribute chain) |
| M6 gate shows the count | `addopts = "-q"` removed; the gate's pytest line now ends `187 passed` |

Confinement kept legal (in `test_confined_io_is_allowed_where_ruled`): in `gitstore` `subprocess`, `shutil`, `os.system`, `open(p, 'w')`, `write_text`; in `cli` `open`, `open(p, 'rb')`, `Path.open(mode='r')`, `importlib.resources`, `cursor.execute(...)`, `str.replace`.
Judgement calls: `rename`/`replace` count as writes only on `os` (`str.replace` is everywhere); a computed `open` mode counts as writing; `shutil` and `tempfile` are banned by import outside `gitstore`; `app` keeps the resolved `datetime` attribute rule (an aliased class, `d = datetime.datetime; d.now()`, still passes there).

Command: `sh scripts/check.sh`; output: ruff format `22 files already formatted`, ruff `All checks passed!`, mypy `Success: no issues found in 16 source files`, vulture clean, pytest `187 passed in 0.30s`.

## Fix round 2 (recheck `task-1-recheck-1.md`, head c64fdf2)

Tests added first, run against the unchanged rules: 23 failed, 200 passed (`-o addopts=""`); every failing line `AssertionError: [...]` listing the false rejection (`lodge/viewer/a.py:1: file reading outside gitstore and cli: read_text`, `...: file writing outside gitstore: open for writing`) or `AssertionError: []` for a violation not reported.

| Finding | Covering tests (failed before unless a guard) |
| --- | --- |
| O1 package data readable in `viewer` and `cli` | `test_package_data_may_be_read_through_importlib_resources` (`files(...).joinpath(...)` with `read_text`, `read_bytes`, `open('r')`; `(files(...) / 's.css').read_text()`; a name bound from `files(...)`; `importlib.resources as ir`; the 6 `viewer` cases failed, `cli` passed already) |
| O1 guard: a plain path still fails | `test_plain_path_read_outside_cli_still_fails` (`Path(...).read_text()`, `p.joinpath(...).read_text()`, a `Path` bound to a name, in `viewer` and `hook`), `test_package_data_read_in_hook_still_fails`; these passed before and after |
| N1 `webbrowser.open(url)` | `test_webbrowser_open_is_not_a_file_open` (a literal URL and a variable, in `cli`, `viewer`, `hook`; 3 failed) |
| N2 | `test_file_writing_outside_gitstore` gains `p.rename(q)`, `p.symlink_to(q)`, `p.hardlink_to(q)` (12 failed); `test_open_for_writing_outside_gitstore` gains `io.FileIO(p, 'w')` and `FileIO(p, mode='a')` (2 failed) |

Rule: a read attribute passes when its receiver chain, followed through calls, attributes, `/`, and names bound from such a chain, starts at a call of `files(...)`, in `viewer` (`cli` reads anything); `webbrowser` receivers are never file opens; `rename`, `symlink_to`, `hardlink_to` are writes; `FileIO(...)` is checked for its mode like `open`.
Residual: any function named `files` in `viewer` is taken for `importlib.resources.files`.

Command: `sh scripts/check.sh`; output: ruff format `22 files already formatted`, ruff `All checks passed!`, mypy `Success: no issues found in 16 source files`, vulture clean, pytest `223 passed in 0.36s`; largest module `structure_calls.py`, 243 lines.
