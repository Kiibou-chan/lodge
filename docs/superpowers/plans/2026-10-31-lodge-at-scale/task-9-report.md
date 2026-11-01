# Task 9 build report

Task 9 status: complete; the full check, all required replays, and the copied full-index clear measurement passed.

## Task 8a fix round

All six Minor findings in task-8a-review.md are addressed.
Committed gitlinks now key their empty text with `blob_id(b"" )`, agreeing with the key for empty text on disk.
The regression test uses a gitlink in the committed tree and a FIFO at the same disk path.
`Tree.blobs` now documents keys and the empty mapping on derived trees from writes, threads, and apply; these trees omit keys because their files changed, so consumers must parse unkeyed files directly.
`disk_tree` documents its exact-byte keys, and `read_tree` names its fetched entries `blob_paths`.
The three mislabelled case ID patterns now name their actual instants, and Task 4's stale status header is replaced with its resolved status.
`blob_id` is SHA-1 only, now explicit in its docstring.
In a SHA-256 repository committed and disk keys differ for equal bytes, which only misses cache reuse; exact reads remain correct.
No algorithm change was made for SHA-256.

New test command before implementation: `uv run --frozen pytest tests/gitstore/test_tree_blobs.py::test_gitlink_keys_the_empty_text_read -q`.
Failing output, with temporary paths omitted:

```text
> assert committed.blobs[path] == disk.blobs[path] == blob_id(b"")
E AssertionError: commit object ID != e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
FAILED tests/gitstore/test_tree_blobs.py::test_gitlink_keys_the_empty_text_read
1 failed in 0.54s
```

Fix-round validation: 52 focused tests passed in 0.44 s.
`UV_FROZEN=true sh scripts/check.sh` passed: 618 files formatted, Ruff clean, strict mypy on 236 files, Vulture clean, 1,691 tests passed and 1 skipped in 78.10 s, and `lodge check --gate` printed `ok` with the recorded storage-order note.

## Task 9 skeleton and red tests

The Task 8a fix round is committed and pushed as `94be161`.
Task 9 consumes d-9n3mad and s-gy0nsm, read through `lodge show --reasoning`; the product decision and area order were already recorded, so no record writes are part of this task.
The skeleton adds the codec, `FileKey`, `Index`, the SQLite adapter and space helpers, and front-door exports.
Before writing tests, `uv run --frozen pytest tests/test_structure.py -q` passed all 39 tests, and `uv run --frozen mypy` passed on 241 files.

Red command: `uv run --frozen pytest tests/core/test_codec.py tests/gitstore/test_index_db.py tests/gitstore/test_index_failures.py tests/gitstore/test_index_parses.py tests/app/test_parse_cache.py tests/e2e/test_index_off_same_output.py -q`.
All 59 collected cases failed before implementation.
The end-to-end fixture initially used an invalid new-decision draft with an existing ID; after correcting it, the two end-to-end tests were rerun before implementation and failed on the absent index file (2 failed in 0.80 s).
No passing parity assertion alone is counted as a red test: app tests also require actual cache use, and end-to-end tests require an index file.
Failing output, with repeated tracebacks and temporary paths omitted:

