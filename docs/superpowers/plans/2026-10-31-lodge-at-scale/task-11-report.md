# Task 11 build report

Status: Task 11 complete after the coordinator ruling; ready for review.
The dispatch authorises every Task 10b review Minor except conflicts with the plan or a decision.
FOLD-1 is already recorded as d-eg5nra, and SECOND-1 and CONV-1 are read as d-n65rhr and d-egknpk.
No record operation is required or will be run.

## Task 10b fix round

I1 distinguishes query-level fallback from damaged cached data, and I2 filters historical parse candidates against current state rows.
M1 restores removed-source CRLF histories and compares parsed values in the property test.
M2 ranks empty searches from row metadata and fetches only displayed parses.
M3 treats a proven absent exact ID as absent.
M4's cap and M6's interim R11 rule and unused `every` argument are dictated by the plan, so they remain unchanged.
M5 runs the 300-query differential against SQLite, including non-ASCII and digit words.

## Earlier Task 11 context question, now resolved

Earlier NEEDS_CONTEXT: does Task 11's requirement that a seen identity takes no base names and builds no mapping apply only to R11-B, while interim R11-A retains its full-file comparison and uses the folder cache for traversal?
Task 8c's production `candidates()` returns `None` under the dispatched interim R11-A rule.
`CheckoutIdentity.current()` therefore reads all disk files and compares their hashes with `Committed.listing(rev)` to construct the base-relative identity.
Folder rows contain names and kinds that differ from the base, rather than base file hashes, so they cannot provide that comparison on a new store object without the base mapping.
Changing the identity scheme, storing per-file hashes, switching the R11 rule, or dropping the full-file comparison would change behaviour the task does not name.
That pre-skeleton stop is resolved by the coordinator ruling recorded below; the authorised Task 10b fix round remains complete.

## Implementation and review coverage

QueryFallback leaves a valid stored state untouched when a query requires memory or FTS is unavailable; damaged stored data still raises Miss and can be healed by a complete keep.
Proven absent exact IDs and historical parses absent from current rows no longer invalidate the state.
Empty and filter-only queries rank metadata through core.rank, and only displayed records load their parses.
The real-file regression deletes a committed synthetic record, keeps the new state, and proves all six following searches equal the exact reader without calling memory search, keeping a state, or changing the epoch.
The query-fallback tests repeat six reads with a one-byte cap, count keeps, and verify an unchanged epoch, including unavailable FTS.
The differential now runs 300 queries each against MemoryIndex and IndexDB, with café, 港口, Straße, and numeric words in the vocabulary, and counts unnecessary keeps.
The CRLF property test keeps its source-removal histories, compares line-normalised text and parsed values, and retains one-way identity consistency over normalised texts.
Its existing test was run under both interim R11-A and the R11-B test switch.

Existing tests edited: test_search_prints_as_in_memory gains the real-index parameter, richer vocabulary, and zero-keeps assertion; the search_store fixture gains that vocabulary; the two damaged-row tests use the port's None sentinel for corruption rather than a proven empty result; test_random_edits_agree retains CRLF history and checks parsed equivalence.
The Task 10b Files list is amended for the extracted lookup helper, property regression, and two new regression files, as the dispatch's hand-off rule requires.
No Index port or schema changes are made.

M4 remains report-only: the production cap still cannot fit the larger stores' complete state with FTS, pending DISK-1 and Task 12.
M6's production R11-B alternative remains dormant pending STALE-1, and the every argument remains in the plan's candidate interface.
The six R11-A-only cases to revisit with an R11 ruling are test_removed_attributes_agree[ident], test_removed_attributes_agree[working-tree-encoding=UTF-16], test_removed_attributes_agree[filter=berth], test_removed_attributes_agree[text eol=crlf], test_every_file_read_without_a_conversion_source, and test_r11a_does_not_compute_git_candidates.
No R11 decision is inferred.

## Failing-test evidence

