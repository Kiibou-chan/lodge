# Task 10a and prerequisite Task 9c fix round

Scope: every Minor in `task-9c-review.md`, followed by Task 10a as amended by plan fixes 6b and 7b.
SECOND-1 is recorded as d-n65rhr, and CONV-1 as d-egknpk.
Task 8c's interim R11 rule is retained.
No records are opened directly, added, or edited.

## Task 9c fix round

The review is copied verbatim to `task-9c-review.md`.
M1 adds cross-paired blob coverage and checks that only requested rows are decoded.
M2 will weigh the table size before choosing a scan, with a 1,000-key full-table comparison before and after.
M3 adds a cursor failure after successful hits and preserves those hits.
M4 corrects the stored-state settings digest hand-off in the plan and ledger.
M5 removes the redundant threshold request and ineffective monkeypatch, and condenses the original red output.

The scan now requires both at least 1,000 keys and at least one requested key for every four rowids.
`max(rowid)` is one b-tree probe, and conservatively favours per-key reads when rowids have gaps.
A scan catches cursor SQL errors after preserving already decoded hits.
The fixture uses distinct blob names, an unrequested cross-pair, and a requested pair whose blob is absent for that path.
Only requested rows are decoded.
Existing tests edited: the scan fixture, SQL-count assertions (the new size probe), and the redundant second request in `test_scan_reads_once`; the ineffective settings monkeypatch and its import are removed.
The original Task 9c report retains the red command and count while condensing the repeated tracebacks.

Test-first commands and failing output:

```text
uv run --frozen pytest tests/gitstore/test_index_fixes.py::test_scan_keeps_hits_before_sql_error tests/gitstore/test_index_parses.py::test_small_fraction_of_a_large_table_uses_per_key -q --tb=short
FAILED test_scan_keeps_hits_before_sql_error
E   AssertionError: assert {} == {('unit-0', 'blob'): None, ...}
E   Right contains 700 more items
FAILED test_small_fraction_of_a_large_table_uses_per_key
E   AssertionError: assert 1 == 1001
2 failed in 0.22s
```

M1 already holds in the production implementation, so its new regression was run against the review's path-and-blob-tested-separately mutant before any implementation change.
The source was restored immediately afterwards.

```text
uv run --frozen pytest tests/gitstore/test_index_parses.py::test_scan_requires_the_requested_pair -q --tb=short
FAILED test_scan_requires_the_requested_pair
E   Left contains 1 more item:
E   {('lodge/spec/berths/s-000002.md', 'blob-3'): None}
1 failed in 0.32s
```

M2 timing command: `uv run --frozen python /var/tmp/lodge-bench/task-9c-fix-bench.py`.
Same native-disk Python and copied synthetic `s90000` parse table as Task 9c, 278,177 rows, 241,197,056 used bytes, at the 241,200,000-byte cap.
The request is 1,000 keys, with 1,000 hits in every run, and each timed read includes its explicit transaction.
Best of three: before 0.229595 s (samples 0.235350, 0.231602, 0.229595); after 0.004688 s (0.005605, 0.005038, 0.004688).
No timing assertion is added to pytest.

After explicit bytecode compilation (`uv run --frozen python -m compileall -q src .venv/lib`), the same after measurement gave 0.005364 s best of three (0.005772, 0.005735, 0.005364).
The focused command `uv run --frozen pytest tests/gitstore/test_index_parses.py tests/gitstore/test_index_fixes.py -q` passed all 31 tests.

## Task 9c fix-round gate and delivery

`UV_FROZEN=1 sh scripts/check.sh` exited 0 before the fix-round commit.
Ruff format, Ruff, strict mypy, Vulture, pytest, and `lodge check --gate` all passed.

```text
642 files already formatted
All checks passed!
Success: no issues found in 257 source files
1981 passed, 6 skipped in 88.64s (0:01:28)
ok
note: area storage: order changed
```

The storage-order note predates this fix round.
The full gate output is retained under `/var/tmp/lodge-bench/task-9c-fix-check-final.log`.
`git diff --check` passed.
Delivery is the separate commit `Task 9c fix round: address all five review minors`, with explicit paths and the dispatched Codex trailer, followed by `git push -u origin read-speed-build`.
The fix round has no outstanding review finding.

