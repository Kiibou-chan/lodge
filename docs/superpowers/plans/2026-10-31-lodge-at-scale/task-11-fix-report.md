# Task 11 fix round

Status: complete.
Scope: Task 11 review I1, I2, and M1 to M11, with the author's STALE-1 and DISK-1 rulings.
No record operation is needed or run.

Before changes: 2,254 collected tests.
The four affected original modules run as 50 passed and 37 skipped; the committed full-gate baseline is 2,215 passed and 39 skipped.

Rulings, red run: `uv run --frozen pytest tests/gitstore/test_index_cap_ruling.py tests/gitstore/test_identity_fix_round.py::test_production_uses_stat_candidates tests/gitstore/test_identity_lazy.py::test_removed_attributes_follow_the_index tests/gitstore/test_folders.py::test_seen_identity_takes_no_base_names -q`.
Output excerpts, before production changes (printed values and test paths shortened; full failure logs are retained as `t11-*-red.log` under the benchmark directory):

```text
FAILED test_index_cap_ruling.py::test_authorised_index_cap: assert 1500 == 1900
FAILED test_identity_fix_round.py::test_production_uses_stat_candidates: assert 0 == 1
FAILED test_identity_lazy.py::test_removed_attributes_follow_the_index[ident]
FAILED test_identity_lazy.py::test_removed_attributes_follow_the_index[working-tree-encoding=UTF-16]
FAILED test_identity_lazy.py::test_removed_attributes_follow_the_index[filter=berth]
FAILED test_identity_lazy.py::test_removed_attributes_follow_the_index[text eol=crlf]
FAILED test_folders.py::test_seen_identity_takes_no_base_names: AssertionError: base names
7 failed in 9.17s
```

The R11-A full-file branch, its four removed-attribute agreement parameters, its no-source full-read assertion, and its no-candidate assertion are removed.
The four R11-B removed-attribute parameters now run without skips, including exact `trees()` assertions for the gate and `add`.
Folder tests run once against production, without duplicate A/B parameters or a scratch switch.
The property oracle runs against production R11-B; M8's conditional R11-A byte assertion has no remaining R11-A route to apply to.
CONV-1's conversion route and tests remain.

The new `Committed.folder` and `disk.open_root` signatures were introduced as `NotImplementedError` skeletons before the new fix regressions: structure, 39 passed; strict mypy, 296 files clean.

`uv run --frozen pytest tests/gitstore/test_folder_fix_round.py -q`, with production R11-B already active, failed before the fixes:

```text
test_folder_rows_are_scoped_to_each_checkout:
E AssertionError: relisted another checkout
test_three_hundred_changes_use_constant_git_processes[False]:
E AssertionError: 305
E assert 305 <= 6
test_three_hundred_changes_use_constant_git_processes[True]:
E AssertionError: 606
E assert 606 <= 6
test_reference_time_precedes_lstat_and_scan[1000000000]:
E Right contains 1 more item:
E {'lodge/decisions/late.md': '02a708592a3f013fe350d25b313180d62f19b9b3'}
test_reference_time_precedes_lstat_and_scan[2000000000]:
E Right contains 1 more item:
E {'lodge/decisions/late.md': '02a708592a3f013fe350d25b313180d62f19b9b3'}
test_clear_preserves_folder_hits:
E AssertionError: clear lost folder rows
test_one_changed_folder_writes_and_lists_only_it:
E AssertionError: full base map
test_vanished_rows_are_deleted_without_rewriting_others:
E assert (1 == 1 and "path='lodge/decisions/temporary'" in 'DELETE FROM folders')
test_failed_refresh_cannot_materialise_an_empty_lazy_listing:
E Failed: DID NOT RAISE RuntimeError
9 failed in 3.48s
```

`uv run --frozen pytest tests/gitstore/test_disk_descriptor_stack.py -q` failed before the descriptor change:

```text
E AssertionError: 16654
E assert 16654 < (4 * 180)
1 failed in 0.29s
```

`uv run --frozen pytest tests/gitstore/test_committed_batch.py -q` failed before batching:

```text
E AssertionError: assert 6 == 1
1 failed in 0.30s
```

`uv run --frozen pytest tests/gitstore/test_folder_fix_round.py::test_invalid_extra_row_is_removed_when_snapshot_heals -q` failed before the incremental writer's recovery fix:

```text
E AssertionError: invalid row never healed
1 failed in 0.47s
```

The process bound was corrected from six `attempt` calls to ten after the first implementation showed eight on the tracked case, including fixed setup and configuration work.
The seven concurrent git calls are separately fixed by `run_many`, giving a bound of seventeen processes independent of the 300 changed paths.
The folder-listing spy now observes `attempt`, which handles missing base folders, rather than only `run_bytes`.
These corrections retain the original failures at 305 and 606 calls and the prohibition on full base mappings.
The final focused regression run passes 42 tests, and the wider identity, folder, property, fault, and structure run passes 152 tests.

