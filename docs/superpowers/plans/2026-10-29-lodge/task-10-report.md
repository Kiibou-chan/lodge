# Task 10 report: the command line, the guide, and the composition root

Status: DONE_WITH_CONCERNS (concerns below are small deviations, each with its reason).

## What was built

- `src/lodge/cli/parser.py`: argparse grammar, one frozen dataclass per command, `parse(argv) -> Command | int` (the int is the exit status when argparse has already answered, for `--help`, `--version`, and usage errors).
- `src/lodge/cli/commands.py`: `run(argv, make_lodge, init, view, hook) -> int`, one `match` over the command; reads draft files for `add` (UTF-8, errors as one-line `LodgeError`s naming the file).
- `src/lodge/cli/output.py`: the printed forms (freshness line, `problem:` lines, level-1 blocks, `## Reasoning`, `## Provenance`, `feedback:`, `note:`, `check <n>:`, the outcome line).
- `src/lodge/cli/guide.md`: 54 lines, one sentence per line, read with `importlib.resources`.
- `src/lodge/main.py`: composition root; `_make_lodge` and `_init` find the repository and load settings lazily, so `--version`, `guide`, and `hook` run anywhere; one `except LodgeError` prints `lodge: <message>` and returns its code; `_view` raises `LodgeError("the viewer is not built yet")`; `_hook` reads stdin, swallows `OSError`/`ValueError`, returns 0.
- `pyproject.toml`: registers the `slow` marker only; uv_build ships `guide.md` without a package-data setting (the wheel test proves it).
- Tests: `tests/e2e/` (`__init__.py`, `conftest.py`, `support.py`, one file per command as the brief names them, plus `test_add_dry_run.py`, `test_add_import.py`, `test_view.py`), and `tests/test_wheel.py`.

## Test-first evidence

Before any code, `uv run pytest tests/e2e tests/test_wheel.py --ignore=tests/e2e/test_view.py` gave `76 failed, 1 passed` (the one pass was `--version`); `tests/e2e/test_view.py` failed at collection with `ImportError: cannot import name 'run' from 'lodge.cli'`.
After the first implementation, 8 failed: the guide file was missing (3), and 5 were wrong test assumptions fixed afterwards (see below).

## Result

`sh scripts/check.sh` green: ruff format and check, mypy strict (130 files), vulture, 885 tests passed in about 17 s, `test_installed_wheel_runs` included (it ran, uv reached its cache and network; it skips with a stated reason when uv reports no network).

## Output forms, as built

- Reads (`search`, `show`, `waiting`, `spec`, `check`): freshness line when not `None`, then `problem: <path>:<line>: <message>` per unrecorded problem (the `:<line>` appears only when the problem has one), then the body.
  `search` and `waiting` print `format_level1` blocks separated by one blank line, or `no matches` / `nothing waits for the author`.
- `show`: level 1, then `## Reasoning` and `## Provenance` in that order when asked; an empty section prints `none recorded`.
- `draft` and `guide` print the text exactly, without an added newline; `draft` has no freshness line since it is a file to save.
- `add`: `feedback: <id>: <message>`, `note: <text>`, `check <n>: <message>`, then `published <ids>`, `staged <ids>`, or `not published: the check failed`; IDs separated by spaces, in draft order; "nothing changed" prints `note: nothing changed` and `published` alone.
  `--dry-run` appends `dry run: nothing published`, after `not published: the check failed` when the check fails; exit 1 on a failed check or a `Conflict`.
- `check`: `ok` or the `check <n>:` lines, then `note:` lines; problems already shown as `problem:` lines are not repeated; exit 1 when not `ok`.
- `hook`: any argv starting with `hook` (other than `-h`/`--help`) skips argparse, so the route never exits 2; `post-tool-use` calls the hook callable, any other event exits 0 silently.

## Deviations and concerns

1. `test_add_non_string_scalar_exits_2` uses `title: [a, b]` (a list), not `title: no`: `load_yaml` keeps every scalar as text (`tests/core/test_yamlio.py:6-10`), so `title: no` is accepted as the title "no"; a companion test pins that.
   The plan's Review Focus 2 wording ("a non-string scalar (`title: no`)") predates that core ruling.
2. `check <n>:` lines carry the message only (as the brief says); core messages from `problem_at` start with the record ID, but check 7 area problems carry only the area text.
3. `search` takes an optional QUERY (an empty one lists what the filters allow), a superset of the brief's `search QUERY`.
4. `main` calls `reconfigure(errors="replace")` on stdout and stderr, so a record with a character the terminal cannot encode never ends in a traceback.
5. e2e tests patch `lodge.main.datetime` with a clock that advances a minute per reading: two adds inside one second tie on date, and the review flag (newest change wins, ties by ID) then depends on the random IDs.
   Real use is not affected; the test for the flag needed it.
6. `tests/e2e/test_view.py::test_view_is_not_built_yet` pins the placeholder; Task 11 replaces it.
7. The unrecorded problem `problem:` line includes `:<line>`, an addition to the brief's `<path>: <message>` form.

## Fix round 1

- I1: `Clock.sleep(seconds)` on the port (real: `time.sleep`; the fakes advance their time); `add` reads the clock until its whole second is later than the newest decision in the current tree (at most three waits, then check 1 refuses a decision still ahead); `check_change` takes the current state and dates a new decision after its decisions too; tests `tests/app/test_writes_dates.py`, `tests/core/test_check_current.py`, `tests/e2e/test_same_second.py` (checkout: the agent edit is flagged; branch: the chain publishes and the gate passes; both fail with the wait switched off), commit 58c64f4.
- I2: `lodge add --attach PATH` (repeatable, one flag per file, so `FILE...` stay positional) reads each file as exact UTF-8 text, and `Lodge.add(..., attachments)` writes it to `lodge/attachments/<new decision id>/<base name>` in the same publish; refused with one sentence when the add creates no decision or several, when a name is not a plain file name or repeats, when the decision does not list exactly the attached names, or when a file is not UTF-8; tests `tests/app/test_writes_attach.py`, `tests/e2e/test_add_attach.py` (checkout and branch landing, `show --provenance`, dry run, the refusals).
- M1: `init_store` wraps `OSError` as `lodge: cannot create <path>: <reason>`, exit 2; `test_init_in_an_unwritable_checkout` (skipped as root).
- M2: the guide says "the author" throughout; `test_guide_names_the_author_not_a_person`.
- M3: the guide says `add` stages in checkout mode and publishes in branch mode.
- M4: the guide says an entry's `--reasoning` lists the decisions that changed it.
- M5: the guide writes `replaces: [d-xxxxxx]` and `narrows: [d-xxxxxx]`.
- The guide's attachment lines name the `--attach` route; the guide is 57 lines.
- Check 1 compares only decisions new in this add against the current state, so the standalone `check --gate` (no current state to compare) is unchanged.