## Task 10a: historical NEEDS_CONTEXT, resolved below

No Task 10a skeleton, new test, implementation, or replay has been started.
The current plan, progress ledger, Global Constraints, Review Focus, Task 9, Task 9c, Task 10a, and the named decisions have been read through the required interfaces.
The following interface question stops Task 10a under the dispatch's unclear-step rule.

Step 3a requires the file count to be supplied by the tree's caller, rather than inferred from the misses.
The specified `Index.keep_parses(parsed)` and `Index.keep_state(state, rows, answers, citing, facts, parses, misses, epoch)` signatures have no file-count argument.
Task 10b explicitly preserves both signatures and spells out `keep_parses(parsed)` again.
Neither the number of misses, the number of record rows, nor the union of current and published parses gives the caller's tree file count.

Question: may Task 10a add a keyword-only `files` parameter to these writer methods (and carry it into the marker writer), updating the plan's interface and Task 10b hand-off text accordingly, or which alternative interface should carry the caller's count while preserving the specified signatures?
This is a question about the required port, before the interface skeleton, rather than a request to change the cap policy.
SECOND-1, the cap condition, and Task 8c's interim identity rule are settled inputs and require no new decision here.
No `lodge add` command has been run.
Task 10a's tests, complete gate, replay timings, keep breakdown, cap occupancy, and ten-cycle clear count remain outstanding.

## Task 10a resumed: coordinator ruling

The coordinator answered the interface question yes in the build dispatch.
`Index.keep_parses`, `Index.keep_state`, and the marker writer each require keyword-only `files: int`, without a default, supplied by every caller from its tree's file count.
The plan's interface lines and Task 10b hand-off are amended with the code.
The previous NEEDS_CONTEXT status is resolved.
The skeleton adds the value types, port methods, concrete adapter and fake stubs, read-model builders, indexed read entry points, and the deferred-output hook.
Existing parse-writer test calls gain the required keyword; their synthetic fixtures supply the test's tree size.

## Skeleton and first red run

Before writing tests, `uv run --frozen pytest tests/test_structure.py -q` passed 39 tests, and `uv run --frozen mypy` passed all 260 source files.
The initial new test run used the six Task 10a suites plus the small `test_indexed_keep.py` split to keep modules below 300 lines.
It failed all 66 collected cases against the skeleton before implementation.
The process-death and real-pipe cases are in `test_index_keep_processes.py`, also run red before implementation.

```text
uv run --frozen pytest tests/app/test_read_model.py tests/app/test_indexed_reads.py tests/app/test_indexed_keep.py tests/gitstore/test_index_states.py tests/gitstore/test_index_concurrency.py tests/e2e/test_indexed_reads.py -q --tb=short
E   NotImplementedError
66 failed in 1.20s
```

The complete failures are retained outside the repository in `task-10a-red.log` and `task-10a-red-processes.log` under the native benchmark folder.
Two test-fixture collection errors (an escaped newline and an author message missing its synthetic source) were fixed before this collected red run.
Implementation and timings remain outstanding at this point.

## Implementation and first complete gate

Stored states now serve `show`, `waiting`, `threads`, and `thread` under one explicit read transaction.
Missing, malformed, or incomplete cached data discards the partial answer and rebuilds through the pinned listings and parse cache.
The settings digest uses `sha1(repr(settings).encode()).hexdigest()`.
Validity bounds compare offset-aware datetimes in both clock directions.
Freshness is read live, while cached `Read.statuses` is empty and viewer-only fields retain their defaults.
The viewer factory explicitly disables the read model.

First sightings write one bounded marker transaction and their missed parses, without building read-model rows, answers, or citers.
Second sightings return a closure over the checked state, listings, parses, clock reading, epoch, and key.
The CLI writes and explicitly flushes its whole output before calling that closure, including multi-ref commands returning a nonzero status.
All model construction, encoding, and storage is inside an ordinary-exception boundary.
Failed writes, flushes, and real broken pipes never call the keep, and release never calls it.

