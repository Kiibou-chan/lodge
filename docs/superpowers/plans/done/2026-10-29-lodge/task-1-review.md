# Task 1 review: skeleton, structure test, gate script

Reviewer: `reviewer` (Opus), range `e87a528..b975932`, reviewed at `b975932` in a detached scratch worktree.

## Verdicts

- Spec compliance: **no**, one gap.
  The brief's Step 3 says "the root `lodge/__init__.py` may import nothing"; the implementation enforces this only for `lodge` targets, so `import os` in the root passes (I1).
  Every other item the brief names is present and verified by probe below.
- Task quality: **not approved**: 0 Blocking, 3 Important, 6 Minor.

## What I ran

- `sh scripts/check.sh` at `b975932`: ruff format (17 files), ruff check, mypy (11 files), and vulture all clean; pytest green, 59 passed (counted with `uv run pytest -o addopts="" -q`, since the gate itself prints no count, see M6).
- `uv run lodge --version` was not rerun; `test_version` covers it in-process and passes.
- Tag `v0.1.0.dev0` is on `origin` at `b975932` (`git ls-remote --tags origin`).
- Commit `b975932` carries the repository's identity and the `Co-Authored-By: Claude <noreply@anthropic.com>` trailer that `CLAUDE.md` prescribes.
- The report's red-before-code runs (collection error, then 54 failed and 4 passed against a stub) cannot be replayed from the history, since the task is one commit; I took them as reported.

## Probes of `violations()`

Script: a throwaway tree per probe built like `tests/test_structure.py::scan`, calling `violations()` from the branch's `tests/structure_rules.py`.
86 probes; CAUGHT means at least one violation reported.

Named in the brief, all CAUGHT with the expected message: `core` importing `app`; `cli` importing `gitstore`; `from lodge.core.check import run` in `app`; `from lodge.core import check` with `core/check.py` present; `from lodge import gitstore` in `cli`; `import lodge.gitstore.git as g` in `cli`; `from ..gitstore import x`; import inside a function; `importlib.import_module` and `__import__` in `viewer`; `from lodge.core import Snapshot` in `core/check.py`; `src/lodge/importer/`; a two-module cycle; a 301-line module; `import os` and `import secrets` in `core`; `dt.datetime.now()`, `date.today()`, `open(...)`, and `print(...)` in `core` or `app`; `import subprocess` in `cli`.

Not named in the brief, CAUGHT: `gitstore` importing `cli`; `app` importing `gitstore`; `hook` importing `viewer`; `from lodge import main` in `cli`; `import lodge` in `cli`; `import lodge.core` inside `core`; a `TYPE_CHECKING` import from `cli` into `gitstore`; `import subprocess` in a class body; imports in a method and in an `async def`; a three-module cycle; a self-import; a cycle closed by a function-level import; a cross-package cycle between `app` and `core` through both front doors; `from lodge.core.sub import x` past the front door; `__future__`, `collections`, `from os import path`, `importlib`, `uuid`, and `socket` in `core`; `functools.partial(datetime.now)` in `core`; `from datetime import datetime as C; C.today()` in `app`; `r = open` in `core`; `input()` in `core`; `io.open` and `os.open` in `viewer`; `Path.read_text` in `hook`; `open` in `main.py` and in the root; `import subprocess` in `main.py` and in the root; `from importlib.resources import files` in `hook`; `src/lodge/__main__.py` and `src/lodge/util.py` as unknown packages; a 301-line `tests/sub/test_a.py`.

Not named in the brief, MISSED (each a finding below): `import os` in the root (I1); `os.system`, `os.popen`, `os.execvp`, `asyncio.create_subprocess_exec`, and `import multiprocessing` outside `gitstore` (I2); `Path.write_text` in `viewer` and in `cli` (I3); `.now()` on any receiver in `core`, and `d = datetime.datetime; d.now()` and `getattr(datetime, "now")()` in `app` (M1); `from importlib import import_module as im; im(...)`, `getattr(importlib, "import_module")(...)`, `exec(...)` in `core`, and `eval(...)` in `app` (M2); a package directory without `__init__.py` (M3); `r = open; r(p)` in `viewer`, `fileinput.input()` and `pkgutil.get_data` in `hook`, and `import importlib; importlib.resources.files(...)` in `hook` (M5).
Non-UTF-8 source crashes `violations()` with a bare `UnicodeDecodeError` (M4).

