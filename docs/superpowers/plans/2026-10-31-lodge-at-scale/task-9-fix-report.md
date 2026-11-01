# Task 9 fix round

Scope: B1, I1 to I3, and the applicable Minors from `task-9-review.md`.
I4 and M10 remain with Task 10a, including the parse-only keep callers, the tree file count, the named cap, and the meaning of `meta.kept`.
M11 remains with Task 8c, as dispatched.
No record is needed or written, and no later task is started.

## Initial evidence

The unchanged build's s90000 index contains 160,800 units.
A sequential profile of `from_plain`, with cyclic collection disabled, took 2.464901, 2.456012, and 2.468938 seconds, best 2.456012 seconds.
The profiled call took about 10.0 seconds, with `_fits`, `get_args`, and `get_origin` dominating the work.
The benchmark uses only the new build on the existing synthetic store under `/var/tmp/lodge-bench/s90000`.
Raw observations are in `/var/tmp/lodge-bench/task-9-fix-profile-before.log`.

Step 0 adds signatures for sharing the git common directory and explicitly releasing the adapter.
The structure check and strict mypy pass before the new tests.
Implementation and failing-test evidence follow incrementally.

## Failing tests before implementation

Commands use `uv run --frozen pytest`, with full logs under `/var/tmp/lodge-bench`.
The first run of the app, adapter, e2e, structure, and codec files ended:

```text
65 failed, 240 passed in 2.03s
UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 22: surrogates not allowed
FAILED test_surrogate_path_with_real_index[show]
FAILED test_surrogate_path_with_real_index[gate]
FAILED test_surrogate_path_with_real_index[add]
FAILED test_unencodable_key_skips_only_that_unit
FAILED test_any_adapter_exception_is_a_miss[parses]
FAILED test_any_adapter_exception_is_a_miss[keep_parses]
FAILED test_any_adapter_exception_is_a_miss[epoch]
FAILED test_non_utf8_path_same_output[command0]
FAILED test_non_utf8_path_same_output[command1]
FAILED test_non_utf8_path_same_output[command2]
FAILED test_non_utf8_path_same_output[command3]
```

The derived-tree regressions failed for `add`, `ask`, `reply`, and `close`, showing unchanged decision paths in the parse spy.
The structure tests plant both import forms in synthetic source trees and failed for the previously permitted imports in gitstore, CLI, viewer, hook, and main.
The compact representation test found a tuple where its JSON-native list was required, and the unknown-class, wrong-arity, and bad-enum compact tests accepted invalid data.
The fourth malformed compact case already failed decoding as required.
Full output: `task-9-fix-red-1.log`.

The separate Minor run ended:

```text
FAILED test_orphan_does_not_abort_pruning
FAILED test_digest_includes_libyaml_version
FAILED test_lookup_keeps_partial_hits
FAILED test_settings_key_needs_no_plain_codec
4 failed in 0.19s
```

Full output: `task-9-fix-red-minors.log`.
The shared-key, retained-epoch, common-directory, and retained-index run ended with seven failures in 0.47 seconds.
It found two common-directory calls instead of one, a discarded epoch of zero, repeated shared keys, and adapters left open when references were retained.
Full output: `task-9-fix-red-lifetime.log`.
The viewer error route in that first run was corrected from an unrecognised route to `/r/missing` before validation.

## Changes built

B1: every lookup handles its own errors, unencodable write keys are skipped individually, and the adapter boundary catches `Exception` for lookups, writes, and epochs.
Successful keys survive a bad key in either direction.
I2: the structure rule bans marshal, pickle, and shelve throughout source, and confines sqlite3 and dbm to gitstore.
I3: derived write trees retain only unchanged files' exact-byte keys; changed paths parse directly.
One build shares decoded units across current, derived, and published snapshots by the whole file key.
M6: the epoch is retained on `State` for the build instead of discarded.
M1: pruning handles each build's age independently, treats a missing lock as oldest, and takes an exclusive lock before deleting the orphan.
The README documents persistent empty lock files and manual reclamation.
M2: partial hits survive later lookup errors.
Automatic post-open corruption repair remains deferred because the plan explicitly specifies a miss after opening; no marker or repair policy is introduced.
M3: libyaml's version string joins the build digest.
M4: composition discovers the common directory once and shares it with the store and index.
M5: settings use their representation without the parse codec, and index preparation catches failures.
M7: the existing lock test now holds `BEGIN IMMEDIATE`, attempts a keep, checks its miss, verifies unchanged bytes, and retains the subsecond open assertion.
M8: the speculative FTS branch and task-specific comment are removed until its table and tests exist.
M9: batched SELECTs conflict with the dispatch's per-key lookup requirement, so lookups remain per key.
M12: unused settings storage and the serialisation type-ignore are removed; CLI commands and viewer GET/POST requests explicitly release the index in `finally`, including errors with retained frames.
The destructor remains a fallback for direct adapter users.

## Codec and validation refinement

The stored plain form is JSON-native: `[ClassName, ...fields]`, `["=EnumName", value]`, `["", ...tupleItems]`, `["*", ...setItems]`, plain string-keyed mappings, and scalar values.
Schema 2 and the build digest isolate it from previous cache formats.
JSON uses ASCII escapes, preserving surrogateescaped content without requiring UTF-8 encoding of that content.
No pickle or marshal remains in source.
The decoder caches class layouts and validators, checks tags, arity, exact scalar types, and nested shapes, and constructs only registered dataclasses through their field dictionaries.
Scalar tuples avoid a second recursive walk through `from_plain`.
It retains enum instances and never executes a stored constructor name.