The adapter keeps 1,024 compact-JSON buckets, all answers and code/root citer rows, and immutable parses and facts.
`KEPT_STATES = 4` controls replacement and FIFO eviction, which removes only the state's own rows.
A changed epoch restores every parse unit the build used.
Every writer takes the caller's required `files` count and checks used pages before inserting.
`meta.written` counts actual parse/fact inserts, and a clear resets it and `meta.kept`, and raises the epoch.
Only a complete state sets `meta.kept`.

Small internal helpers split indexed lookups, schema creation, and shared explicit transactions, keeping every module below 300 lines without changing package edges.
The in-memory index fake moves to `fake_index.py`, re-exported by `fakes.py`, to keep the state fixture focused and leave room for Task 10b.
The port retains `typing.ContextManager` with a targeted Ruff deprecation suppression because the existing pure-app import rule excludes `contextlib`; no structure rule is changed.
Existing tests edited so far are the four parse-writer suites (`test_index_db.py`, `test_index_failures.py`, `test_index_fixes.py`, and `test_index_parses.py`) and `fakes.py`, for the required writer keyword.

The extra SQLite CLI-contract suite checks the real marker transaction, every constructor and SQL keep after flush, missing and undecodable data in each state table, bucket/facts encoding failures with both exit statuses and with/without eviction, and the tree count passed to parse-only writers.
Its 21 cases were also run against an isolated copy with the interface skeleton restored, then against the implementation.

```text
uv run --frozen pytest tests/gitstore/test_indexed_cli_contract.py -q --tb=short
E   NotImplementedError: interface skeleton
21 failed in 0.59s

Implementation: 21 passed in 0.49s
```

The storage/concurrency/process suites passed 24 tests in 48.89 s, including failure at each SQL statement with and without eviction, a real process clear, SIGKILL within a write, and SIGPIPE with both dispositions.
An intermediate sweep ran while source files were changing, changing the source-derived database filename during its fixture setup; the final uninterrupted sweep above passed.
The app/read-model/end-to-end suites passed 46 tests in 5.94 s.

`UV_FROZEN=1 sh scripts/check.sh` exited 0 on the first complete implementation gate, before the supplemental suite joined the final gate.

```text
All checks passed!
Success: no issues found in 273 source files
2051 passed, 6 skipped in 144.77s (0:02:24)
ok
note: area storage: order changed
```

The storage-order note predates this task.
The gate output is retained outside the repository as `task-10a-check-1.log`.
Benchmark replay and complete-keep measurements are now running in isolated native-disk synthetic clones, with one synthetic question added through `ask` so `thread` can be measured as well.
No `lodge add` command has been run.

The final SQL fault sweep now runs the actual second-sighting CLI command at every injected statement, for both successful and multi-ref nonzero commands, with and without an eviction.
Each case checks byte-for-byte output and exit status, absence of the failed state, and completeness of every prior state.
Together with the git-status refresh regression, it passed nine cases in 45.77 s.
These extended cases also failed against the isolated interface skeleton (nine failed in 0.36 s).
The process-kill fixture now stops after all 1,024 buckets were inserted, and the validity test explicitly observes rebuilding in both clock directions.
Those focused checks passed five cases in 0.27 s.

The initial replay setup left each clone's remote-tracking `main` before its added synthetic question, so clean reads unnecessarily compared two different published listings.
Those timings are discarded.
The final replay updates the synthetic clone's remote-tracking ref to its committed baseline, then starts from a fresh index for each mode.
Only the benchmark clones are changed.

## Final output barrier regression

A further test exposed a buffered error-stream flush that the command had not explicitly attempted before keeping a multi-ref result.
The command now flushes stderr as well as stdout before invoking the deferred keep.
This keeps the nonzero result's entire output inside the success boundary.
The new test was run red before that code change.

```text
uv run --frozen pytest tests/app/test_indexed_keep.py::test_failed_error_stream_flush_keeps_nothing -q --tb=short
E   Failed: DID NOT RAISE OSError
1 failed in 0.20s
```

After the fix, the keep and real SQLite CLI-contract suites passed 37 tests in 0.60 s.
The final full gate and the replay use this final source digest; earlier timing samples are discarded.

## Final gate

