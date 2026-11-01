# Task 9 fix round 2

Scope: N1 and every Minor (N3 to N7) of `task-9-recheck.md`.
N2 is report-only, with the changed-read path being reworked by the planner.
No lookup or codec design change, record addition, or later-task implementation is authorised in this round.

## Initial evidence

The branch is `read-speed-build`, and the worktree started clean.
The standing rules, the plan's Global Constraints, Review Focus, Tasks 9 and 10a, the recheck, and the previous fix report have been read.
`lodge waiting` reports nothing waiting for an agent.
The gate's two extra snapshot calls omit `state.parses`.
The codec guards, viewer POST release, and project-index exception handler already exist, so their new regression tests will first run against individually planted regressions, restored immediately after each run.
The settings digest will stop travelling through the parse-only opening path until Task 10a uses it for state keys.

## Work and validation

Failing-test evidence, targeted changes, and the Task 10a hand-offs are recorded below.
The whole gate passed, and the task is ready for its commit and push.

## Failing tests before the fixes

Commands use `uv run --frozen pytest`.
Full logs are under `/var/tmp/lodge-bench/task-9-fix-2-red-*.log`.
The initial POST fixture used a token below the existing length requirement; that fixture was corrected before recording the meaningful release regression below.
The gate fixture edits the same file in place and includes both a distinct committed tree and a working tree.

```text
$ uv run --frozen pytest tests/app/test_parse_cache.py::test_gate_looks_up_shared_keys_once tests/test_structure_io.py::test_index_modules_confined -q
FAILED tests/app/test_parse_cache.py::test_gate_looks_up_shared_keys_once
E           AssertionError: assert 9 == 3
FAILED test_index_modules_confined[import {module}-_sqlite3-viewer]
FAILED test_index_modules_confined[import {module}-_pickle-gitstore]
FAILED test_index_modules_confined[from {module} import loads-_dbm-main]
27 failed, 86 passed in 0.38s

$ uv run --frozen pytest tests/gitstore/test_index_fixes.py::test_parse_only_opening_needs_no_settings -q
E       TypeError: project_index() missing 1 required positional argument: 'settings'
1 failed in 0.15s
```

For existing protections, each mutation was planted alone and restored in `finally` before the next mutation.
The codec mutations and their matching new test cases were:

| Mutation | Test case | Failing output |
|---|---|---|
| Remove the scalar tuple marker check | `wrong-tuple-marker` | `Failed: DID NOT RAISE ValueError`, 1 failed |
| Replace `type(v) is annotation` with `isinstance(v, annotation)` | `nested-int-bool` | `Failed: DID NOT RAISE ValueError`, 1 failed |
| Replace `type(v) in args` with `isinstance(v, args)` | `nested-union-int-bool` | `Failed: DID NOT RAISE ValueError`, 1 failed |
| Remove mapping value validation | `mapping-item-type` | `Failed: DID NOT RAISE ValueError`, 1 failed |

Each codec case ran separately using its full node ID in `tests/core/test_codec.py`, taking 0.12 s.
Removing the POST `finally` release and running the two new `test_factory_releases_retained_index[post]` and `[post-error]` cases produced:

```text
E       AssertionError: assert <retained lock> is None
FAILED tests/e2e/test_index_lifetime.py::test_factory_releases_retained_index[post]
FAILED tests/e2e/test_index_lifetime.py::test_factory_releases_retained_index[post-error]
2 failed in 0.21s
```

Removing `project_index`'s exception handler and running `test_project_index_skips_open_errors` produced:

```text
E       RuntimeError: injected opening failure
FAILED tests/gitstore/test_index_fixes.py::test_project_index_skips_open_errors
1 failed in 0.16s
```

All these mutations have been restored.
No codec or viewer implementation change is needed for N4 or N5.

## Changes built

- N1: both gate snapshot calls pass `state.parses`, sharing every decoded unit across the published, committed, and working trees.
  The counting test covers cold and warm reads, distinct tree objects, an uncommitted edit at the same path, and unchanged gate output with the index off.
  Three unique keys now have three lookups, rather than nine.
  Independently reverting either call site's memo makes the same test fail.