Output below is excerpted verbatim, omitting traceback paths and object addresses.
The first regression run, before the implementation, failed all six initial cases in 0.44 s; the complete final regression set was also run against the original indexed.py, with the cap forced low to exercise epoch clearing.

Command: `uv run --frozen pytest tests/app/test_indexed_search_review.py -q`.

```text
E           AssertionError: assert 3 == 0
E           AssertionError: assert 3 == 0
E           AssertionError: assert 3 == 0
E               AssertionError: must use stored rows
E           assert 100 <= 3
E               AssertionError: must use stored rows
E           AssertionError: assert 3 == 0
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args0]
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args1]
FAILED tests/app/test_indexed_search_review.py::test_query_fallback_does_not_keep_or_change_epoch[args2]
FAILED tests/app/test_indexed_search_review.py::test_deleted_record_does_not_send_search_to_memory
FAILED tests/app/test_indexed_search_review.py::test_empty_search_fetches_only_displayed_parses
FAILED tests/app/test_indexed_search_review.py::test_unknown_exact_id_uses_stored_absence
FAILED tests/app/test_indexed_search_review.py::test_unavailable_fts_does_not_keep_complete_state
7 failed in 0.48s
```

The strengthened existing 300-query differential also failed on the original implementation for both adapters.
Command: `uv run --frozen pytest tests/app/test_indexed_search.py -q -k search_prints`.

```text
E           AssertionError: assert 32 == 0
E           AssertionError: assert 32 == 0
FAILED tests/app/test_indexed_search.py::test_search_prints_as_in_memory[False]
FAILED tests/app/test_indexed_search.py::test_search_prints_as_in_memory[True]
2 failed, 13 deselected in 20.01s
```

The real deleted-file test was run against the original implementation before using the fix.
Command: `uv run --frozen pytest tests/e2e/test_search_deleted_file.py -q`.

```text
E               AssertionError: must use stored rows
FAILED tests/e2e/test_search_deleted_file.py::test_six_searches_after_deleted_record_use_stored_rows
1 failed in 0.56s
```

Restoring the CRLF history before changing its assertions failed under the R11-B test switch.
Command: `uv run --frozen python` invoking `pytest.main(['tests/gitstore/test_identity_property.py', '-q', '-x'])` within identity_rules.r11b().

```text
E           AssertionError: assert {'lodge/decis...6530749', ...} == {'lodge/decis...1fbc493', ...}
E             Differing items:
E             {'lodge/decisions/record-29.md': '1256ee5b89faf459873751d6677b61268f189966'} != {'lodge/decisions/record-29.md': '8342dc7293138208401bb2ec1672592098201473'}
FAILED tests/gitstore/test_identity_property.py::test_random_edits_agree - As...
1 failed in 10.34s
```

After the assertion fix, R11-B's property run passes in 13.84 s.
The targeted search, structure, and regression suite passes 61 tests in 23.09 s, and the real deleted-file regression passes in 0.57 s.
The R11-A property run passes with the targeted suite, 22 tests in 32.29 s.

## Gate and timings

`UV_FROZEN=1 sh scripts/check.sh` exits 0.
Ruff format checks 674 files, Ruff passes, strict mypy checks 288 source files, Vulture passes, and pytest reports 2,158 passed and six skipped in 196.13 s.
`lodge check --gate` prints `ok` and the existing `note: area storage: order changed`.
The environment variable keeps the script's uv invocations frozen.
The fix round is committed as `Task 10b fix round: avoid rebuilding complete search states` and pushed to `origin/read-speed-build`.
At the earlier context stop, Task 11 had no implementation, replay, identity timing, or FUSE claim.

## Task 11 coordinator ruling and scope