Correctly allowed: `webbrowser.open` in `viewer`, `import os` in `gitstore`, `sys.stdin.read()` in `hook`, a 300-line test file, and `clock.now()` in `app`.

Real tree: in the scratch worktree I deleted `src/lodge/core/__init__.py`, added `core/x.py`, put `import os` in `src/lodge/__init__.py`, and put `os.system("git status")` plus `Path("lodge/d-x.md").write_text("x")` in `cli/a.py`; `test_real_tree_is_clean` still passed.

## Correctness

### I1 (Important): the root package may import any non-`lodge` module

- Handle: `tests/structure_rules.py:136` sends every non-`lodge` target to `_outside_edge`, which (`:155-164`) has no case for `ROOT`; only `lodge` targets reach the `ALLOWED` lookup that rejects root edges (`:148`).
- Brief: Step 3, "the root `lodge/__init__.py` may import nothing".
- Failure: `import os` (or `yaml`, `json`, anything) in `src/lodge/__init__.py` passes; that module runs on every `import lodge.<anything>`, including in `core`'s tests, so a side effect there reaches the pure packages unseen.
- Fix: in `_imports`, when `pkg == ROOT`, report every `Import` and `ImportFrom` ("root imports nothing"); add `test_root_imports_nothing` cases for `import os` and `from os import path`.

### I2 (Important): process spawning outside `gitstore` passes

- Handle: `tests/structure_rules.py:160-161` matches only the module name `subprocess`.
- Spec: line 288 (LODGE-5), "`gitstore` is the only package that touches git".
- Failure: `os.system("git push")`, `os.popen("git log")`, `os.execvp`, `os.spawn*`, `os.posix_spawn`, `asyncio.create_subprocess_exec`, and `multiprocessing` all pass in `cli`, `viewer`, `hook`, and `main.py`; `main.py`, which plan Task 10 says "finds the repository", is the likeliest place for an agent blocked from `subprocess` to reach for `os.popen("git rev-parse ...")`.
- Fix: outside `gitstore`, report an attribute call whose name is `system`, `popen`, or `startfile`, or starts with `exec`, `spawn`, `posix_spawn`, or `fork`, any `create_subprocess_exec` or `create_subprocess_shell`, and imports of `multiprocessing`, `pty`, and `asyncio.subprocess`; one parametrised test over these forms.

### I3 (Important): writing files is not confined at all

- Handle: `tests/structure_rules.py:36` (`READ_ATTRS`) and `:220-225` check only reads; `open` with a write mode in `cli` passes by the `gitstore` and `cli` exemption.
- Spec: line 288, "`gitstore` is the only package that touches git or the record files"; `CLAUDE.md`, "Record files are written only through `lodge add`".
- Failure: `Path("lodge/d-x.md").write_text(...)` in `cli` or `viewer` passes, as does `open(p, "w")` in `cli`; a `cli` command that writes a record or `.lodge.toml` itself bypasses the store, its lock, and the check, and no test notices.
- Fix: outside `gitstore`, report `write_text`, `write_bytes`, `mkdir`, `touch`, `unlink`, `rename`, and `replace`, and `open` calls whose mode argument contains `w`, `a`, `x`, or `+`; no other package in the plan writes files (Task 10 wires `init` from `main`).
  The plan's Global Constraints list only reading, so this enforces the half of the spec's rule the plan did not restate; a ledger line suffices, no question for the author.

## Practice

### M4 (Minor): non-UTF-8 source crashes without naming the file

- Handle: `tests/structure_rules.py:64` (`path.read_text(encoding="utf-8")`), and `:76` for tests.
- Failure: a stray Latin-1 byte gives `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 5` with no path; the gate still fails, but the reader has to hunt for the file.
- Fix: catch `UnicodeDecodeError` and report `f"{rel}: not UTF-8"`, as the `SyntaxError` branch already does.

### M6 (Minor): the gate prints no test count

- Handle: `pyproject.toml:21` (`addopts = "-q"`) plus `scripts/check.sh:7` (`pytest -q`) gives `-qq`.
- Failure: the green gate ends in a line of dots with no "59 passed", so a report or ledger line quoting the count cannot be read off the gate's own output (this review's count came from a separate run).
- Fix: drop `addopts = "-q"`; the brief puts `-q` in `check.sh`.