```text
src/lodge/core/codec.py:9: NotImplementedError
src/lodge/core/codec.py:13: NotImplementedError
src/lodge/gitstore/index_db.py:14: NotImplementedError
src/lodge/gitstore/index_db.py:26: NotImplementedError
app: assert index.lookups  # no cache call
end-to-end, corrected fixture: assert list(folder.glob("index-*.sqlite"))
E AssertionError: assert []
=========================== short test summary info ============================
FAILED tests/core/test_codec.py::test_round_trip_of_every_parse_kind - NotImp...
FAILED tests/core/test_codec.py::test_round_trip_of_mappings_and_read - NotIm...
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain0]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain1]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain2]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain3]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain4]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain5]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain6]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[bad]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain8]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain9]
FAILED tests/core/test_codec.py::test_refuses_unknown_class_and_bad_shapes[plain10]
FAILED tests/core/test_codec.py::test_no_pickle_or_marshal_in_core - NotImple...
FAILED tests/gitstore/test_index_db.py::test_creates_folder_and_file_named_by_digest
FAILED tests/gitstore/test_index_db.py::test_digest_changes_with_source_bytes
FAILED tests/gitstore/test_index_db.py::test_digest_names_python_yaml_libyaml_sqlite[sys-version-new-python]
FAILED tests/gitstore/test_index_db.py::test_digest_names_python_yaml_libyaml_sqlite[yaml-__version__-new-yaml]
FAILED tests/gitstore/test_index_db.py::test_digest_names_python_yaml_libyaml_sqlite[yaml-__with_libyaml__-False]
FAILED tests/gitstore/test_index_db.py::test_digest_names_python_yaml_libyaml_sqlite[sqlite3-sqlite_version-new-sqlite]
FAILED tests/gitstore/test_index_db.py::test_two_builds_keep_their_files - No...
FAILED tests/gitstore/test_index_db.py::test_old_build_deleted_after_seven_days_under_the_lock
FAILED tests/gitstore/test_index_db.py::test_no_fcntl_deletes_nothing - NotIm...
FAILED tests/gitstore/test_index_db.py::test_lock_taken_before_connect_and_touched
FAILED tests/gitstore/test_index_db.py::test_read_only_lock_file_is_opened - ...
FAILED tests/gitstore/test_index_db.py::test_fifth_most_recent_build_is_deleted
FAILED tests/gitstore/test_index_db.py::test_refused_upgrade_returns_none_and_holds_no_lock
FAILED tests/gitstore/test_index_db.py::test_corrupt_without_fcntl_returns_none
FAILED tests/gitstore/test_index_db.py::test_secure_delete_off_and_wal_bounded
FAILED tests/gitstore/test_index_db.py::test_two_clears_in_a_row_raise_the_epoch
FAILED tests/gitstore/test_index_db.py::test_connection_is_explicit_and_wal
FAILED tests/gitstore/test_index_db.py::test_cap_counts_used_pages - NotImple...
FAILED tests/gitstore/test_index_db.py::test_clear_keeps_a_readers_snapshot
FAILED tests/gitstore/test_index_db.py::test_two_writers_over_the_cap_clear_once
FAILED tests/gitstore/test_index_failures.py::test_read_only_folder_reads_or_skips
FAILED tests/gitstore/test_index_failures.py::test_read_only_and_missing_returns_none
FAILED tests/gitstore/test_index_failures.py::test_locked_at_open_does_not_delete
FAILED tests/gitstore/test_index_failures.py::test_locked_write_is_skipped - ...
FAILED tests/gitstore/test_index_failures.py::test_corrupt_file_is_rebuilt - ...
FAILED tests/gitstore/test_index_failures.py::test_corrupt_file_held_by_another_reader_is_not_deleted
FAILED tests/gitstore/test_index_failures.py::test_corrupt_file_read_only_returns_none
FAILED tests/gitstore/test_index_failures.py::test_keep_parses_interrupted_at_each_statement[1]
FAILED tests/gitstore/test_index_failures.py::test_keep_parses_interrupted_at_each_statement[2]
FAILED tests/gitstore/test_index_failures.py::test_keep_parses_interrupted_at_each_statement[3]
FAILED tests/gitstore/test_index_failures.py::test_keep_parses_interrupted_at_each_statement[4]
FAILED tests/gitstore/test_index_failures.py::test_concurrent_keep_parses - N...
FAILED tests/gitstore/test_index_failures.py::test_parse_units_are_immutable
FAILED tests/gitstore/test_index_failures.py::test_non_corruption_open_error_never_deletes
FAILED tests/gitstore/test_index_parses.py::test_hit_after_keep - NotImplemen...
FAILED tests/gitstore/test_index_parses.py::test_key_is_path_and_blob - NotIm...
FAILED tests/gitstore/test_index_parses.py::test_undecodable_row_is_a_miss - ...
FAILED tests/app/test_parse_cache.py::test_second_read_parses_nothing - asser...
FAILED tests/app/test_parse_cache.py::test_gate_uses_only_parses_keyed_by_read_bytes
FAILED tests/app/test_parse_cache.py::test_read_output_same_with_and_without_index[clean]
FAILED tests/app/test_parse_cache.py::test_read_output_same_with_and_without_index[changed]
FAILED tests/app/test_parse_cache.py::test_read_output_same_with_and_without_index[broken]
FAILED tests/app/test_parse_cache.py::test_read_output_same_with_and_without_index[stray]
FAILED tests/e2e/test_index_off_same_output.py::test_index_off_same_output - ...
FAILED tests/e2e/test_index_off_same_output.py::test_read_only_common_dir_reads
59 failed in 0.49s
```

