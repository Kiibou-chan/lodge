# Task 10b report

Status: Task 8c fix round and Task 10b complete; the coordinator resolved the earlier file-scope question.
Read the current plan, progress ledger, standing builder rules, Task 8c review and scratch probes, and decisions through `lodge show --reasoning`.
No record writes are required or authorised by this task.
Production retains interim R11-A; SECOND-1 is d-n65rhr, and CONV-1 is d-egknpk.

## Task 8c fix round

The review is copied to `task-8c-review.md`.
A1 preserves the full 1,100-deep exact tree, without the review's proposed depth cap, which conflicts with the dispatched requirement to preserve reads.
B1 concerns the test's removed conversion source and staged CRLF bytes, plus a FIFO swap that R11-B never opens unless the file changes first.
M1 to M6 are addressed, with the required `unlistable` interface retained as explained below.

### Red evidence

The initial regression run was `uv run --frozen pytest tests/gitstore/test_disk_depth.py tests/gitstore/test_identity_fix_round.py -q`:

```text
FAILED tests/gitstore/test_disk_depth.py::test_1100_deep_tree_is_read_with_bounded_descriptors
FAILED tests/gitstore/test_disk_depth.py::test_repository_root_may_be_a_link
FAILED tests/gitstore/test_identity_fix_round.py::test_r11a_does_not_compute_git_candidates
3 failed, 1 passed in 0.72s
```

The unchanged R11-B scratch baseline reproduced B1:

```text
test_random_edits_agree: record-29.md index blob 1256ee5b89faf459873751d6677b61268f189966 != disk blob 8342dc7293138208401bb2ec1672592098201473
1 failed in 9.90s
```

The first baseline run passed in 14.27s, confirming the timing dependence.
The unchanged FIFO test also failed in the scratch R11-B package:

```text
test_regular_file_swapped_for_fifo_before_open: listing blob 67969c3e0daaba8ef035b8cfe1c92e74cd02dbc2 != empty-file blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
1 failed in 0.34s
```

The failed `ls-files` test failed against the pre-fix R11-B package before the conservative fallback was added:

```text
FAILED tests/gitstore/test_identity_fix_round.py::test_failed_ls_files_reads_every_base_path
1 failed in 0.35s
```

The first deep-tree test lost its file under the 128-descriptor soft limit, the root-link test raised `NotADirectoryError`, and the R11-A test raised `AssertionError: unneeded candidate group`.
The parser list equality test passes on the existing complete lists; removing `guide` from the shortcut list in memory makes its new assertion fail.
No parser behaviour change was needed for M6.

```text
  assert set(action.choices) == grammar._COMMANDS == set(COMMANDS)
AssertionError
```

### Implementation and focused verification

A1 uses an explicit folder stack and reopens validated ancestors with a constant descriptor bound, preserving every file at depth 1,100 even under a soft limit of 128 descriptors.
The root may be a link; every folder below it still uses `O_NOFOLLOW`.
M1 removes `Flags.read`, the unused conversion defaults, the unread root field, and the checkout alias assignment; flag tests now execute `CheckoutIdentity.current` under R11-B.
The `unlistable` field stays because Task 8c's documented walk interface produces it for Task 11; the new depth test reads it.
M2 reads every base path if `ls-files` fails.
M3 moves the candidate group into the R11-B branch: `candidates` returns `None` for production R11-A and switches to `identity.stat_current(rev, trunk)` for R11-B.
M4 opens only the repository root without `O_NOFOLLOW`.
M5 recognises the first descriptor listing by call order, removing the test's `/proc` dependency.
M6 compares both command lists with the complete parser's subparser choices.
B1 normalises any remaining CRLF working files before removing the conversion source between sequences, and edits the FIFO target before the swap, so the same tests cover either branch.
The source is still removed each sequence, preserving the property test's ability to detect missing diff and flag handling; dedicated removed-source history tests retain each R11 rule's byte-versus-index coverage.
Existing tests edited: `test_identity_property.py`, `test_identity_links.py`, `test_flags.py`, `test_attributes.py`, `test_identity_lazy.py`, `test_parser_named.py`; `identity_rules.py` supplies an explicit alternative-rule context manager.
The flag and conversion tests now supply the production group's explicit inputs; the staged-race and fallback tests explicitly select R11-B, where those mechanisms execute.
Focused verification: 63 passed, four skipped; strict mypy and the 39 structure checks pass.
The twenty-run scratch R11-B property/FIFO proof passes; all four property mutants fail.