- N3: the structure rule forbids `_pickle` everywhere and confines `_sqlite3` and `_dbm` to `gitstore`, including both `import` and `from` forms.
- N4: the new tests kill the tuple marker and both exact integer-type guard mutations, with an extra mapping-item case.
  The existing decision-shape test locates fields by name rather than by positional constants.
  The codec implementation is unchanged.
- N5: real retained connections and locks are checked after successful and exceptional `handle_post` requests.
  The write operation itself is stubbed to return a redirect or raise, so the lifetime test writes no records.
  Both cases fail when the existing release is removed.
- N6: `project_index`, `open_index`, and `IndexDB` no longer take or compute unused settings input.
  `settings_key` remains a tested helper for Task 10a's state keys, and Task 10a now names that use explicitly.
  A raising `open_index` is tested as a miss.
- N7: Task 10a Step 3a quotes the I4/M10 hand-off and the recheck's measured M9 hand-off.
  It names parse-only cap callers, the caller's tree file count, `INDEX_FILE_CAP`, `prepare_keep`, the meaning of `meta.kept`, and the completion of the unit-growth bound by Task 10a.
  The ledger carries the same hand-offs and supersedes the earlier M9 error-isolation rationale with the measured gain.

Existing test files edited: `tests/app/test_parse_cache.py` (new gate test and opening signature), `tests/core/test_codec.py` (field names and nested shapes), `tests/e2e/test_index_lifetime.py` (POST variants), `tests/test_structure_io.py` (private module variants), and `tests/gitstore/test_index_fixes.py` (opening regressions and constructor signature).
The existing callers in `tests/gitstore/index_helpers.py`, `tests/gitstore/test_index_db.py`, and `tests/gitstore/test_index_failures.py` only lose the unused opening or constructor argument.
No existing assertion is removed or weakened.
`tests/structure_imports.py` strengthens the structure rule.
No interface is added or moved, so the plan's interface-skeleton step does not apply.

## Targeted verification

The targeted run covered the changed app, codec, lifetime, adapter, failure, parse, and structure suites:

```text
442 passed, 1 skipped in 2.32s
```

Ruff format, Ruff, strict mypy (250 source files), Vulture, and `git diff --check` passed.
The skip is the existing full-WAL clear timing guard: this Python's SQLite defaults `secure_delete` to 0, so the test asserts the configured pragmas but skips the branch requiring a default of 1.

## Timings and remaining concerns

N2 is report-only and the planner is reworking the changed-read path.
The recheck's measurement, not a fresh claim from this round, is 1.40 to 1.42 s for lookup and decode of 160,800 units, giving about 4.3 s for the changed read on the plan's arithmetic against the 3 s target.
Its measured batching gain is about 0.05 s.
No lookup or codec redesign, full replay, or full-index clear timing is part of this round; the previous Task 9 reports retain those timings.
This round's measured durations are the failing regressions, targeted verification, and whole gate.
The target stop remains after Task 11 (d-26e6zj).
The cap's parse-only integration remains Task 10a's explicit responsibility, and Task 10b still owns the FTS clear integration.
No new decision is needed, no record is added, and no later task is implemented.

## Whole gate and delivery

Command: `UV_FROZEN=1 sh scripts/check.sh`, with the normal index setting.
The command exited 0 before the commit.
Ruff format, Ruff, strict mypy, Vulture, pytest, and `lodge check --gate` all passed.

```text
1917 passed, 2 skipped in 83.52s (0:01:23)
ok
note: area storage: order changed
```

Full output is in `/var/tmp/lodge-bench/task-9-fix-2-check.log`.
The existing storage-order note is also present in the previous fix report's successful gate.
`git diff --check` and a scan of every added line for personal paths, machine-specific pytest paths, and em dash characters passed.
Delivery is one commit, `Task 9 fix round 2: share gate parses and cover recheck gaps`, with explicit paths and the dispatched Codex trailer, followed by `git push -u origin read-speed-build`.
N1 and N3 to N7 are addressed; N2 remains the planner's report-only hand-off.