I1: `folders` has primary key `(root, path)`, where `root` is the absolute git dir, with `folder_roots(root, folder_count)` completeness and schema 8.
Alternating worktrees retain independent hits.
I2: a non-folder `added` name absent from the same folder's `removed` proves the base lacks that path, so it skips lookup; all remaining paths use one `cat-file --batch-check` process.
Its ordinary inputs are `rev:path` lines; the same single batch uses NUL separators when a path contains a line break.
Known unavailable gitlinks retain their empty-text representation without asking git to inspect the absent object.
M1 and M2: the reference time is captured before `lstat`, and the 2 s margin stays; controlled 1 s and 2 s rounded-stat histories both recover the file created during the first scan.
M3 and M4: production R11-B runs in every normal test run and takes no base names on a folder hit; the plan states this in place.
M5: clears retain both independent folder tables, including their per-root counts.
M6: the current path retains at most 64 ancestor descriptors, plus the root and a transient descriptor; the regression also checks that all descriptors close.
M7: the base is listed only for each relisted folder; only changed or vanished rows are written in one transaction, comparing with the current database under its write lock, and malformed extra rows are removed when healing.
M8: R11-A and its tests are removed, so the production R11-B oracle keeps its ruled line-ending comparison; the exact-reader agreement regressions still compare blobs for ordinary histories.
M9: lazy placeholders have a distinct type, and materialising one after a failed refresh raises instead of returning an empty valid-looking listing.
M10: `disk.open_root` replaces the private flag reference, and `listing.py` imports `Committed` directly from its owner.
M11: `folders.py` documents clock, directory metadata, attribute caching, and device assumptions; the plan's existing FUSE sentence also names NFS and SMB.

Existing test edits: `test_flags.py`, `test_identity_fix_round.py`, and `test_identity_lazy.py` drop the scratch R11-B context; the removed-attribute regression replaces R11-A's assertions with the ruled index text and retains exact `trees()` checks.
`test_folders.py` removes A/B duplication, uses the production no-base-names assertions, activates the index-race regression, and adapts interrupted-write fixtures to the scoped schema, with the missing-completeness case renamed from `missing_meta` to `missing_root`.
`test_folder_recovery.py` drops the mode fixture import, and `test_folder_property.py` runs the original 200-history oracle once against production.
The obsolete `identity_rules.py` helper is deleted.
New regressions are in `test_index_cap_ruling.py`, `test_folder_fix_round.py`, `test_disk_descriptor_stack.py`, and `test_committed_batch.py`.

The plan's cap, R11 ruling, folder table, reference-time order, incremental-write rule, and no-base-names paragraph are amended in place, as are the ledger's STALE-1 and DISK-1 entries.
Task 12's report and timings each gain the one sentence naming R11-B / 1,900 as production; no recorded table, benchmark script, or imported benchmark name changes.
The Task 12 stop remains in effect; this fix round starts no later work.

The final collection is 2,230 tests, compared with 2,254 before the round.
The difference is 32 duplicate A/B cases and five R11-A-only cases removed, plus thirteen new regressions; four removed-attribute cases and the formerly always-skipped index race now run in production, and no STALE-1 skip remains.

For M6, a fresh synthetic store is generated with `uv run --frozen python scripts/bench_store.py /var/tmp/lodge-bench/t11-deep-seeded --decisions 1`, then extended by a 1,500-level chain of empty `d` folders.
The traversal probe is `/var/tmp/lodge-bench/t11-deep.py`: an in-memory index, an empty base callback, one priming walk, and three hit walks with `listed_at_ns` three seconds ahead to mature the signatures without sleeping.
Both source trees are compiled with `uv run --frozen python -m compileall -q src/lodge /var/tmp/lodge-bench/t11-before-source/src/lodge`.
The pre-fix source is extracted with `git archive ce5f5e1 src` before the fix commit, under the benchmark directory; no other worktree is used or changed.
Before: `PYTHONPATH=/var/tmp/lodge-bench/t11-before-source/src uv run --frozen python /var/tmp/lodge-bench/t11-deep.py`.
After: `uv run --frozen python /var/tmp/lodge-bench/t11-deep.py`.
The same native-disk store and interpreter are used for both.

| 1,500-level chain hit | Run 1 | Run 2 | Run 3 | Best |
|---|---|---|---|---|
| Before | 2.929157 s | 2.945806 s | 2.956201 s | 2.929157 s |
| After | 0.124569 s | 0.126754 s | 0.123253 s | 0.123253 s |

This measures folder traversal alone, not a complete command or a new Task 12 target claim.
The descriptor-stack regression permits fewer than 720 opens at 180 levels and no more than 66 simultaneously live descriptors.

The first complete gate passes: 2,228 passed, 2 skipped in 223.41 s, with formatting, Ruff, strict mypy, Vulture, and `lodge check --gate` green.
A final protocol assertion was then added to the existing 300-path regression to require ordinary `rev:path` lines, with this failure before adjusting the batch input:

```text
test_three_hundred_changes_use_constant_git_processes[True]:
E AssertionError: assert b'\x00' not in batch input
1 failed, 1 passed in 0.89s
```

Ordinary queries now use lines; names containing line breaks retain the NUL-input route in the same one-process batch.
The final gate runs with `UV_FROZEN=1 sh scripts/check.sh` so all commands inside the gate also use the frozen dependency lock.

The M6 traversal runs use CPython 3.13.5, SQLite 3.47.1, and the native ext-family benchmark file system.

The final frozen gate exits 0: formatting, Ruff, strict mypy over 299 files, Vulture, and pytest are green.

```text
2228 passed, 2 skipped in 218.58s (0:03:38)
ok
note: area storage: order changed
```

The storage-order note is pre-existing.
All requested findings are addressed; no NEEDS_CONTEXT question remains.
The recorded Task 12 target misses and stop remain for the coordinator; this round makes no replacement timing claim for that table.
Delivery is one commit on `read-speed-build`, with subject `Task 11 fix round: activate rulings and harden folder caching`.
