# Task 1 recheck 2: fix round `c64fdf2..3eb75ce`

Rechecker: `rechecker` (Opus), against `task-1-recheck-1.md` (O1, N1, N2 only), in a detached scratch worktree at `3eb75ce` (`.claude/worktrees/recheck-t1-2`, removed after).

## What I ran

- `sh scripts/check.sh` at `3eb75ce`: ruff format, ruff, mypy (16 source files), and vulture clean; pytest `223 passed in 0.33s`.
- A probe script (`scratchpad/probe2/probe.py`) calling `tests/structure_tree.py::scan` on a throwaway tree per probe; 46 probes against the rules at `3eb75ce`, and the same probes against the rules copied from `c64fdf2` to tell regressions from pre-existing gaps.
- A second script (`scratchpad/probe2/fp.py`) for package-data forms the exemption does not follow.

## Verdicts per finding

- O1: answered, `tests/structure_calls.py:137,143-165`.
  Pass in `viewer`: `files('lodge.viewer').joinpath('style.css').read_text(encoding='utf-8')`, `.read_bytes()`, `.open()`, `importlib.resources.files(...)` as an attribute chain, and `root = files(...)` then `(root / 'style.css').read_text()` inside a function.
  Fail in `viewer`: `Path('style.css').read_text()`, `(Path(__file__).parent / 'style.css').read_text()`.
  The exemption does not reach other packages: the same `files(...)` read fails in `hook` and `main.py` (reading and `importlib.resources` both reported) and in `core` and `app` (import and reading reported), because `_reads_package_data` requires `scope.pkg == "viewer"` (`:165`).
  It does open holes inside `viewer`; see R1 to R3.
- N1: answered, `tests/structure_calls.py:163-164,223`.
  `webbrowser.open(url)`, `webbrowser.open('http://localhost:8000/')`, and `webbrowser.open_new_tab(url)` pass in `viewer` and `cli`; `p.open('w')` in `viewer` is still caught.
  Not covered, acceptable: `import webbrowser as wb; wb.open(url)` and `webbrowser.get().open(url)` are still reported as file opens, since the exemption matches the literal name `webbrowser` only; `tarfile.open(p)` in `cli` is still reported as writing (the recheck-1 aside, not a finding).
- N2: answered, `tests/structure_calls.py:14-24,211,215`.
  Caught in `cli`, `hook`, and `main.py`: `p.rename(q)`, `p.symlink_to(q)`, `p.hardlink_to(q)`; caught in `cli`: `io.FileIO(p, 'w')`, `from io import FileIO; FileIO(p, mode='a')`.
  Still pass in `gitstore` (all four) and `cli` (`io.FileIO(p)`, `str.replace`).
  Known cost, accepted by the recheck-1 fix: `df.rename(columns=m)` in `cli` is reported as a write.
  Residual, below Minor: `from io import FileIO as F; F(p, 'w')` passes, since `:211` matches the name `FileIO` only.

## Test diff

No assertion weakened: the diff only adds cases to `WRITING` and to `test_open_for_writing_outside_gitstore`, and adds four tests.
The new guard tests check plain-path reads in `viewer` and `hook` and a package-data read in `hook`, but none checks a package-data open for writing in `viewer`, which is how R1 got through.

## New problems

### R1 (Minor, regression): a package-data `open` for writing passes in `viewer`

- Handle: `tests/structure_calls.py:218-224`; `_opens_a_file` returns `False` for any receiver `_reads_package_data` accepts, so `_call` (`:213`) never checks the mode.
- Failure: in `viewer`, `files('lodge.viewer').joinpath('s.css').open('w')` and `ROOT = files('lodge.viewer'); ROOT.joinpath('s').open(mode='a')` give no violation at `3eb75ce`; at `c64fdf2` both gave `file writing outside gitstore: open for writing`.
  `files()` returns a `pathlib.Path` for an installed directory package, and `/` with an absolute string replaces the root, so `(files('lodge.viewer') / some_path).open('w')` writes anywhere.
  `write_text` on the same receiver is still caught (`:139`), so only `open` regressed.
- Fix: in `_opens_a_file`, exempt only the browser (`webbrowser` receiver), not package data, so a package-data `open` still has its mode checked; the read check at `:137` keeps its package-data exemption.
  Add `files('x').joinpath('s').open('w')` in `viewer` to `test_open_for_writing_outside_gitstore` (parametrise it over `cli` and `viewer`).

### R2 (Minor): a name bound once to package data is package data everywhere in the module

- Handle: `tests/structure_calls.py:71-73` collects every `Assign` target bound to a `files(...)` chain into one module-wide set and never removes a name; `:158` trusts the set.
- Failure: in `viewer`, `def css(): path = files('lodge.viewer') / 'style.css'; ...` followed by `def record(root): path = Path(root) / 'choices.md'; return path.read_text()` passes (at `c64fdf2` the second read was reported); so does a parameter sharing the name, `ROOT = files('lodge.viewer')` then `def record(ROOT): return ROOT.joinpath('d.md').read_text()`.
  `path` and `root` are the names a viewer handler reaching for a record file would use, so the store bypass LODGE-5 forbids passes silently in exactly the module that serves package data.
- Fix: treat a name as package data only when every binding of it in the module is a package-data expression: collect all bound names (assignment, annotated and augmented assignment, function parameters, `for`, `with ... as`, comprehension, and walrus targets) and drop from `package_data` any name also bound otherwise.
  Add both forms above to `test_plain_path_read_outside_cli_still_fails`.

### R3 (Minor, the residual the report names, wider than named): `files` is matched by spelling

- Handle: `tests/structure_calls.py:148-150` accepts a call of any name `files` and of any attribute `.files` on any receiver.
- Failure: in `viewer`, `files = Path`, `from pathlib import Path as files`, `def files(p): return Path(p)`, each followed by `files('/r/x.md').read_text()`, and `self.files('/r/x.md').read_text()`, all pass; each was reported at `c64fdf2`.
  The report's residual names only "any function named `files`"; the attribute form on any receiver (`self.files`, `repo.files`) is the more likely accident.
- Fix: track the names bound by `from importlib.resources import files [as f]` and the aliases of `importlib.resources` (as `_collect_aliases` does for `os`), and accept only those names and `<alias>.files` / `importlib.resources.files`.
  Add the four forms above to the plain-path guard test.

## Observation (not a finding)

Package-data forms the exemption does not follow are still rejected in `viewer`: an annotated binding (`ROOT: Traversable = files(...)`), an attribute binding (`self.root = files(...)`, then `self.root.joinpath(...).read_text()`), and `with as_file(files(...) / 's') as p: p.read_text()`.
Task 11 has a passing form (`files('lodge.viewer').joinpath('style.css').read_text()` direct, or a module-level `ROOT = files(...)`), so this costs style, not a rule change.

## Counts

Findings answered: 3 of 3 (O1, N1, N2).
New: 0 Blocking, 0 Important, 3 Minor (R1 regression of a write check, R2 and R3 holes in the O1 exemption, all three `viewer` only and all in `tests/structure_calls.py`).
Recommendation: take R1 to R3 now rather than parking them, since the next round touching `tests/structure_calls.py` may be far off and Task 11 is the first code they bear on.
