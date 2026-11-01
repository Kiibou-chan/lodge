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

## Task 10a: NEEDS_CONTEXT

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