## Design

### M1 (Minor): the adopted clock ruling is weaker than it needs to be in `core`

- Handle: `tests/structure_rules.py:181-192` (`_reads_clock`) and `:207-212`; ledger, "Task 1: Ruling (builder's, adopted)".
- Judgement: in `app` the ruling does its job.
  It catches every habitual form (`datetime.now()`, `dt.datetime.now()`, `date.today()`, aliased imports, `partial(datetime.now)`) and lets the Clock port's `clock.now()` through, which plan Task 8 (`class Clock(Protocol): def now(...)`, "The date is `clock.now()`") requires.
  The residual holes are an aliased class (`d = datetime.datetime; d.now()`), `getattr(datetime, "now")`, and `.now()` on a datetime instance (`decision.date.now()`), none of them a habitual form.
- Gap: `core` has no Clock port (Task 8 puts `Clock` in `lodge.app`; the spec says "the time and ID entropy come in as parameters"), so the relaxation buys `core` nothing, yet `core` now accepts `.now()` on any receiver, including a datetime instance passed in.
- Fix: in `core`, report `now`, `today`, `utcnow`, and `fromtimestamp` as attributes on any receiver (the plan's literal rule); keep the resolved form in `app` only; add one test for `def f(d): return d.now()` in `core`.

### M2 (Minor): dynamic code bypasses every import rule

- Handle: `tests/structure_rules.py:35` and `:216-219` match `import_module` and `__import__` by the called name only.
- Failure: `from importlib import import_module as im; im("lodge.gitstore")` in `cli`, `getattr(importlib, "import_module")(...)`, and `exec("import os")` in `core` all pass, and the last voids `core`'s whole allow-list.
  These are evasions rather than habits, hence Minor.
- Fix: report the names `exec`, `eval`, and `compile` anywhere in `src`, and any `ImportFrom` of `import_module` from `importlib`.

### M3 (Minor): a missing front door goes unreported

- Handle: `tests/test_structure.py:185-186` derives the visited packages from submodule names; `violations()` never checks that `lodge/<pkg>/__init__.py` exists.
- Failure: delete `src/lodge/core/__init__.py` with any other module left in `core` and `test_real_tree_is_clean` passes (verified in the scratch worktree); `lodge.core` becomes a namespace package with no front door, and edges to it attach to the root node in the cycle graph.
- Fix: in `violations()`, report each `ALLOWED` package except `main` whose `__init__.py` is absent; in the test, assert `f"lodge.{p}" in modules(...)` for each package.

### M5 (Minor): name-based I/O rules miss indirect forms

- Handle: `tests/structure_rules.py:222-225` and `:162`.
- Failure: `r = open; r(p)` in `viewer`, `fileinput.input()` and `pkgutil.get_data(...)` in `hook`, and `import importlib; importlib.resources.files(...)` in `hook` all pass; "`hook` reads stdin only" (Global Constraints) is enforced only as "`hook` opens no file".
- Fix: outside `gitstore` and `cli`, report the name `open` in any position, not only as a call, and imports of `fileinput` and `pkgutil`; outside `cli` and `viewer`, report the attribute chain `importlib.resources`.

### Note: room for the fixes

`tests/structure_rules.py` is 258 lines; I1, I2, I3, and the Minors will take it near the 300 limit it enforces.
Split it in the fix round, for example `structure_imports.py` (targets, edges, cycles) and `structure_calls.py` (purity, I/O), with `structure_rules.py` keeping the tables and `violations`.

## Files

Read: `.claude/agents/reviewer.md`; `CLAUDE.md`; `task-1-brief.md`; `task-1-report.md`; the plan's Global Constraints, Task 1, Task 8 interfaces, and the Task 10 line on `main`; the spec's Structure section and its LODGE-5 line (288); the ledger's Task 1 lines; at `b975932`: `tests/structure_rules.py`, `tests/test_structure.py`, `tests/test_entry_point.py`, `src/lodge/main.py`, `pyproject.toml`, `scripts/check.sh`, `vulture_allow.py`, the `.gitignore` diff, and the list of empty front doors.
Not read: `uv.lock` (generated); the review package's diff file itself, since I read the same files at `b975932` directly.