`test_refuses_unknown_class_and_bad_shapes` now uses the actual list representation for its class and enum cases.
The old tuple-class decoder was removed, so that test does not pass merely by rejecting an obsolete wire format.
The additional scalar regression first reported two failures: an integer path and a boolean check number were accepted.
The nested regression first reported four failures for a wrong enum class, missing changes, an integer change, and a non-string attachment.
Full outputs: `task-9-fix-red-scalars.log` and `task-9-fix-red-nested.log`.
All now pass with compiled validators.

An intermediate full suite passed with 1,862 tests and two skips before the four nested cases were added.
The first whole-gate invocation set `LODGE_INDEX=off` globally to avoid creating a shared cache while checking this worktree.
That was unsuitable for tests which explicitly assert that the default factory opens an index: five failed, with 1,861 passing and two skipped.
The final whole gate runs with the normal index setting and frozen dependency resolution.

Existing tests changed: the original codec rejection cases now use the current wire form; the lock test exercises a real blocked writer; the folder-creation test drops its assertion on unused settings storage; and the collector test's factory stub now returns a releasable mock, since viewer setup explicitly releases its initial adapter.
The original second-read epoch assertions remain, and a new test checks the value retained on the build.

## Final s90000 measurements

Commands, from the build worktree:

```sh
uv run --frozen python -m compileall -q src .venv/lib
uv run --frozen python -u /var/tmp/lodge-bench/task-9-fix-profile.py
uv run --frozen python /var/tmp/lodge-bench/task-9-fix-clear.py
```

Store: `/var/tmp/lodge-bench/s90000`, native disk, Python 3.13.5, SQLite 3.47.1.
Only this build runs against the store, with one benchmark call at a time.
The profile populates the current build's index through `waiting`, selects its 160,800 stored values, decodes the plain JSON outside the reconstruction interval, disables cyclic collection, and times three complete `from_plain` loops.
It then profiles a separate complete loop with cProfile.
The baseline follows the same reconstruction loop on the unchanged build's plain values; its existing marshal deserialisation is outside that timed interval.
The final digest is `48e7f60cd9c525b3`.

| Measurement | Sample 1 (s) | Sample 2 (s) | Sample 3 (s) | Best (s) |
|---|---:|---:|---:|---:|
| Before: `from_plain`, 160,800 units | 2.464901 | 2.456012 | 2.468938 | 2.456012 |
| After: `from_plain`, 160,800 units | 0.550109 | 0.545041 | 0.548061 | 0.545041 |
| After: per-key SELECT, JSON decode, and reconstruction | 1.529874 | 1.525019 | 1.514729 | 1.514729 |
| Clear and commit on a full index copy | 0.057805 | 0.056172 | 0.051172 | 0.051172 |

Reconstruction is about 4.5 times faster and within 0.096 seconds of the plan's 0.45-second estimate.
This figure includes exact scalar and nested type validation.
The whole parse-cache lookup remains 1.515 seconds, above the plan's whole-cache estimate; it is not claimed to meet the later changed-read budget.
No time assertion was added to pytest.
Raw final timings and the profile are in `task-9-fix-profile-final.log` under the benchmark folder.
One intermediate run was discarded because source edits during cache population changed the digest before the measurement opened its database.
The final run holds source fixed throughout.

The new index occupies 145,293,312 bytes and holds all 160,800 units, about 904 bytes per unit, below the 241,200,000-byte cap for that tree.
The clear benchmark makes three SQLite backup copies under the benchmark folder, with copying and checkpointing outside the interval.
Every copy drops from 160,800 rows and 145,293,312 used bytes to zero rows and 16,384 used bytes, raises epoch 1 to 2, and preserves its inode and 145,293,312-byte file size.
Each uses WAL, `synchronous=NORMAL`, `secure_delete=OFF`, and `journal_size_limit=16777216`; the WAL is zero after the untimed truncating checkpoint.
Raw clear observations are in `task-9-fix-clear.log`.
The original Task 9 replay tables are historical and were not rerun in full for this fix round; the current CLI parity tests cover default, disabled, warm, read-only, and non-UTF-8-path cases.

## Remaining concerns and hand-offs

I4 and M10 are report-only: Task 10a must wire the cap, clear, and keep callers, including parse-only writers, use the tree's file count, name `INDEX_FILE_CAP`, and make `meta.kept` mean a state kept.
Task 10b must add its virtual-table clear behaviour with its FTS table and tests.
M11 is report-only for Task 8c: `identity.committed` must key a gitlink by the blob of its empty read text, matching `read_tree`.
The review's related SHA-256 repository limitation also remains: committed keys can be 64 hex characters while lodge's disk hash is 40, causing misses rather than wrong hits.
The retirement path inside `core.apply` still performs its own uncached load because core cannot consume the app's index port; this round does not change the package boundary.
Post-open physical corruption can still leave a cache cold on later reads until manual reclamation, as the plan specifies; partial good keys now survive each lookup.
Per-key SQL lookup remains required by this dispatch, so M9's batching suggestion is not applied.
No personal paths or machine names are added to source, tests, or this report.
No record is added, no later task is implemented, and no decision is needed.

## Final gate and delivery

Command: `UV_FROZEN=1 sh scripts/check.sh`, with the normal index setting.
It exited 0 before the commit:

```text
633 files already formatted
All checks passed!
Success: no issues found in 250 source files
1866 passed, 2 skipped in 83.38s (0:01:23)
ok
note: area storage: order changed
```

Vulture also passed in that gate.
Full output: `/var/tmp/lodge-bench/task-9-fix-check-final.log`.
`git diff --check` passed, and the public-path scan passed for all 28 changed files.
Delivery is one `Task 9 fix round: ...` commit, with the dispatched Codex trailer, pushed to `origin/read-speed-build`.
No Blocking finding remains in this fix round; the explicitly deferred work and performance limits above remain visible for the next reviews.