`UV_FROZEN=1 sh scripts/check.sh` exited 0 after the final output-barrier change and all supplemental tests.
Ruff format, Ruff, strict mypy, Vulture, pytest, and `lodge check --gate` all passed.

```text
Success: no issues found in 274 source files
2076 passed, 6 skipped in 138.87s (0:02:18)
ok
note: area storage: order changed
```

The complete output is retained outside the repository as `task-10a-check-final.log`.
`git diff --check` is clean.

## Final measurement protocol

Commands: `uv run --frozen python /var/tmp/lodge-bench/task-10a-replay.py`, followed by `uv run --frozen python /var/tmp/lodge-bench/task-10a-phases.py`.
The scripts and raw JSON/logs are retained under the native benchmark folder.
The stores are isolated clones of `scripts/bench_store.py`'s `s900`, `s9000`, and `s90000`, with one synthetic question written through `ask`, committed locally, and included in the published baseline.
All stores and scratch artefacts stay below the native benchmark folder.
Python 3.13.5 and SQLite 3.47.1 are the same as the preceding build measurements, with a native-disk virtual environment and explicit bytecode compilation before timing.
The filesystem reports `ext2/ext3` through `stat -f`.
Git uses an empty global configuration, no system configuration or attributes, and a synthetic home directory; no conversion source is configured.
The production interim R11 rule is retained, including its reads and hashes of every working-tree file.
No R11 alternative is used for these timings.

Every replay row is the best of three separate processes on the same input state, timed through process exit.
Every sample's stdout, stderr, and exit status is compared with an exact `LODGE_INDEX=off` run of that state.
Cold samples start with no index; seen samples start with a complete baseline state; changed samples restore that complete baseline index and make the same one-record edit before each sample.
The phase script separately times the first, second, and third CLI exits without instrumentation, then repeats the same states with disjoint instrumentation of the complete keep and read phases.
Its ten consecutive three-read cycles retain the evolving index rather than restore it between edits.
All timings are provisional under d-26e6zj, with Task 10c's published-facts optimisation and Task 11 still ahead.

## Recorded timings

Replay and independent timing summaries are in seconds and use the best of three.
Each disjoint phase column is taken whole from the instrumented run with that column's shortest exit time.
The ten-cycle trace gives single observations from one uninterrupted sequence.

The 72 replay rows, comprising 216 indexed CLI samples, all matched the exact reader in stdout, stderr, and exit status.

The `changed` replay column is the first sighting of the edited state.

| Store | Command | Cold | Seen | Changed, first |
|---|---|---:|---:|---:|
| s900 | `show {code}` | 0.341411 | 0.185072 | 0.233481 |
| s900 | `show {entry} --reasoning --provenance` | 0.348445 | 0.188222 | 0.233135 |
| s900 | `show {decision}` | 0.341793 | 0.186759 | 0.231512 |
| s900 | `waiting` | 0.343941 | 0.184563 | 0.230625 |
| s900 | `threads` | 0.339993 | 0.185265 | 0.234258 |
| s900 | `show {code} {code2} {entry}` | 0.344246 | 0.184711 | 0.236453 |
| s900 | `show A` | 0.362804 | 0.185562 | 0.252448 |
| s900 | `thread {question}` | 0.347896 | 0.186610 | 0.230765 |
| s9000 | `show {code}` | 1.484143 | 0.357046 | 0.711161 |
| s9000 | `show {entry} --reasoning --provenance` | 1.489732 | 0.360399 | 0.705981 |
| s9000 | `show {decision}` | 1.477085 | 0.361095 | 0.708259 |
| s9000 | `waiting` | 1.485661 | 0.363312 | 0.703950 |
| s9000 | `threads` | 1.482802 | 0.362127 | 0.700449 |
| s9000 | `show {code} {code2} {entry}` | 1.510101 | 0.356812 | 0.713935 |
| s9000 | `show A` | 1.691016 | 0.366733 | 0.917174 |
| s9000 | `thread {question}` | 1.475422 | 0.360620 | 0.693259 |
| s90000 | `show {code}` | 14.295971 | 2.216047 | 7.707148 |
| s90000 | `show {entry} --reasoning --provenance` | 14.395820 | 2.196486 | 7.588622 |
| s90000 | `show {decision}` | 14.361623 | 2.194567 | 7.631193 |
| s90000 | `waiting` | 14.187788 | 2.203374 | 7.633749 |
| s90000 | `threads` | 14.193021 | 2.204410 | 7.636488 |
| s90000 | `show {code} {code2} {entry}` | 14.440450 | 2.209489 | 7.800811 |
| s90000 | `show A` | 16.363489 | 2.223957 | 9.622197 |
| s90000 | `thread {question}` | 14.288710 | 2.196022 | 7.587599 |