## Task 9 groundwork before the coordinator ruling

Historical status before the coordinator ruling: NEEDS_CONTEXT.
The Task 9 changes remain uncommitted pending the scope question below.
The separate Task 8a fix-round commit is already pushed.

The groundwork implements the plain-value codec, including enum tags, registered dataclasses, field-type validation, mappings, tuples, and frozensets.
The SQLite adapter keys files by source bytes and relative names, schema, Python, PyYAML, libyaml availability, and SQLite, and keeps the settings digest separately.
It uses explicit read and write transactions, WAL, the specified pragmas, immutable parse units, decode misses, read-only access, and error-code-specific corruption recovery under the lifetime lock.
Space helpers count used pages, clear tables in place while raising the epoch, preserve existing WAL snapshots, and check the cap inside the caller's write transaction.
There are no stored states yet; the kept-state marker and cap helper are groundwork for Task 10a's state keeper.
`read_checked` uses cached parses for its current and published snapshots, still derives and checks them in full, and parses unkeyed derived trees directly.
The composition root opens the index unless `LODGE_INDEX=off`.
Other snapshot construction sites have not been changed because their files are outside Task 9's explicit Modify list.

Two additional lock regression tests failed before their fixes:

```text
FAILED tests/gitstore/test_index_failures.py::test_rebuilt_file_releases_exclusive_upgrade
E BlockingIOError: [Errno 11] Resource temporarily unavailable
FAILED tests/gitstore/test_index_failures.py::test_missing_own_lock_does_not_prune
E AssertionError: assert False  # an old build was pruned without our own lock
2 failed in 0.19s
```

Recovery now downgrades the exclusive upgrade to a shared lifetime lock, and opening without a usable own lock skips pruning.
The focused run after these fixes passed 60 cases, with 1 conditional skip, in 1.62 s.
The skipped portion is the secure-delete-default-dependent WAL test: this Python's SQLite does not default `secure_delete` to 1; assertions of the required connection pragmas passed before the skip.
Strict mypy passed on 248 files, Ruff passed, Vulture passed, and the structure suite passed all 39 tests.

## Earlier context question, now resolved

Question: may Task 9 also modify `src/lodge/app/reads.py`, `writes.py`, `threads.py`, and `confirm.py` to route their snapshot construction through the parse cache, or is the intended Task 9 scope only the current and published snapshots in `read_checked`?
Task 9 says that app builds every snapshot from cached parses and parsed misses, but its explicit Modify list names only `state.py`, `lodge.py`, `ports.py`, and the front door in app.
`reads.py` directly loads the gate's published and checked trees and calls `read_state` for drafts; `writes.py`, `threads.py`, and `confirm.py` also call `read_state`, with further direct loads in writes and threads.
These callers currently do not pass the new index, so meeting the every-snapshot requirement appears to require changes outside the named file list.
The dispatch also forbids changes to Tasks 1 to 8b's files unless Task 9 says so, and requires an unclear step to stop with NEEDS_CONTEXT.
The question is about the authorised file scope; no change to the product decision is proposed.
Task 9 is stopped at that ambiguity, and neither its replay nor its full-index clear timing has been run.
No Task 9 completion or timing claim is made.

The full gate already running when the task stopped completed with failure: formatting, Ruff, strict mypy, and Vulture passed; pytest reported 20 failed, 1,731 passed, and 2 skipped in 80.96 s.
All 20 failures are the existing `test_identical_read_output_unchanged` parametrisations: their `read_state` replacement takes one argument, while the new `read_checked` passes the optional index as a second argument even when it is `None`.

```text
src/lodge/app/state.py:98: TypeError
E TypeError: shortcut_disabled() takes 1 positional argument but 2 were given
20 failed, 1731 passed, 2 skipped in 80.96s (0:01:20)
```

This compatibility regression is still in the uncommitted groundwork and must be corrected before delivery, without changing those existing tests.
The gate did not reach `lodge check --gate` in this attempt.
The separate committed Task 8a fix round has its own green gate above.
No Task 9 commit or push has been made, and no change was made outside the named worktree.

## Coordinator ruling and resumed Step 3

