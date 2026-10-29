# Task 1 recheck 1: fix round `e447243..6680130`

Rechecker: `rechecker` (Opus), against `task-1-review.md` (I1, I2, I3, M1 to M6, and the split), in a detached scratch worktree at `6680130`.

## What I ran

- `sh scripts/check.sh` at `6680130`: ruff format, ruff, mypy (16 source files), and vulture clean; pytest `187 passed in 0.30s`, the count now printed by the gate itself.
- A probe script (`scratchpad/probe/probe.py`) building a throwaway tree per probe like `tests/structure_tree.py::scan` and calling `violations()`; 66 probes run against the fixed rules (`tests/` at `6680130`) and against the old `tests/structure_rules.py` from `e447243` for comparison.
- Results: every planted violation for I1, I2, M1 to M5 caught; I3 caught in 15 of 19 forms; 3 of 14 allowed-code probes wrongly rejected, 1 of them new in this fix (see below).

## Verdicts per finding

- I1: answered, `tests/structure_imports.py:34-36`.
  Caught: `import os`, `from os import path`, `import json`, `from importlib.metadata import version`, and an import inside a function, all in `src/lodge/__init__.py`, each as "root imports nothing".
- I2: answered, `tests/structure_calls.py:29-31,94-95,110-111,129-137,196-200` and `tests/structure_imports.py:9,92-94`.
  Caught outside `gitstore`: `os.system` (cli), `os.popen` (main.py), `os.execvp` (hook), `os.spawnvp` (viewer), `os.posix_spawnp`, `os.fork`, `os.execl`, `asyncio.create_subprocess_exec` (main.py), `import asyncio.subprocess`, `from multiprocessing import Process`, `from os import popen as p`, `import os.path` then `os.system`, `import pty`.
- I3: answered for the forms the review named, with a residual (Minor, below), `tests/structure_calls.py:14-28,125-133,159-189,201-202` and `tests/structure_imports.py:10,95-96`.
  Caught outside `gitstore`: `Path(...).write_text` in cli, viewer, and main.py; `open(p, 'w')`, `open(p, 'a', encoding=...)`, `open(file=p, mode='x')`, `Path(p).open('w')` in cli; `os.rename` (hook); `os.makedirs`; `shutil`; `p.unlink()`.