### First, second, and third exits at s90000

Command: `show A`, with the complete baseline index restored and the same one-record edit applied for each repeat.

These are uninstrumented CLI processes, including release and interpreter exit.

| Read | Best exit | All three samples |
|---|---:|---|
| first | 9.756700 | 9.803234, 9.761343, 9.756700 |
| second | 15.187024 | 15.187024, 15.224029, 15.442878 |
| third | 2.220500 | 2.413978, 2.220500, 2.222580 |

The following instrumented runs repeat those inputs with the real stdout pipe and explicit flushes.

Nested measurements are subtracted from their callers, so each column sums to its instrumented process exit.

The first row includes Python start-up, import time, release, interpreter shutdown, and any unassigned overhead; it is not presented as a pure import benchmark.

| Phase | First | Second | Third |
|---|---:|---:|---:|
| Start-up, release, and unassigned overhead | 0.205020 | 0.332200 | 0.168858 |
| Composition | 0.005897 | 0.008167 | 0.005386 |
| Build digest | 0.003755 | 0.004803 | 0.003025 |
| Identity, including interim R11 | 1.996510 | 2.009351 | 2.005381 |
| Listings | 0.000003 | 0.000003 | 0.000000 |
| Parse lookup and decode | 1.083966 | 1.087837 | 0.000426 |
| Texts for misses | 0.000032 | 0.000000 | 0.000000 |
| Parse misses and snapshot glue | 0.403452 | 0.399966 | 0.000000 |
| Assemble | 0.207561 | 0.206703 | 0.000000 |
| Derive | 1.892682 | 1.921211 | 0.000000 |
| State check | 0.900035 | 0.887849 | 0.000000 |
| Change facts | 0.000009 | 0.000009 | 0.000000 |
| Change check | 0.771021 | 0.783494 | 0.000000 |
| Read dispatch and stored lookups | 2.157688 | 2.151535 | 0.047147 |
| Answer and output | 0.018622 | 0.000067 | 0.000050 |
| Rows as Row | 0.000000 | 1.050997 | 0.000000 |
| Buckets, including JSON | 0.000000 | 1.537816 | 0.000000 |
| Answers | 0.000000 | 0.025762 | 0.000000 |
| Citers, including roots and family exclusion | 0.000000 | 2.368097 | 0.000000 |
| Facts construction | 0.000000 | 0.000015 | 0.000000 |
| State metadata | 0.000000 | 0.027858 | 0.000000 |
| Parse encoding and inserts | 0.000084 | 0.000017 | 0.000000 |
| Facts encoding and inserts | 0.000003 | 0.167362 | 0.000000 |
| Marker transaction, remaining work | 0.015152 | 0.000000 | 0.000000 |
| Cap check | 0.000056 | 0.000057 | 0.000000 |
| Replacement of the same key | 0.000000 | 0.000062 | 0.000000 |
| FIFO eviction | 0.000000 | 0.000000 | 0.000000 |
| Clear | 0.000000 | 0.000000 | 0.000000 |
| Keep transaction, remaining work | 0.000000 | 0.348714 | 0.000000 |
| Total instrumented exit | 9.661546 | 15.319952 | 2.230273 |

### State size, cap, clears, and eviction

The caller's tree contains 160,801 files, including the synthetic question.

The production cap is 241,201,500 bytes (230.028 MiB).

The newly kept state's own JSON values total 51,775,235 bytes (49.377 MiB), excluding shared parses, shared facts, SQLite keys, b-trees, and page overhead.

