# Recheck of the Task 9 fix round (8df3b2e)

Checked in a detached worktree of 8df3b2e under `/var/tmp/lodge-recheck-t9/`, against `task-9-review.md` and `task-9-fix-report.md`.
Result: 0 Blocking, 2 Important, 5 Minor new findings; every finding of the review is fixed with a test that fails when reverted, or reported with a reason the dispatch, the plan, or a decision supports (details below).
Gate parts I ran: ruff format, ruff, mypy, vulture, full `pytest` (1,866 passed, 2 skipped).
I did not run `lodge check --gate`, which opens the index in the shared `.git/lodge` folder.
Shared folder: untouched by me (its newest file is dated before my first command; my one `lodge show` in the worktree ran with `LODGE_INDEX=off`).
All CLI probes ran on a scratch copy of `s900` and a copy of the `s90000` index file, both under `/var/tmp/lodge-recheck-t9/` (removed afterwards).

## New findings

### Important

**N1 · `check --gate` with an uncommitted edit decodes the committed tree a second time.**
Handle: `src/lodge/app/reads.py:144` and `:151` (`snapshot_of(base.published, w.index)` and `snapshot_of(tree, w.index)` carry no memo), while `read_state`, `read_checked`, `add`, and the thread writes now pass `state.parses` (I1's "share decoded units in one read").
Failure scenario: `committed_gate` (`gitstore/published.py:43`) checks `committed` and `working tree` whenever they differ, the usual state in a pre-commit hook.
Measured on a scratch `s900` with one edited decision, counting keys given to `IndexDB.parses`: `check` 1,610 keys; `check --gate` 3,219 keys (1,609, then 1, then 1,609 for the committed tree), identical on a warm second run.
At 160,800 files that is a second full lookup and decode, about 1.4 s, on the gate whose plan row ("about 4 s") counts the parse cache once.
No test sees it: `test_checked_read_looks_up_shared_keys_once` covers `show` only.
Fix: pass `state.parses` as the third argument at both call sites; I applied it in scratch and the same command looked up 1,610 keys (the third call 0), with `tests/app` and `tests/e2e` green (378 passed).
Add a test beside `test_checked_read_looks_up_shared_keys_once` that runs `check(gate=True)` over a store whose working tree differs from HEAD and asserts no key is looked up twice.
It stays within d-q0tb8r: the memo is keyed by the path and the hash lodge computed from the bytes it read.

**N2 · The parse-cache decode is 1.4 s at 160,800 files, and neither Task 10a nor Task 10c as planned removes it from the changed read (plan carry-forward, no defect in 8df3b2e).**
Handle: plan cost table, row "after one changed record" ("parse cache 0.45", total about 3 s), d-232gxs ("a read after one changed record at most 3 s"); Task 10a ("otherwise the state is built in memory from `listings()` and the parse cache"); Task 10c ("the published snapshot itself is still assembled from the parse cache").
Where the time goes, measured on a copy of the `s90000` index (160,800 units, `gc` off, best of three, `find_parses` over every key): 1.40 to 1.42 s, which is 0.57 s of per-key `SELECT` (two B-tree descents, the `UNIQUE(path, blob)` index then the table row), 0.31 s of `json.loads`, and 0.50 s of `from_plain` (the compiled validators and building 160,800 dataclasses); about 7 per cent is the loop and the `isinstance` filter.
Task 10a's stored rows serve the seen-state read only: a changed read has to `derive` and `check_state` over the whole snapshot, so it decodes every unit of the current state, and Task 10c only replaces the published side's `derive` and `check_state` by stored facts.
So the changed read costs about 3.3 - 0.45 + 1.4 = 4.3 s on the plan's own arithmetic, against the 3 s target; d-26e6zj defers the stop to after Task 11, but the table should say so now.
Levers I measured on the same index (not implemented): an ordered scan by rowid with the values read in one pass costs 0.13 s instead of 0.57 s (the per-key loop in sorted order is 0.38 s, chunked `IN (VALUES ...)` 0.32 s, so batching alone, M9, gains about 0.05 s); building each unit without the validators costs 0.21 s instead of 0.50 s; `json.loads` stays 0.31 s.
Together about 0.65 s, still above the plan's 0.45 s, so the changed row comes to about 3.5 s.
Fix: record this in the ledger and the Task 10a brief; give `keep_state` the state's ordered unit list (rowids) so a changed read fetches its units in one scan, and decide, as a ruling, whether rows written by the same build digest skip per-field validation; if the 3 s target stays, ask the coordinator now rather than at Task 12.

### Minor

**N3 · The structure rule does not cover `_pickle` and `_sqlite3`.**
Handle: `tests/structure_imports.py:88` and `:90` compare the first dotted name with `{"marshal", "pickle", "shelve"}` and `{"sqlite3", "dbm"}`.
Planted `import _pickle` in `viewer/server.py` and `import _sqlite3` in `viewer/forms.py`: `tests/test_structure.py` 39 passed.
`import sqlite3`, `marshal`, `pickle`, `shelve`, `dbm.sqlite3`, `from sqlite3 import connect`, `import pickle as p`, a function-local import, and `importlib.import_module('pickle')` in `cli`, `viewer`, `hook`, `main`, `app`, `core`, and `gitstore` all failed as required (14 plants, I2 holds).
Fix: add `_pickle`, `_sqlite3`, and `_dbm` to the two sets, with a case in `test_index_modules_confined`.

**N4 · Three codec guards survive removal, and one test pins decision field positions.**
Handle: `src/lodge/core/codec.py:170` (`raw[0] != ""`, the tuple marker: without it `["x", "a"]` is accepted for a `tuple[str, ...]` field and `"x"` is dropped), `:103` and `:107` (`type(v) in args` and `type(v) is annotation`: replaced by `isinstance`, a `bool` is accepted in a nested `int` slot).
I mutated 14 guards of `_compact`, `_check`, and `_layout` and ran `test_codec.py` and `test_index_parses.py`: 9 killed; the 5 survivors were these three plus two that are equivalent (an unknown class and a non-dataclass raise `ValueError` one step later anyway).
Also `test_compact_nested_shapes_are_checked` (`tests/core/test_codec.py:125`) indexes `to_plain(decision())` by position (3, 9, 16), so a reordered field makes it pass or fail for the wrong reason.
Fix: three cases (a tuple field with a wrong marker, a `bool` for an `int` inside a tuple or mapping, a wrong item type under a `Mapping`) and look the position up by field name.
I also ran a 200,000-case mutation fuzz of the stored plain forms of all five parse kinds (random junk at random positions, deletions, insertions): 31,408 accepted, 0 of them failing an independent deep type check, no exception outside `ValueError` and 30 `TypeError`, all caught by `find_parses`.

**N5 · The viewer's POST release has no test.**
Handle: `src/lodge/viewer/writes.py:210-212` (the new `finally`); `tests/e2e/test_index_lifetime.py` covers the CLI and `render` only.
Removing the `finally` leaves `tests/viewer` at 134 passed.
Fix: a fourth case in `test_factory_releases_retained_index` that posts through `writes.handle_post`.

**N6 · The settings digest is computed and discarded, and the new `try` in `project_index` is untested.**
Handle: `src/lodge/gitstore/index_db.py:102` (`settings_digest` is never read in `open_index`) and `:136` (`IndexDB.__init__` takes `settings: str` and drops it); `:46-50` (`except Exception: return None`) has no test (the M5 test covers `settings_key` only).
Fix: leave the parameter out until Task 10a stores it, or say in the 10a brief that it is already threaded; add a test that a raising `open_index` gives `None`.

**N7 · The I4 and M9 hand-offs live only in the fix report.**
Handle: `task-9-fix-report.md` ("Remaining concerns and hand-offs"); the plan's Task 10a says the clear happens in `keep_state` and that `keep_parses` keeps its signature, so parse-only writers (`add`, the gate, every non-indexed read) have no planned caller of `prepare_keep`, and `meta.kept` is still set nowhere (`index_space.py:93,99`).
The deferral is supported by the dispatch and by the plan's Task 10a for `keep_state`; it is not supported for parse-only writers.
Fix: write it into the Task 10a brief and the ledger line for Task 9 (parse-only writers clear too, `kept` means a state kept, the tree's file count is the caller's), so the unit growth of invariant 1 is bounded by the end of Task 10a.
On M9: the report cites the dispatch's per-key lookup, which concerns error isolation; the better reason is my measurement above (batching gains about 0.05 s), so the decline stands.

## The review's findings, one by one

Each "reverted" line means: I reverted the fix in scratch and ran its test.

- **B1 fixed.** Reverting both layers (per-key `try` in `find_parses` and `insert_parses`, `except Exception` at the port) fails 12 tests: `test_surrogate_path_with_real_index[show|gate|add]` (app level, real `IndexDB`), `test_unencodable_key_skips_only_that_unit`, `test_any_adapter_exception_is_a_miss[parses|keep_parses|epoch]`, `test_lookup_keeps_partial_hits`, and `test_non_utf8_path_same_output` for `show`, `check`, `check --gate`, `add` (e2e).
  With only the per-key `try` reverted the port's `except Exception` still turns it into a miss, and exactly `test_unencodable_key_skips_only_that_unit` and `test_lookup_keeps_partial_hits` fail: the two layers are separately tested.
  Real CLI on a scratch `s900` with `lodge/decisions/stray-\xff\xfe.md` untracked, staged, and committed: `show`, `check`, `check --gate`, `add --dry-run`, `waiting`, `search`, `threads` print the same stdout, stderr, and exit status with the index on (twice) and `LODGE_INDEX=off`, no traceback; invalid UTF-8 *content* in a decision likewise.
- **I1 fixed as far as the codec goes.** `from_plain` over 160,800 units: 0.505 s here, 0.545 s in the report (the plan's 0.45 s is not reached, as the report says).
  Refusal of bad shapes: see N4; the old tuple wire form is gone, so `test_refuses_unknown_class_and_bad_shapes` now exercises the list form for its class and enum cases, and the five tests added for scalars and nested shapes kill the mutants noted in N4.
  The compiled decoder builds records with `object.__new__` and `__dict__.update`; no core dataclass has `slots`, `__post_init__`, or `field(init=False)` (grep of `src/lodge/core`), so nothing is skipped that the constructor ran.
  No `pickle` or `marshal` is left in `src`.
  The memo that shares decoded units works for `read_checked`, `add`, `ask`, `reply`, and `close` (reverting it fails `test_checked_read_looks_up_shared_keys_once`); the gate is the gap (N1).
- **I2 fixed.** Reverting `tests/structure_imports.py` fails 46 cases of `test_index_modules_confined`; planting in real `src` is under N3.
- **I3 fixed.** Reverting the keys in `writes.py` fails `test_derived_tree_parses_only_changed_files[add]`; reverting them in `threads.py` fails `[ask]`, `[reply]`, and `[close]`.
  On a scratch `s900` with a warm index, `add --dry-run` and `ask` each call `core.parse_file` once (the changed file); `LODGE_INDEX=off` parses all.
  Keys come from `current.blobs`, which `disk_tree` hashes from the bytes read (`checkout.py:103-114`), and only for paths the write did not change (`writes.py:91-96`, `threads.py:92-96`), so d-q0tb8r holds: no key comes from git for a working-tree file, and the gate and `add` look up only bytes they read.
- **I4 report-only, accepted with N7. M10 report-only, as dispatched. M11 to Task 8c, as dispatched.**
- **M1 fixed** (reverted `index_space.py`: `test_orphan_does_not_abort_pruning` fails). **M2** declined with the plan's text ("after opening, such an error is a miss") and the partial hits kept (`test_lookup_keeps_partial_hits`). **M3 fixed** (reverted: `test_digest_includes_libyaml_version` fails). **M4 fixed** (an extra `common_dir(root)` call in `main.py` fails `test_common_directory_discovered_once`). **M5 fixed** (reverted: `test_settings_key_needs_no_plain_codec` fails; see N6). **M6 fixed** (without `epoch=epoch`, `test_epoch_is_kept_for_the_build` fails). **M7 fixed** (the test holds `BEGIN IMMEDIATE` and checks a skipped keep). **M8 fixed** (branch and comment gone). **M9** declined, see N7. **M12 fixed** (without the `finally` in `main` or `render`, `test_factory_releases_retained_index` fails for `cli`, `cli-error`, `viewer`, `viewer-error`; POST is N5).

## Files read

`task-9-review.md`, `task-9-fix-report.md`, `brief-t9fix.md`; the diff 4065059..8df3b2e of `src/lodge/core/codec.py`, `app/{state,writes,threads,lodge,ports}.py`, `gitstore/{index_db,index_parses,index_space,setup,__init__}.py`, `main.py`, `viewer/{server,writes}.py`, `README.md`, and all changed tests; whole files `core/codec.py`, `gitstore/index_db.py`, `app/state.py`, `gitstore/checkout.py` (`disk_tree`), `gitstore/trees.py` (`read_tree`), `gitstore/published.py` (`committed_gate`), `app/reads.py` (`check`), `core/settings.py`, `tests/structure_imports.py`; the plan's header, Global Constraints, cost table, Tasks 9, 10a, 10b, 10c, and 11 headings and text; d-q0tb8r and d-232gxs with `--reasoning` (read with `LODGE_INDEX=off`), d-26e6zj.

## Files not read

`tests/gitstore/index_helpers.py`, `test_index_db.py` beyond the diff, the other e2e tests; `gitstore/branch.py` and `listing.py` (branch mode was not run); `scripts/bench_reads.py`; the viewer was not run as a server, only `render` and `handle_post` through the tests; the `s90000` store itself was not read (a copy of its index file and a directory walk only), and the report's before figure of 2.456 s and its clear timing (0.051 s) were not re-run.