- M1: answered, `tests/structure_calls.py:140-145`; `d.now()` and `d.date.today()` caught in `core`; `app` keeps the resolved rule (`dt.datetime.now()` caught, the aliased class `d = datetime.datetime; d.now()` still passes, as the report's judgement call says).
- M2: answered, `tests/structure_calls.py:90-93,161-168,194-195`; caught: `exec` (core), `eval` (app), `compile` (main.py), `from importlib import import_module as im`, `getattr(importlib, 'import_module')(...)`; `re.compile` in core still passes.
- M3: answered, `tests/structure_rules.py:45-58` and `tests/test_structure.py` (`test_real_tree_is_clean` asserts each `lodge.<pkg>`); caught: deleted `core/__init__.py` with `core/x.py` present, deleted `hook/__init__.py`, `app/sub/x.py` without `__init__.py`.
- M4: answered, `tests/structure_rules.py:33-36`; a `0xff` byte in `core/a.py` gives `lodge/core/a.py: not UTF-8`.
- M5: answered, `tests/structure_calls.py:96-100,112-117` and `tests/structure_imports.py:11,97-100`; caught: `r = open; r(p)` (viewer), `fileinput.input()` and `pkgutil.get_data` (hook), `importlib.resources.files(...)` as an attribute chain and `import importlib.resources as ir` (hook).
- M6: answered, `pyproject.toml` (`addopts` removed); the gate prints `187 passed`.
- Split under 300 lines: answered; largest module `tests/structure_calls.py` at 202 lines, the real-tree size check passes.

## Test diff

No old assertion was weakened: the moved tests keep their cases, `test_subprocess_outside_gitstore` changes only its expected message, and `test_confined_io_is_allowed_where_ruled` gains cases.
One allowed case left that test (`from lodge.core import Snapshot` in `app`); my probe of it still passes, and other edge tests cover allowed `lodge` imports.

## New problems

### N1 (Minor): `webbrowser.open(url)` is now reported as opening a file for writing

- Handle: `tests/structure_calls.py:173-175`; `_call` treats every `.open(...)` call outside `os` as a file open and reads argument 0 as its mode, with no `webbrowser` exemption (the one at `:123` covers only the read rule).
- Failure: `import webbrowser; webbrowser.open(url)` in `viewer` gives `file writing outside gitstore: open for writing` (a non-constant argument counts as a write mode), and `webbrowser.open('http://localhost:8000/')` does too, because the URL contains `a`; both passed at `e447243`, and the first review listed `webbrowser.open` in `viewer` as correctly allowed.
  The plan's Task 11 does not name `webbrowser`, so no planned code hits this yet; the same misreading applies to any `x.open(arg)` in `cli` (`tarfile.open(p)`, `gzip.open(p)`).
- Fix: in `_call`, check the mode only when the receiver is a `Path`-like call or name not in an exempt set, at minimum skipping owner `webbrowser` as `:123` does; add `webbrowser.open(url)` in `viewer` to `test_confined_io_is_allowed_where_ruled`.

### N2 (Minor, I3 residual): `Path.rename`, `Path.replace`, `symlink_to`, and `io.FileIO(p, 'w')` pass outside `gitstore`

- Handle: `tests/structure_calls.py:14` (`WRITE_ATTRS`) lacks `rename`, `replace`, `symlink_to`, `hardlink_to`; `:173-175` checks the mode of `.open` only.
- Failure: `p.rename(q)`, `p.replace(q)`, `p.symlink_to(q)`, and `io.FileIO(p, 'w')` in `cli` all pass; a `cli` command that moves a record file bypasses the store.
  The report's reason for leaving out `replace` (`str.replace` is everywhere) holds; it does not cover `rename`, `symlink_to`, or `hardlink_to`, which no `str` or `dict` method shares.
- Fix: add `rename`, `symlink_to`, and `hardlink_to` to `WRITE_ATTRS`; leave `replace` to the `os` rule; park `io.FileIO` as an evasion rather than a habit.

## Observation outside this fix (pre-existing at `e447243`)

### O1 (Important for Task 11): `viewer` cannot read its own package data

- Handle: `tests/structure_calls.py:123` (`READ_ATTRS` = `read_text`, `read_bytes`, `open` on any receiver outside `gitstore` and `cli`).
- Failure: `files('lodge.viewer').joinpath('style.css').read_text(encoding='utf-8')` in `viewer` gives `file reading outside gitstore and cli: read_text`; `read_bytes()` and `.open()` fare the same.
  `files('lodge.viewer')` alone passes, as the dispatch asked, but the plan's Task 11 serves `/style.css` from package data in `viewer` (plan lines 459 and 466) and the Global Constraints allow `importlib.resources` there (plan line 22), so the Task 11 builder meets a rule it may not loosen (`CLAUDE.md`, "never loosen a rule to pass").
  Same result at `e447243`, so not introduced by this fix.
- Fix: in `viewer` (and `cli`, for consistency), allow `READ_ATTRS` on a receiver whose chain starts at a call to `files` bound from `importlib.resources`; add the `style.css` read to the allowed-code test.

## Allowed code later tasks need

Pass at `6680130`: `clock.now()` and `self.clock.now()` in `app`; `subprocess.run`, `Path.write_text`, `tempfile.NamedTemporaryFile`, `os.open(..., O_CREAT | O_EXCL)`, and `os.unlink` in `gitstore`; `Path.read_text` and `importlib.resources.files('lodge.cli').joinpath('guide.md').read_text()` in `cli`; `importlib.resources.files('lodge.viewer')` and an `http.server` handler writing to `self.wfile` in `viewer`; `sys.stdin.read()`, `json.load(sys.stdin)`, and `sys.stdout.write` in `hook`; `secrets.token_bytes(8)`, `datetime.now().astimezone()`, and `print(..., file=sys.stderr)` in `main.py`; `re.compile` in `core`; `str.replace` in `cli`.
Rejected: the `viewer` package-data read (O1, pre-existing) and `webbrowser.open` (N1, new).

## Counts

Findings answered: 10 of 10 (I1, I2, I3, M1 to M6, split), I3 with a Minor residual.
New: 0 Blocking, 0 Important, 2 Minor (N1, N2).
Outside the fix: 1 Important for Task 11 (O1), pre-existing.