The coordinator answered the scope question yes.
Every snapshot includes all snapshot construction in `app/reads.py`, `app/writes.py`, `app/threads.py`, and `app/confirm.py`.
These modules may change only to take the index through `Wiring` and build snapshots with cached parses.
The gate and `add` use only parses keyed by the bytes read, and still derive and check in full, as d-q0tb8r requires.
The existing wrong-key gate test remains required.
Tests replacing `read_state` with a one-argument function may be updated to its new signature; this supersedes the earlier report's instruction to leave those tests unchanged.
The only such replacement found is `shortcut_disabled` in `tests/app/test_identical_reads.py`; it will accept and forward the optional index.
No record writes are required: d-9n3mad, s-gy0nsm, and the storage order are already recorded.

Resumption red command: `uv run --frozen pytest tests/app/test_parse_cache.py -q`.
The six new caller cases and the extra gate-tree case all failed before their implementation:

```text
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[draft]
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[mint]
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[add]
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[ask]
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[behind]
FAILED tests/app/test_parse_cache.py::test_every_app_snapshot_uses_cache[confirm]
FAILED tests/app/test_parse_cache.py::test_gate_caches_each_exact_tree
E AssertionError: snapshot bypassed the parse cache
E AssertionError: assert index.lookups > lookups
E AssertionError: assert keys <= index.values.keys()
7 failed, 6 passed in 0.16s
```

The shared `snapshot_of` now serves all app snapshot construction sites, including extra gate trees, write proposals, and their published comparison trees.
Derived trees without blob keys parse directly and never store a parse under an unrelated key.
`tests/app/test_identical_reads.py::shortcut_disabled` now accepts `index: Index | None = None` and forwards it to the original `read_state`.
This is the only existing test edited for the new signature.

## Resumed validation

Focused command: `uv run --frozen pytest tests/app/test_parse_cache.py tests/app/test_identical_reads.py tests/core/test_codec.py tests/gitstore/test_index_db.py tests/gitstore/test_index_parses.py tests/gitstore/test_index_failures.py tests/e2e/test_index_off_same_output.py -q`.
Result: 96 passed and 1 conditional SQLite skip in 1.90 s.
The earlier 20 signature failures are resolved.
`UV_FROZEN=true sh scripts/check.sh` passed with exit 0: formatting and Ruff clean, 630 files formatted, strict mypy on 248 files, Vulture clean, 1,758 passed and 2 skipped in 82.61 s, and `lodge check --gate` printed `ok` with the recorded storage-order note.
The replay remains in progress; the later pruning regression and fresh gate below supersede this first gate result.
The initial small-store timing overlapped the gate and will be discarded and repeated after it.

## Replay method

The replay uses native-disk synthetic stores `s900`, `s9000`, and `s90000`, the Task 9 wheel installed in a separate native-disk environment, and the existing installed Task 8b build as the comparison.
Both environments use CPython 3.13.5 and PyYAML 6.0.3 with libyaml; SQLite is 3.47.1, and the filesystem is native ext4 on NVMe.
Both environments' bytecode is compiled with `python -m compileall` before measurement.
The benchmark disables global git configuration, system git configuration, and system attributes.
For every size and mode, the command is `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/sSIZE --lodge /var/tmp/lodge-bench/venv-task-9/bin/lodge --against /var/tmp/lodge-bench/venv-task-8b/bin/lodge --runs 3 --mode MODE`, with `SIZE` and `MODE` substituted.
All lines of `scripts/bench_reads.txt` are replayed; timings below are best of three separate processes per command.
`cold` removes the disposable cache before each process; `seen` primes each command first.
Output equality includes stdout and exit status as compared by the replay script.

## Final pruning edge case

Review before delivery found that pruning ran before creating a new build's database, so four existing builds could remain beside the newly opened fifth build.
A regression was added and run before the fix: `uv run --frozen pytest tests/gitstore/test_index_db.py::test_new_build_counts_towards_four_files -q`.

```text
> assert len(files) == 4
E AssertionError: assert 5 == 4
FAILED tests/gitstore/test_index_db.py::test_new_build_counts_towards_four_files
1 failed in 0.30s
```

Pruning now includes the current build's path in the age ordering before connecting, even when its database has not yet been created.
The lifetime lock is already held at that point.
The preliminary replays are discarded, and the installed wheel is rebuilt for the final replay.

The new pruning test originally also assumed sequential opens had distinct timestamps.
A focused run after the count fix exposed a tied timestamp, so the fixture now sets each previous build's lock age explicitly.
The first attempt to set that age used a helper bound to the unpatched digest; that fixture path was corrected to the synthetic digest.
The corrected focused suites passed: 36 passed and 1 conditional SQLite skip in 0.87 s.
The intermediate full check was interrupted while correcting this fixture, and a fresh full check starts before the final replay.