The coordinator rules that the no-base-names and no-mapping requirement binds R11-B only.
Interim R11-A still reads and hashes every file, retains its base comparison mapping, and uses folder rows to find untracked names without a full names walk.
Both branches use Task 8c's single `candidates()` switch; production stays R11-A.
R11-B cases remain beside the active tests, skipped with "awaits the author's STALE-1", and will run through a scratch switch, including twenty property runs.
Step 4 measures both branches.
FOLD-1's record step is already complete as d-eg5nra; no `lodge add` is needed or run.

The Files list is extended for the construction hand-off through `setup.py`, `checkout.py`, and `listing.py`, the schema in `index_schema.py`, and the extracted committed-tree helper needed to keep identity below 300 lines.
The folder snapshot needs a completeness count in `meta` so a missing subfolder row cannot silently hide its contents; this is disposable cache metadata, with no Index port change.
Skeleton validation and failing-test evidence follow as work proceeds.

## Task 11 skeleton and red tests

Before tests, `uv run --frozen pytest tests/test_structure.py -q` passes 39 tests in 0.53 s, and `uv run --frozen mypy` passes 289 source files.
The new folder API's concrete body raises `NotImplementedError` in that skeleton.
The Files list also includes `disk.py` for descriptor-relative folder stat and listing and `test_folder_property.py` for the existing history oracle with a persistent cache.

Commands: `uv run --frozen pytest tests/gitstore/test_folders.py -q` and the same file through the scratch R11-B switch, enabling its skipped parameters.
Every named Task 11 test ran red before the construction hand-off or implementation, including all link and corrupt-row parameters.
The output excerpts omit temporary paths and object addresses.

```text
E       TypeError: open_store() got an unexpected keyword argument 'index'
19 failed, 19 skipped in 2.36s
```

The scratch R11-B run also reports `TypeError` at that hand-off for all nineteen cases:

```text
19 failed, 19 deselected in 1.84s
```

Command: `uv run --frozen pytest tests/gitstore/test_folder_property.py -q`.

```text
E       TypeError: open_store() got an unexpected keyword argument 'index'
FAILED tests/gitstore/test_folder_property.py::test_folder_property_r11a
1 failed, 1 skipped in 0.34s
```

Initial green results are nineteen folder cases in each branch, 3.93 s for R11-A and 3.94 s for R11-B.
The interrupted-write case uses the existing SQLite connection fault injector, fails each statement of the write transaction including its commit boundary, verifies the earlier rows survive whole, and then compares the next read with the exact tree.

## Integration findings and additional red evidence

The first full gate exposes the existing `test_git_status_refresh_does_not_write_a_seen_state` premise: its folders were created within the two-second racy window, so Task 11 correctly re-lists and rewrites their rows.
Its focused run fails before the test hand-off, with the byte-for-byte index assertion unchanged:

```text
E       AssertionError: assert {PosixPath(...): ...} == {PosixPath(...): ...}
FAILED tests/e2e/test_indexed_reads.py::test_git_status_refresh_does_not_write_a_seen_state
1 failed, 4 deselected in 0.31s
```

Under the dispatch's required hand-off rule, the Task 11 Files list adds that existing test.
It now primes folder rows with a listing time beyond the racy window before measuring the unchanged no-write assertion; no existing assertion is removed or weakened.
The actual racy-window behaviour remains covered separately in `test_change_in_the_same_second_as_the_listing`.
No Tasks 1 to 9 test or implementation file is changed apart from Task 11's explicitly named identity and index hand-offs.

Two additional corruption cases fail before the fallback fix:

```text
E       RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
E       TypeError: 'NoneType' object is not subscriptable
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-deep_json]
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-missing_meta]
2 failed, 2 skipped, 38 deselected in 0.56s
```

Folder reads now handle these as misses, like the existing disposable-index reader.
R11-B gitlink probes find two further integration issues: a known non-blob may reference a missing object, and an unavailable folder cache must retain the full walk's type so the candidate path includes the base's non-blobs.
Before those fixes, all six scratch-switch combinations of absent, empty, and populated gitlinks with a usable or unavailable index fail:

```text
E       lodge.app.errors.LodgeError: fatal: git cat-file: could not get object info
E       AssertionError: assert dict(listing.blobs) == dict(tree.blobs)
6 failed, 48 deselected in 1.27s
```

They now pass, six cases in 1.09 s.
The persistent-cache R11-B property test was also run against the pre-task source in scratch and fails at the missing `index` construction argument, one failed and one deselected in 0.34 s.

A byte-named untracked folder also fails before the cache-write fallback handles encoding errors:

```text
E       UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 16: surrogates not allowed
FAILED tests/gitstore/test_folders.py::test_unencodable_folder_path_is_a_cache_miss[a]
1 failed, 1 skipped, 54 deselected in 0.37s
```

Finally, an index change after each overlay build exposes a stale pending lazy overlay surviving the exact fallback.
Before clearing that pending overlay, the scratch R11-B race test fails:

```text
E       AssertionError: assert dict(listing.blobs) == dict(tree.blobs)
FAILED tests/gitstore/test_folders.py::test_index_race_after_overlay_keeps_exact_fallback
1 failed, 56 deselected in 0.31s
```

The pending overlay is now cleared before the single exact fallback tree is returned.
The first full gate reports 2,179 passed, 28 skipped, and the one existing no-write-premise failure in 221.76 s; its updated premise passes the focused test in 0.24 s.
The final gate will be rerun on the completed code.

## Final implementation coverage

Schema 6 adds the base-relative `folders` table and its complete-snapshot count in `meta`.
Folder stats and listings use Task 8c's descriptor-relative disk reader, with `lstat` before listing and the listing time afterwards.
Matching mature rows avoid directory listing, and changes to the base, inode, mtime, ctime, or row data force a relist.
A link never contributes descendant rows, and folder writes replace their whole snapshot in one explicit write transaction.
A partial walk with an unlistable folder keeps the earlier snapshot, so permission recovery is retried instead of hidden by a parent hit.
R11-B includes the full base candidate set on an unlistable walk, matching the exact reader.
R11-A keeps hashing every file and retains its comparison mapping; R11-B defers full mapping construction until `listings()` and resolves only named changed inputs during identity construction.
The production R11 function remains unchanged.
The application Index port, immutable state and parse semantics, cap, and SECOND-1 output lifecycle are unchanged.
The gate and writes still consume exact trees; the viewer still has no stored read model.

The Files list adds `test_folder_recovery.py` for partial-walk recovery.
Before its fix, the two R11-A parameters fail:

```text
E       AssertionError: assert dict(listing.blobs) == dict(tree.blobs)
FAILED tests/gitstore/test_folder_recovery.py::test_unlistable_folder_recovers[a-False]
FAILED tests/gitstore/test_folder_recovery.py::test_unlistable_folder_recovers[a-True]
2 failed, 2 skipped in 0.55s
```

R11-B's existing-folder parameter also fails while the folder is unreadable, before including all base candidates on that miss.
Its final focused run passes both parameters in 0.42 s; R11-A passes both in 0.44 s.
The existing R11-B suite initially exposes four removed-conversion-source cases: the uncached walk must retain Task 8c's symmetric difference and non-blob candidates rather than read every path.
That integration is fixed without changing any Task 8c test.
With the six known R11-A-only cases deselected and the four dormant R11-B cases enabled, all 95 applicable existing identity, flags, conversion, listing, and exact-blob tests pass in 19.82 s.
The initial twenty-run scratch property sequence passed, and a final twenty-run sequence is being recorded after the additional fault fixes.

The expanded FUSE run initially cannot create a non-UTF-8 filename, returning EILSEQ in the fixture before any cache operation.
That optional byte-name case now skips only on EILSEQ; its native-disk case still tests the cache-write fallback.
This is a filesystem capability limit, rather than evidence of a stale signature.
Final FUSE results and any signature-related fallback follow below.