| State table | Newest state's value bytes |
|---|---:|
| states | 1,211,353 |
| buckets | 50,440,572 |
| answers | 1,065 |
| citers | 122,245 |

The representative second read has 2 complete states and 263,159,808 used bytes across the whole index.

Only one complete state fits below the production cap in the measured sequence; the largest observed kept count is 2, including the permitted working set above the cap.

The ten consecutive edit/read/read/read cycles produced 5 clears.

Reads that perform a clear are classified as cold, with any subsequent rebuilding cost shown, and are not put under the changed-read stop.

| Cycle | Read | Exit | Clear alone | Used bytes after | Kept states | Epoch |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 9.669147 | 0.078563 | 65,536 | 0 | 2 |
| 4 | 1 | 9.759161 | 0.080495 | 65,536 | 0 | 3 |
| 6 | 1 | 9.750518 | 0.086246 | 65,536 | 0 | 4 |
| 8 | 1 | 9.784892 | 0.081074 | 65,536 | 0 | 5 |
| 10 | 1 | 9.753837 | 0.082280 | 65,536 | 0 | 6 |

The complete ten-cycle occupancy trace is below; each cell lists first, second, and third read values.

| Cycle | Exit seconds | Used bytes | Kept states | Epochs |
|---|---|---|---|---|
| 1 | 9.691944, 15.253966, 2.218382 | 203,591,680 / 263,159,808 / 263,159,808 | 1, 2, 2 | 1, 1, 1 |
| 2 | 9.669147, 24.844778, 2.242652 | 65,536 / 206,942,208 / 206,942,208 | 0, 1, 1 | 2, 2, 2 |
| 3 | 9.816679, 15.311533, 2.224333 | 206,942,208 / 266,506,240 / 266,506,240 | 1, 2, 2 | 2, 2, 2 |
| 4 | 9.759161, 24.363983, 2.231663 | 65,536 / 206,942,208 / 206,942,208 | 0, 1, 1 | 3, 3, 3 |
| 5 | 9.728249, 15.180597, 2.227254 | 206,942,208 / 266,526,720 / 266,526,720 | 1, 2, 2 | 3, 3, 3 |
| 6 | 9.750518, 24.598002, 2.251099 | 65,536 / 206,942,208 / 206,942,208 | 0, 1, 1 | 4, 4, 4 |
| 7 | 9.740728, 15.251094, 2.225265 | 206,942,208 / 266,506,240 / 266,506,240 | 1, 2, 2 | 4, 4, 4 |
| 8 | 9.784892, 24.581818, 2.215607 | 65,536 / 206,942,208 / 206,942,208 | 0, 1, 1 | 5, 5, 5 |
| 9 | 9.636624, 15.290360, 2.230018 | 206,942,208 / 266,526,720 / 266,526,720 | 1, 2, 2 | 5, 5, 5 |
| 10 | 9.753837, 24.800290, 2.234580 | 65,536 / 206,942,208 / 206,942,208 | 0, 1, 1 | 6, 6, 6 |

A separate writer diagnostic copies the final synthetic index and raises only that copy's cap to 10,000 bytes per file, so four complete states remain long enough to measure a fifth keep's FIFO eviction.

This diagnostic changes neither the production constant nor the target timing configuration.

Best of three complete `keep_state` calls: 1.761903 s; FIFO eviction alone: 0.033758 s.

All samples, as total/eviction: 1.761903/0.057368, 1.790040/0.033758, 1.778053/0.049577.

## Concerns and delivery

The measurements miss the eventual seen and changed targets at s90000.

They retain the current interim R11 identity port, which reads and hashes every working-tree file, and full published-state derivation and checking until Task 10c.

The complete second-sighting keep, cap occupancy, and cold clears above are the implementation's measurements, rather than plan fix 7b's partial 8.764 s proxy.

The stop remains with Task 12 under d-26e6zj; this task changes no target or ruling.

No unresolved interface question or known correctness concern remains in this task.

No lodge repository record was opened directly, added, or edited, and no `lodge add` command was run.

The commit includes the required file-count interfaces, the corresponding Task 10b hand-off, the tests, the implementation, this report, and the Task 10a ledger entry.