Fresh full check after the pruning fix: `UV_FROZEN=true sh scripts/check.sh`, exit 0.
All 630 files are formatted; Ruff, strict mypy on 248 files, and Vulture passed.
Pytest: 1,759 passed and 2 skipped in 81.55 s.
`lodge check --gate` printed `ok` and `note: area storage: order changed`.
The final replay starts only after this fresh check finishes.

### Final replay: s900

All outputs and exit statuses match Task 8b in both modes, in all three repetitions.
All commands exit 0.

| Command | Task 8b cold (s) | Task 9 cold (s) | Task 8b seen (s) | Task 9 seen (s) |
|---|---:|---:|---:|---:|
| `show {code}` | 0.309 | 0.371 | 0.311 | 0.284 |
| `show {entry} --reasoning --provenance` | 0.310 | 0.376 | 0.308 | 0.284 |
| `show {decision}` | 0.313 | 0.354 | 0.312 | 0.287 |
| `search berth --brief` | 0.329 | 0.384 | 0.330 | 0.305 |
| `search "berth crane" --brief` | 0.324 | 0.370 | 0.322 | 0.304 |
| `search {code} --brief` | 0.328 | 0.390 | 0.329 | 0.303 |
| `search berth` | 0.329 | 0.383 | 0.327 | 0.307 |
| `waiting` | 0.314 | 0.369 | 0.310 | 0.279 |
| `threads` | 0.312 | 0.369 | 0.310 | 0.282 |
| `spec --area area-001` | 0.312 | 0.370 | 0.310 | 0.280 |
| `check` | 0.308 | 0.371 | 0.309 | 0.283 |
| `check --gate` | 0.378 | 0.399 | 0.356 | 0.329 |
| `show {code} {code2} {entry}` | 0.329 | 0.367 | 0.314 | 0.283 |
| `show A` | 0.347 | 0.390 | 0.336 | 0.305 |
| `search berth tide --brief` | 0.347 | 0.405 | 0.349 | 0.316 |
| `search --phrase "berth crane" --brief` | 0.335 | 0.398 | 0.340 | 0.310 |

### Final replay: s9000

All outputs and exit statuses match Task 8b in both modes, in all three repetitions.
All commands exit 0.

| Command | Task 8b cold (s) | Task 9 cold (s) | Task 8b seen (s) | Task 9 seen (s) |
|---|---:|---:|---:|---:|
| `show {code}` | 1.451 | 1.689 | 1.455 | 1.116 |
| `show {entry} --reasoning --provenance` | 1.432 | 1.661 | 1.433 | 1.122 |
| `show {decision}` | 1.419 | 1.672 | 1.433 | 1.100 |
| `search berth --brief` | 1.657 | 1.906 | 1.671 | 1.344 |
| `search "berth crane" --brief` | 1.641 | 1.893 | 1.652 | 1.327 |
| `search {code} --brief` | 1.660 | 1.902 | 1.662 | 1.402 |
| `search berth` | 1.649 | 1.889 | 1.669 | 1.325 |
| `waiting` | 1.438 | 1.679 | 1.447 | 1.119 |
| `threads` | 1.434 | 1.668 | 1.441 | 1.111 |
| `spec --area area-001` | 1.433 | 1.678 | 1.437 | 1.180 |
| `check` | 1.458 | 1.653 | 1.423 | 1.107 |
| `check --gate` | 1.738 | 1.876 | 1.650 | 1.321 |
| `show {code} {code2} {entry}` | 1.497 | 1.681 | 1.617 | 1.121 |
| `show A` | 1.660 | 1.890 | 1.818 | 1.318 |
| `search berth tide --brief` | 1.896 | 2.115 | 1.909 | 1.578 |
| `search --phrase "berth crane" --brief` | 1.771 | 1.982 | 1.753 | 1.429 |

The final `s90000` cold replay completed: every stdout and exit status matches Task 8b in all three repetitions, and all commands exit 0.
Cold `show {code}` is 16.947 s for Task 9 and 14.168 s for Task 8b, best of three.
The largest-store seen replay is now running; its full table and the clear timing remain pending.

### Final replay: s90000

All outputs and exit statuses match Task 8b in both modes, in all three repetitions.
All commands exit 0.