An intermediate full gate is green: 2,187 passed, 36 skipped in 210.82 s, followed by `lodge check --gate` printing `ok` and the existing `note: area storage: order changed`.
The gate is running again with the partial-walk recovery fix.
Benchmark preparation uses a local clone of the synthetic `s90000` under `/var/tmp/lodge-bench/task11`, the existing native Python and virtual environment, and compiled source copies whose only branch difference is the one R11 function.

## Initial named-test failure list

The first folder run's failure summary identifies every original case:

```text
FAILED tests/gitstore/test_folders.py::test_unchanged_folders_are_not_listed[a]
FAILED tests/gitstore/test_folders.py::test_seen_identity_takes_no_base_names[a]
FAILED tests/gitstore/test_folders.py::test_new_file_in_a_listed_folder[a] - ...
FAILED tests/gitstore/test_folders.py::test_new_subfolder_with_a_file[a] - Ty...
FAILED tests/gitstore/test_folders.py::test_deleted_untracked_file[a] - TypeE...
FAILED tests/gitstore/test_folders.py::test_rename_within_a_folder[a] - TypeE...
FAILED tests/gitstore/test_folders.py::test_deleted_attachment_is_absent[a]
FAILED tests/gitstore/test_folders.py::test_folder_replaced_by_link_drops_its_rows[a-copy]
FAILED tests/gitstore/test_folders.py::test_folder_replaced_by_link_drops_its_rows[a-other]
FAILED tests/gitstore/test_folders.py::test_folder_replaced_by_link_drops_its_rows[a-attachments]
FAILED tests/gitstore/test_folders.py::test_change_in_the_same_second_as_the_listing[a]
FAILED tests/gitstore/test_folders.py::test_mtime_set_back_still_detected[a]
FAILED tests/gitstore/test_folders.py::test_base_change_relists[a] - TypeErro...
FAILED tests/gitstore/test_folders.py::test_read_only_index_falls_back_to_the_walk[a]
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-missing]
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-undecodable]
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-bad_kind]
FAILED tests/gitstore/test_folders.py::test_damaged_folder_row_is_a_miss[a-traversal]
FAILED tests/gitstore/test_folders.py::test_interrupted_folder_write_lists_again[a]
```

The expanded FUSE run also shows that this filesystem does not enforce the directory permission bits used by the recovery fixture.
The fixture now checks that the folder is actually unreadable and skips when the filesystem cannot exercise that scenario, as it already does for root.
Those two initial failures occur at the assertion that the fixture is unreadable, while the indexed and exact listings themselves agree.
They are fixture capability limits, alongside the EILSEQ byte-name limit, rather than stale folder signatures.
No signature discrepancy has been observed; the final capability-aware FUSE rerun is recorded below.

## Final verification

`UV_FROZEN=1 sh scripts/check.sh` exits 0 on the final implementation.
Ruff format checks 679 files, Ruff passes, strict mypy checks 293 source files, Vulture passes, and pytest reports 2,189 passed and 39 skipped in 213.99 s.
`lodge check --gate` prints `ok` and the existing `note: area storage: order changed`.
After the fixture portability checks, formatting, Ruff, strict mypy, and the native recovery tests pass again.

The final R11-B folder suite passes 29 cases, and both recovery parameters pass separately.
The final twenty scratch-switch property runs each pass the existing 200-history oracle through the persistent folder cache.
Command: `for run in {1..20}; do uv run --frozen python /var/tmp/lodge-bench/task11-r11b-tests.py tests/gitstore/test_folder_property.py -q -k r11b || exit; done`.
The scratch helper selects only the dormant branch cases, removes their STALE-1 skip markers in memory, and patches the single production `candidates()` function through Task 8c's existing `identity_rules.r11b()` helper.
No production source switch is made.
All twenty pass; elapsed times range from 15.20 s to 17.98 s, totalling 326.13 s.