The first attempted property repair retained the attributes file permanently, which let the no-diffs mutant survive because every Markdown path became a conversion candidate.
It was replaced before delivery by normalising the files before each source removal.
All four mutants now fail independently: no-diffs in 0.44 s, no-flags in 0.63 s, no-untracked in 0.47 s, and no-conversions in 2.05 s.

The final candidate branch checks a failing `ls-files` separately from the two diff outputs, avoiding any attempt to interpret flag-tagged names as diff paths.
The four mutants of that final source fail in 0.49 s, 0.69 s, 0.56 s, and 2.16 s respectively.
The first full gate passed: 2,081 tests, six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
The final uninterrupted `UV_FROZEN=1 sh scripts/check.sh` exited 0 before the fix-round commit:

```text
662 files already formatted
All checks passed!
Success: no issues found in 277 source files
2081 passed, 6 skipped in 148.69s (0:02:28)
ok
note: area storage: order changed
```

The storage-order note predates this fix round.
The complete gate log is `/var/tmp/lodge-bench/t8c-fix-gate-final.log`.
`git diff --check` passes.

### Fix-round identity timing

Command: `uv run --frozen python` with three fresh child processes calling `open_store(...).identities()` on synthetic `s90000` under `/var/tmp/lodge-bench`, with `LODGE_INDEX=off`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`, and `GIT_OPTIONAL_LOCKS=0`.
The native virtual environment and source were bytecode-compiled first; imports are outside the measured call, and a new store object is constructed in each process.
Interim R11-A, 160,800 files, samples 2.220533 s, 2.180887 s, and 2.213531 s; best of three 2.180887 s.
This verification ran beside the test suites and is diagnostic, with no speed-up claim against the previous isolated measurements.
No Task 10b search replay timing is claimed while its scope question is pending.

The final scratch R11-B package also passes the four unskipped removed-source history cases and the failed-`ls-files` regression: five passed in 9.00 s.
Production keeps the four R11-B history cases skipped until the author's ruling.

### Twenty-run R11-B proof and delivery

A scratch package under `/var/tmp/lodge-bench/t8c-fix-r11b` differs from the finished production source only in the `candidates` function body, which returns `identity.stat_current(rev, trunk)`.
In twenty fresh subprocesses, run with `PYTHONPATH` pointing at that scratch source, the command was `python -m pytest tests/gitstore/test_identity_property.py tests/gitstore/test_identity_links.py::test_regular_file_swapped_for_fifo_before_open -q`.
Every invocation exited 0 and printed `2 passed`, for twenty property-test passes and twenty FIFO-test passes, with no failures.
The full output is `/var/tmp/lodge-bench/t8c-fix-r11b-proof.log`.
Both the full gate and this proof use the final source, with no further production changes afterwards.
The fix-round commit includes the copied review, implementation, tests, ledger, and this report, with message `Task 8c fix round: preserve deep reads and prove both R11 branches`.
The dispatch's push command follows that commit.

## Task 10b: NEEDS_CONTEXT before the skeleton

The task's file list omits the search dispatch and the modules split out during Task 10a.
`app/lodge.py` routes both search entry points directly to `reads`, and must route them to `indexed` for the CLI to reach indexed search.
`gitstore/index_schema.py` owns schema creation, and `gitstore/index_space.py` owns whole-index clearing, including iteration over every SQLite table; FTS5 requires coordinated creation and drop/re-creation rather than deleting its shadow tables independently.
`tests/app/fakes.py` only re-exports `MemoryIndex` from `tests/app/fake_index.py`, so implementing the specified fake method belongs in that module.
Question: may Task 10b modify `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` to complete those hand-offs, in addition to its listed files?
The dispatch requires an unclear step to be reported and stopped, and prohibits changes to earlier tasks' files unless Task 10b calls for them.
No Task 10b skeleton, tests, implementation, or benchmark has started while this scope question is pending.


## Task 10b build: scope ruling and skeleton

The coordinator authorised `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` for the search and FTS hand-offs described above.
The dispatch also authorises omitted files that the task's own hand-offs require.
`cli/commands.py` must flush search output and call `after_output`, as the existing four indexed CLI reads do, to preserve SECOND-1 for search.
Task 10b's Files list is amended for those five files in the implementation commit.
No earlier task's interface, decision, or unnamed behaviour changes.
The skeleton adds the pure word conversion, FTS adapter functions, the `Index.candidates` port and fake signature, and the indexed search signature before new tests.

### Skeleton and red evidence

Before adding tests, `uv run --frozen pytest tests/test_structure.py -q` passed all 39 checks, and `uv run --frozen mypy` passed for 278 source files.
Both search entry points are wired to the concrete search skeleton; the fake and adapter expose `candidates`.
The new word and search tests were then run before their implementation:

```text
uv run --frozen pytest tests/gitstore/test_index_words.py tests/app/test_indexed_search.py -q
FAILED test_ascii_tokenizer_returns_core_words
FAILED test_any_and_every
FAILED test_path_words_are_not_candidates
FAILED test_words_row_shares_the_parse_rowid
FAILED test_without_fts5_and_sql_errors_are_misses
FAILED test_clear_preserves_word_snapshot_and_recreates_fts
FAILED test_search_prints_as_in_memory
FAILED test_older_parse_of_a_record_is_not_a_candidate
FAILED test_needs_memory_queries_run_in_memory[THE-False]
FAILED test_needs_memory_queries_run_in_memory[of the-True]
FAILED test_without_fts5_runs_in_memory
FAILED test_revert_after_eviction_is_found
FAILED test_words_rows_after_a_clear_and_another_keep[True]
FAILED test_words_rows_after_a_clear_and_another_keep[False]
FAILED test_search_keeps_only_after_second_output_flush
15 failed in 1.01s
```

The search skeleton and candidate methods raised `NotImplementedError`; the rowid assertion found no `words` table.
The separate fault and property tests also failed before implementation:

```text
uv run --frozen pytest tests/gitstore/test_index_words_faults.py tests/e2e/test_index_property.py -q
FAILED test_keep_state_interrupted_leaves_no_searchable_state
FAILED test_locked_word_write_keeps_no_state
FAILED test_index_reads_equal_memory_under_random_edits
3 failed in 0.73s
```

The fault tests reached the candidate skeleton, and the property test reached the search skeleton on its first search.
The complete red logs are `/var/tmp/lodge-bench/t10b-red-search-words.log` and `/var/tmp/lodge-bench/t10b-red-faults-property.log`.
No existing test file is edited for this task; the existing fake adapter gains its required method.
The new property fixture lives in `tests/e2e/index_property_support.py`, an extracted helper for the task's named property test, and is included in the task's Files list.

### Implementation and supplemental regressions

`core.parse_words` returns sorted, space-joined title and statement word sets, with empty columns for non-record parses.
Schema 4 creates optional FTS5 `words(title, statement)` with the `ascii` tokeniser, without a key column.
All parse writers share `insert_parses`, which inserts each words row only with a newly inserted parse row, using that rowid inside the same transaction.
The existing `keep_parses` and `keep_state` signatures, including keyword-only `files`, are unchanged.
A whole-index clear drops FTS before enumerating the remaining tables, re-creates it in the same write transaction, and raises the epoch.
Normal eviction never deletes parse or words units.

Both search entry points use the indexed read model when enabled.
Search joins word candidates with current-state rows by their full parse key, adds exact IDs, code families, and complete citer lists, and passes the same core ranking function its stored word sets.
Phrases retain core's token-run check; empty queries use all state rows.
Several queries share one stored-state read transaction and the loaded records, with the existing per-query limits and duplicate suppression.
A function-word phrase or code, absent FTS5, failed candidate lookup, missing parse, incomplete row result, or incomplete citer list discards the cached search and answers the whole request in memory.
The CLI flushes successful search output before running its optional second-sighting keep.

The initial focused run passed 16 tests and exposed two fixture mistakes, corrected without changing product behaviour.
Changing a title through `files_of` adds a new slug path, so the old-parse and revert tests now overwrite their existing path.
An internal `Read.statuses` comparison was replaced by an item comparison, consistent with the task's printed-output contract and Task 10a's stored reads.
The complete 300-search printed differential, fault injection, and 60-step CLI property then passed: 18 passed in 25.84 s.
The app test now opens its scratch SQLite adapter directly, so it also runs alone without depending on another test directory's collection.

Two additional regressions were written and seen failing before their fixes:

```text
FAILED test_incomplete_rows_discard_the_cached_search[False]
FAILED test_incomplete_rows_discard_the_cached_search[True]
2 failed, 6 passed in 0.49s
FAILED test_sqlite_code_search_uses_stored_rows[BERTH-1]
FAILED test_sqlite_code_search_uses_stored_rows[ROOT]
2 failed in 0.31s
```

The first pair prevents an empty or undecodable row lookup from silently printing no matches.
Conservative fallback also covers historical candidates whose IDs no longer have a state row.
The second pair found that passing the query text itself to bucket lookup causes a miss for code suffixes outside the ID alphabet.
Only a valid record ID is now added as an exact-ID lookup; codes use their family and citer IDs.
The full supplemental logs are `/var/tmp/lodge-bench/t10b-red-incomplete.log` and `/var/tmp/lodge-bench/t10b-red-sqlite-codes.log`.

A final failure-path regression was added after the focused run:

```text
FAILED test_fts_creation_error_rolls_back_the_clear
Failed: DID NOT RAISE OperationalError
1 failed in 0.22s
```

Catching every `OperationalError` from FTS creation would also swallow an unrelated write failure during a clear.
Only the specific absent-FTS5 module error may be ignored; other errors must roll back the clear and preserve the previous state and words snapshot.
The red log is `/var/tmp/lodge-bench/t10b-red-create-rollback.log`.

### Verification in progress

The first full `UV_FROZEN=1 sh scripts/check.sh` exited 0:

```text
668 files already formatted
All checks passed!
Success: no issues found in 283 source files
2103 passed, 6 skipped in 175.28s (0:02:55)
ok
note: area storage: order changed
```

The storage-order note predates this task.
The log is `/var/tmp/lodge-bench/t10b-gate.log`.
The additional FTS-creation rollback regression then passed with the other word tests: seven passed in 0.15 s.
A second complete gate includes that regression and the final error handling before the task commit.

The second uninterrupted `UV_FROZEN=1 sh scripts/check.sh` exited 0 before the exact-ID completeness regression:

```text
668 files already formatted
All checks passed!
Success: no issues found in 283 source files
2104 passed, 6 skipped in 174.00s (0:02:54)
ok
note: area storage: order changed
```

The log is `/var/tmp/lodge-bench/t10b-gate-before-exact-id.log`.
That gate precedes the final exact-ID miss regression and is retained as intermediate evidence.

### Exact-ID completeness regression

A final review of the completeness guard found that an exact-ID row missing from the cache could print no matches when the query's words matched no title or statement.
The regression was written and run before extending the guard:

```text
FAILED tests/app/test_indexed_search.py::test_missing_exact_id_row_discards_the_cached_search
E AssertionError: assert (0, 'fetched ...atches\n', '') == (0, 'fetched ...· Quay\n', '')
1 failed in 0.24s
```

The raw output is `/var/tmp/lodge-bench/t10b-red-exact-id-miss.log`.
Every explicitly requested ID, family member, and citer must now have a row, or the whole search falls back.
This also conservatively falls back for an unknown exact ID, preserving its output.
The earlier timing run was interrupted and discarded, and the gate and replay are repeated on this final implementation.

### Final gate

After the exact-ID guard, the final uninterrupted `UV_FROZEN=1 sh scripts/check.sh` exited 0:

```text
668 files already formatted
All checks passed!
Success: no issues found in 283 source files
2105 passed, 6 skipped in 169.46s (0:02:49)
ok
note: area storage: order changed
```

The log is `/var/tmp/lodge-bench/t10b-gate-final.log`.
The storage-order note is unchanged from before Task 10b.
No implementation or test change follows this gate.

### Search replay

Command: `uv run --frozen python /var/tmp/lodge-bench/t10b-replay.py`, with all six search lines from `scripts/bench_reads.txt`, in both `seen` and `changed` modes.
The script uses fresh, uninstrumented CLI processes, three samples per row, and reports their minimum.
Stores are independent local clones of the synthetic `scripts/bench_store.py` stores under `/var/tmp/lodge-bench/task10b/`; the original stores are untouched.
`s900` has 1,607 files and 1,585 searchable records, `s9000` has 16,120 files and 15,895 records, and `s90000` has 160,800 files and 158,550 records.
The source, virtual environment, and stores are on native disk; source and environment bytecode are compiled before replay.
The interpreter is CPython 3.13.5, with PyYAML 6.0.3, libyaml enabled, and SQLite 3.47.1 with FTS5.
Git's global and system configuration and system attributes are isolated, with a synthetic home under the benchmark folder, and no conversion source.
Task 8c's interim R11-A rule still reads and hashes the working-tree files on every identity lookup.

Two successful initial reads populate the baseline state under SECOND-1 before timing seen reads.
Every changed sample restores that baseline index, changes the same synthetic entry, and measures its first sighting, including the marker write and process exit.
The changed read runs the full in-memory ranking; its later complete keep is outside these timed first sightings.
A separate diagnostic process counts the candidates passed to core's rank on the actual path, after the timing samples, without adding instrumentation to the measured processes.
For two queries, counts are listed in query order.
Seen counts include word candidates admitted by their current parse key, plus exact code family and citer records; changed counts are the full in-memory candidate pool.
Every timed sample compares stdout, stderr, and exit status with `LODGE_INDEX=off` on the same store and edit.
All timings are provisional under d-26e6zj and d-hxmdkz.
The largest store's baseline index uses 250,286,080 bytes against its 241,200,000-byte cap, with one complete state, epoch 1, and all 160,800 parse units.
Epoch measurements around each uninstrumented sample confirm the largest-store changed samples take the cap clear on their first writer and is classified as cold under the plan, shown as `changed (clear, cold)` below.
`s9000` also clears: its baseline uses 25,763,840 bytes against its 24,180,000-byte cap.
Only `s900` has ordinary changed rows, with 2,760,704 used bytes below the 16,777,216-byte minimum cap.
The epoch is read outside the measured process before and after each sample; every clear row has three confirmed epoch increases, and every seen row has none.

| Store | Mode | Search | Candidates | Best of three (s) | Identical |
|---|---|---|---:|---:|---|
| s900 | seen | `search berth --brief` | 676 | 0.198948 | yes |
| s900 | seen | `search 'berth crane' --brief` | 1081 | 0.211400 | yes |
| s900 | seen | `search CODE-9 --brief` | 8 | 0.178661 | yes |
| s900 | seen | `search berth` | 676 | 0.202748 | yes |
| s900 | seen | `search berth tide --brief` | 676, 698 | 0.225366 | yes |
| s900 | seen | `search --phrase 'berth crane' --brief` | 1081 | 0.217342 | yes |
| s900 | changed | `search berth --brief` | 1585 | 0.237955 | yes |
| s900 | changed | `search 'berth crane' --brief` | 1585 | 0.245269 | yes |
| s900 | changed | `search CODE-9 --brief` | 1585 | 0.239374 | yes |
| s900 | changed | `search berth` | 1585 | 0.245363 | yes |
| s900 | changed | `search berth tide --brief` | 1585, 1585 | 0.243664 | yes |
| s900 | changed | `search --phrase 'berth crane' --brief` | 1585 | 0.251743 | yes |
| s9000 | seen | `search berth --brief` | 6939 | 0.621122 | yes |
| s9000 | seen | `search 'berth crane' --brief` | 10861 | 0.710563 | yes |
| s9000 | seen | `search CODE-1549 --brief` | 57 | 0.344766 | yes |
| s9000 | seen | `search berth` | 6939 | 0.621881 | yes |
| s9000 | seen | `search berth tide --brief` | 6939, 6865 | 0.920836 | yes |
| s9000 | seen | `search --phrase 'berth crane' --brief` | 10861 | 0.779847 | yes |
| s9000 | changed (clear, cold) | `search berth --brief` | 15895 | 0.914786 | yes |
| s9000 | changed (clear, cold) | `search 'berth crane' --brief` | 15895 | 0.895056 | yes |
| s9000 | changed (clear, cold) | `search CODE-1549 --brief` | 15895 | 0.911274 | yes |
| s9000 | changed (clear, cold) | `search berth` | 15895 | 0.912964 | yes |
| s9000 | changed (clear, cold) | `search berth tide --brief` | 15895, 15895 | 1.142197 | yes |
| s9000 | changed (clear, cold) | `search --phrase 'berth crane' --brief` | 15895 | 1.020043 | yes |
| s90000 | seen | `search berth --brief` | 69208 | 5.186630 | yes |
| s90000 | seen | `search 'berth crane' --brief` | 108331 | 6.196066 | yes |
| s90000 | seen | `search CODE-53010 --brief` | 543 | 2.550652 | yes |
| s90000 | seen | `search berth` | 69208 | 5.158674 | yes |
| s90000 | seen | `search berth tide --brief` | 69208, 68183 | 8.350815 | yes |
| s90000 | seen | `search --phrase 'berth crane' --brief` | 108331 | 6.884549 | yes |
| s90000 | changed (clear, cold) | `search berth --brief` | 158550 | 10.090834 | yes |
| s90000 | changed (clear, cold) | `search 'berth crane' --brief` | 158550 | 10.087449 | yes |
| s90000 | changed (clear, cold) | `search CODE-53010 --brief` | 158550 | 10.018261 | yes |
| s90000 | changed (clear, cold) | `search berth` | 158550 | 10.115952 | yes |
| s90000 | changed (clear, cold) | `search berth tide --brief` | 158550, 158550 | 12.730879 | yes |
| s90000 | changed (clear, cold) | `search --phrase 'berth crane' --brief` | 158550 | 11.075319 | yes |

Raw samples and candidate counts are retained in `/var/tmp/lodge-bench/task10b/replay.json` and `/var/tmp/lodge-bench/t10b-replay.log`.

All 108 timed samples match the exact reader's stdout, stderr, and exit status.
All 54 seen samples have no epoch increase; all 18 ordinary changed samples at `s900` have none, while all 36 changed samples at `s9000` and `s90000` clear once.
These are restored-baseline samples; Task 12 owns the chained clear-rate measurement.
The interrupted preliminary replay is excluded from these results.

### Concerns and delivery

The provisional seen targets are missed at `s90000`: the 543-candidate code search takes 2.550652 s against 0.3 s, and the broad searches take 5.158674 to 8.350815 s against 1.0 s.
The current identity still follows the dispatched interim R11-A full-file rule, and Tasks 10c and 11 have not landed.
FTS raises a single complete working set above the production cap at both larger stores, so their changed samples clear and are classified as cold, outside the changed-read stop.
No cap, target, identity ruling, product decision, or earlier writer signature is changed to hide these costs.
The stop remains at Task 12 under d-26e6zj.

Unknown exact IDs, empty stored states, and candidates whose historical ID has no current row conservatively fall back to memory to preserve the completeness rule.
That can add work to those reads; the report's seeded, fault, and replay comparisons retain exact output.
No unresolved interface question or known correctness concern remains in this task.
Task 6 M1's kept-state path now gets its candidate word sets from FTS rather than rebuilding word sets over every record for every query; unkept searches keep the specified memory path.

No lodge repository record was opened directly, added, or edited, and no `lodge add` command was run.
The implementation and tests are unchanged after the final passing gate.
The task commit includes the amended Files list, the coordinator's ruling, this report, and the progress ledger, with explicit paths and the required Codex trailer.
The commit message is `Task 10b: index search candidates with immutable FTS units`, followed by `git push -u origin read-speed-build`.