| Command | Task 8b cold (s) | Task 9 cold (s) | Task 8b seen (s) | Task 9 seen (s) |
|---|---:|---:|---:|---:|
| `show {code}` | 14.168 | 16.947 | 14.274 | 10.995 |
| `show {entry} --reasoning --provenance` | 14.065 | 16.637 | 13.989 | 10.823 |
| `show {decision}` | 14.217 | 16.641 | 15.201 | 10.981 |
| `search berth --brief` | 16.624 | 19.156 | 16.666 | 13.466 |
| `search "berth crane" --brief` | 16.760 | 19.341 | 16.704 | 13.623 |
| `search {code} --brief` | 16.628 | 19.146 | 16.606 | 13.455 |
| `search berth` | 16.583 | 19.036 | 16.597 | 13.443 |
| `waiting` | 13.984 | 16.736 | 13.963 | 10.792 |
| `threads` | 14.012 | 16.482 | 13.939 | 10.753 |
| `spec --area area-001` | 14.353 | 16.657 | 14.037 | 10.940 |
| `check` | 13.980 | 16.484 | 13.914 | 10.878 |
| `check --gate` | 16.484 | 18.907 | 16.496 | 13.458 |
| `show {code} {code2} {entry}` | 14.412 | 17.016 | 14.347 | 11.234 |
| `show A` | 16.025 | 18.580 | 16.159 | 12.973 |
| `search berth tide --brief` | 19.258 | 21.746 | 19.250 | 16.092 |
| `search --phrase "berth crane" --brief` | 17.580 | 20.220 | 17.666 | 14.455 |

## Full-index clear timing

Command: `/var/tmp/lodge-bench/venv-task-9/bin/python /var/tmp/lodge-bench/task-9-clear.py`.
The script makes three fresh SQLite backup copies of the fully populated `s90000` index under `/var/tmp/lodge-bench`, then times one `BEGIN IMMEDIATE`, `index_space.clear`, and `COMMIT` on each copy.
Copying, counting, and the subsequent checkpoint are outside the measured interval.
The original store and index are unchanged by these clears.
SQLite is 3.47.1; this Python's `PRAGMA secure_delete` defaults to 0, and every measured index connection explicitly sets it to 0, with WAL, `synchronous=NORMAL`, and `journal_size_limit=16777216`.

| Sample | Clear and commit (s) |
|---|---:|
| 1 | 0.056094 |
| 2 | 0.049078 |
| 3 | 0.054912 |

Best of three: 0.049078 s.
Every copy starts with 160,800 parse rows, epoch 1, and 144,568,320 used bytes.
Every clear leaves zero parse rows, epoch 2, and 16,384 used bytes.
The file remains 144,568,320 bytes and keeps its inode; freed pages are reusable.
The WAL is zero bytes after the untimed truncating checkpoint.
The cap for this 160,800-file tree is 241,200,000 bytes.
Task 9's populated index holds parses and metadata; the state and FTS tables arrive in Task 10.
The clear helper already handles ordinary tables and virtual-table recreation.

## Delivery and concerns

All 288 pairs of timed stdout and exit-status samples match Task 8b across the three stores, both modes, every command, and every repetition.
Every timed command exits 0.
The final replay uses the rebuilt wheel after the pruning fix and starts after the fresh green check.
The full check passed with 1,759 tests passed and 2 skipped; its exact command and output are recorded above.
The report records the coordinator ruling, the initial failing-test evidence for every new case, and the sole existing test signature edit.
No record was written for this task; the coordinator's product decision, entry, and area order are consumed as recorded.

No blocking concern remains.
Cold reads pay for writing the parse cache, as the tables show.
Seen reads still assemble snapshots and run derivation and checks in full; stored states and indexed search remain scheduled for Task 10, and the performance stop applies after Task 11.
The SQLite-default-dependent half of the WAL test is skipped because this Python defaults `secure_delete` to 0; the required pragma assertions passed, and the full-index clear above was measured with that setting explicitly off.
The cap helper and epoch are ready for Task 10a's state keeper; Task 9 itself keeps no state completeness markers.
Raw replay files, red-test logs, the final check log, and the clear script and observations remain under `/var/tmp/lodge-bench`.

Final delivery verification: the installed benchmark wheel's source digest matches the working source (`72670d6e81c923ab`).
`git diff --check` passed, and all 26 changed files passed the public-file path and identity scan.