FUSE command: `uv run --frozen pytest tests/gitstore/test_folders.py tests/gitstore/test_folder_recovery.py tests/gitstore/test_folder_property.py --basetemp="$FUSE_TEST_ROOT" -q`, with a fresh temporary folder on the available `fuseblk` mount.
The production R11-A run passes 28 cases, with 36 skipped, in 48.38 s.
The scratch R11-B run of the same files passes 29 cases, with three skipped, in 51.80 s.
The three capability skips are the byte-name case and the two directory-permission recovery parameters; the remaining production skips await STALE-1.
The cache's supported FUSE cases agree with the exact reader, so no filesystem signature fallback is needed.
No benchmark store is placed on that mount; these are isolated test repositories only.

## Timing method

The store is the local synthetic clone `s90000`, with 160,800 committed paths under `lodge/`.
Command: `uv run --frozen python /var/tmp/lodge-bench/task11/bench.py`.
The driver runs separate children with the native environment's Python, isolated configuration (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`, and a synthetic HOME), and source copies whose sole R11 branch difference is `candidates()`.
Both source trees and the native environment's bytecode are compiled before timing.
Every replay row takes the best of three complete processes and compares stdout, stderr, and exit status with the exact reader (`LODGE_INDEX=off`).
Two untimed sightings before each command prime SECOND-1, including after earlier exact-tree commands clear an over-cap state.
The driver records kept-state counts and epochs around every timed sample, so a production-cap clear is reported as cold, rather than claimed as a kept hit.

The preliminary replay confirms why the per-command warm-up matters: its exact `spec` command clears the over-cap state, so priming only at each branch's start would mix later cold builds into a seen sample set.
That preliminary run is excluded from the final timing table.
The final driver warms each command twice before taking its three samples, without changing the production cap or any implementation code.
Its early production point sample was a kept hit with identical output, one state, and an unchanged epoch; the final table will supersede that preliminary timing.

The final replay's indexed samples are checked for a kept state before and after, with no epoch change inside the sample.
Exact-tree command warm-ups may clear the over-cap state; two sightings before each following command restore its seen-state premise.
Per-command identity shares also use the best of three instrumented runs, separately from the three ordinary process totals.

## Process deviation

The pre-test skeleton covered the new `folders.py` signatures and passed structure and strict mypy, but it did not yet add the optional `index` argument throughout the store-construction hand-off.
Those signatures were added with the implementation after the first red runs, whose failure is therefore the recorded unexpected-keyword `TypeError`.
This falls short of Global Constraint Step 0's complete hand-off skeleton order.
It does not change the red-before-implementation evidence or the final structure, strict mypy, full gate, and differential results, but is recorded as a process concern rather than claimed as exact compliance.

## Recorded Task 11 timings

Native ext4; Python 3.13.16, PyYAML 6.0.3, libyaml 0.2.5, SQLite 3.53.1, and git 2.56.0.
The native virtual environment and both source copies have compiled bytecode.
The two additional phase runs use `uv run --frozen python /var/tmp/lodge-bench/task11/phase_repeats.py`, and the final isolated probes use `uv run --frozen python /var/tmp/lodge-bench/task11/identity_repeats.py`.
The isolated probe resets its stage counters after constructing the store and before starting the identity timer, excluding construction from both the total and the stage cells.
R11-A is production; R11-B is a scratch copy changing only the existing `candidates()` body.
All 96 timed replay samples agree with the exact reader in stdout, stderr, and exit status.
Each process total and identity share is best of three; the identity column comes from separate instrumented runs of that command, rather than an additive phase claim.
All 78 indexed samples start and finish with a kept state and an unchanged epoch.

| Command | R11-A total (s) | R11-B total (s) | R11-A identity (s) | R11-B identity (s) |
|---|---:|---:|---:|---:|
| `show {code}` | 1.996342 | 0.395327 | 1.740007 | 0.165465 |
| `show {entry} --reasoning --provenance` | 1.992074 | 0.401483 | 1.753248 | 0.163926 |
| `show {decision}` | 1.993627 | 0.401582 | 1.753880 | 0.167892 |
| `search berth --brief` | 5.089430 | 3.490324 | 1.745442 | 0.160222 |
| `search "berth crane" --brief` | 6.106834 | 4.539031 | 1.746246 | 0.165140 |
| `search {code} --brief` | 2.547562 | 0.956415 | 1.748698 | 0.162878 |
| `search berth` | 5.098621 | 3.519403 | 1.737891 | 0.163356 |
| `waiting` | 1.988143 | 0.389010 | 1.753040 | 0.161349 |
| `threads` | 1.991087 | 0.403477 | 1.739863 | 0.160918 |
| `spec --area area-001` | 6.557466 | 6.553013 | exact trees | exact trees |
| `check` | 6.508914 | 6.518049 | exact trees | exact trees |
| `check --gate` | 8.901007 | 8.922663 | exact trees | exact trees |
| `show {code} {code2} {entry}` | 1.994079 | 0.403856 | 1.746841 | 0.169675 |
| `show A` | 2.002022 | 0.405262 | 1.756994 | 0.161697 |
| `search berth tide --brief` | 8.374318 | 6.729058 | 1.742739 | 0.163947 |
| `search --phrase "berth crane" --brief` | 6.803707 | 5.218912 | 1.734192 | 0.163180 |

The exact-tree commands have no clears during their timed samples; their rows remain exact-tree measurements, outside the indexed seen target.
The replay epochs rise by 2 in total between each branch's first and last sample, including the intervening warm-ups.
The per-command warm-up restores the indexed state after those clears.
The largest observed kept working set is 251,650,048 used bytes, against the unchanged 241,200,000-byte cap.

New-store `identities()` is timed separately, best of three, with construction and imports outside the timer as in Task 8c.
The stage cells are disjoint times from the best run; no full names walk runs in any of these warmed folder cases.

| Configuration | Branch | Total (s) | Git group | Serial git | Base mapping | Folder cache | Flag scan | Conversions | Read/hash overlay | Other |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| No conversion source | R11-A | 1.750162 | 0.000000 | 0.061453 | 0.133725 | 0.015453 | 0.000000 | 0.000000 | 1.531524 | 0.008007 |
| No conversion source | R11-B | 0.157595 | 0.121282 | 0.008657 | 0.000000 | 0.015286 | 0.011836 | 0.000216 | 0.000005 | 0.000313 |
| `core.autocrlf=input` | R11-A | 1.746958 | 0.000000 | 0.064529 | 0.128993 | 0.014921 | 0.000000 | 0.000000 | 1.530695 | 0.007821 |
| `core.autocrlf=input` | R11-B | 1.937911 | 0.166342 | 0.063059 | 0.126456 | 0.015190 | 0.012182 | 0.011169 | 1.538004 | 0.005509 |

The no-conversion R11-B identity calls neither `Committed.listing()` nor the full disk names walk.
Under `core.autocrlf=input`, R11-B intentionally enumerates the base and reads every potentially converted file; CONV-1 reports that configuration beside the targets.
R11-A reads every file under both configurations, as the interim rule requires.

## Concerns and hand-off

STALE-1 remains with the author; this task does not select R11-B for production.
Production R11-A still exceeds the seen target because every file is read and hashed.
The scratch R11-B point reads also remain above 0.3 s in this replay; the folder optimisation does not by itself meet the target.
Broad-search cost and any other missed target remain for Task 12 to classify and apply d-26e6zj; no threshold or cap is changed here.
The kept state exceeds the production cap until a writer next checks it; exact-command warm-ups can therefore discard it.
DISK-1 and the deferred facts policy remain open as in the preceding task reports.
The FUSE capability skips leave byte names and enforced permission recovery covered on native disk only.
Per-path git object lookups are limited to named changed inputs when R11-B has no full base mapping; a large untracked overlay may still add process overhead.

Delivery commit: `Task 11: cache base-relative folder signatures`.
No `lodge add` or record edit was run.
