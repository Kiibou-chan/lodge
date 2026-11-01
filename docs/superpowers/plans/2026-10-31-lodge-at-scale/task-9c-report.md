# Task 9c: the parse lookup in one scan

Scope: Task 9c as amended by plan fix 7b, plus the dispatched removal of the unused `settings_key` named in Task 9's hand-offs.
Task 8c waits for the author's ruling and is untouched.
No record addition is required or performed.
The port and `find_parses` signature remain unchanged, so the interface skeleton step does not apply.

## Test-first work

The new tests exercise the existing correctness contract and require the scan through a connection wrapper that records SQL.
Before implementation, correctness assertions may already pass on the per-key reader; the scan assertions must fail in every new case.
Failing output, mutation evidence, measurements, and the final gate will be recorded below as they complete.

Command: `uv run --frozen pytest tests/gitstore/test_index_parses.py -k 'scan or one_bad' -q --tb=short`.
All 15 new cases failed before implementation; every failure was the missing scan, after the existing per-key correctness checks passed.
The original 999-key case also requested a scan; the Task 9c fix round removes that redundant second request.

```text
Command: uv run --frozen pytest tests/gitstore/test_index_parses.py -k 'scan or one_bad' -q --tb=short
15 failed: all scan assertions still saw per-key SELECT statements.
```

Command: `uv run --frozen pytest tests/gitstore/test_index_fixes.py::test_parse_only_module_has_no_settings_key -q --tb=short`.
The replacement for the obsolete settings-key test failed before the unused function was removed.

```text
F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_parse_only_module_has_no_settings_key __________________
tests/gitstore/test_index_fixes.py:57: in test_parse_only_module_has_no_settings_key
    assert not hasattr(index_db, "settings_key")
E   AssertionError: assert not True
E    +  where True = hasattr(index_db, 'settings_key')
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_fixes.py::test_parse_only_module_has_no_settings_key
1 failed in 0.51s
```

## Implementation

`find_parses` uses one `ORDER BY rowid` scan from 1,000 requested keys, filtering by the complete path and blob pair before decoding.
Both branches use the same per-value decoder, validators, and parse-type admission check.
A bad value misses only its key, and a decoded `None` remains a hit.
`IndexDB.parses` retains its existing explicit read transaction.
The unused `settings_key` and its `CoreSettings` import are removed from `index_db.py`, as dispatched.
Existing test edits are limited to replacing the obsolete settings-key test with the absence regression and allowing the parse-only opening guard to install a forbidden settings-key sentinel on the module after removal.

## Focused verification and mutants

Command: `uv run --frozen pytest tests/gitstore/test_index_parses.py tests/gitstore/test_index_fixes.py tests/app/test_parse_cache.py tests/test_structure.py -q`.
Result: `90 passed in 1.33s`.
Both clear interleavings pass: a snapshot pinned by a `SELECT` sees the old units, whereas a clear before the first `SELECT` produces misses; a subsequent transaction sees the clear and epoch 2.
The existing app parse-cache tests cover reconstruction from misses.

Command: `uv run --frozen python /var/tmp/lodge-bench/task-9c-mutants.py`.
Each of the four required mutants ran once in a fresh subprocess with an in-memory replacement for `find_parses`; repository source files were never replaced.
All four exited 1 on correctness assertions, before the SQL-count assertions.

```text
joined-values exit 1
FFF......                                                                [100%]
=================================== FAILURES ===================================
__________________ test_one_bad_value_is_one_miss[truncated] ___________________
tests/gitstore/test_index_parses.py:177: in test_one_bad_value_is_one_miss
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {} == {('lodge/spec...ne=None), ...}
E     
E     Right contains 1479 more items:
E     {('lodge/spec/berths/s-000000.md', 'current'): None}
E     {('lodge/spec/berths/s-000001.md', 'current'): Area(name='berths', title='Berths', intro='Berths.', order=(), rank=None)}
E     {('lodge/spec/berths/s-000002.md', 'current'): Problem(path='2', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000003.md', 'current'): Problem(path='3', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000004.md', 'current'): Problem(path='4', check=1, message='broken', line=None)}...
E     
E     ...Full output truncated, use '-vv' to show
_________________ test_one_bad_value_is_one_miss[joined-nulls] _________________
tests/gitstore/test_index_parses.py:177: in test_one_bad_value_is_one_miss
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {} == {('lodge/spec...ne=None), ...}
E     
E     Right contains 1479 more items:
E     {('lodge/spec/berths/s-000000.md', 'current'): None}
E     {('lodge/spec/berths/s-000001.md', 'current'): Area(name='berths', title='Berths', intro='Berths.', order=(), rank=None)}
E     {('lodge/spec/berths/s-000002.md', 'current'): Problem(path='2', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000003.md', 'current'): Problem(path='3', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000004.md', 'current'): Problem(path='4', check=1, message='broken', line=None)}...
E     
E     ...Full output truncated, use '-vv' to show
_______________ test_one_bad_value_is_one_miss[joined-adjacent] ________________
tests/gitstore/test_index_parses.py:177: in test_one_bad_value_is_one_miss
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {('lodge/spec...ne=None), ...} == {('lodge/spec...ne=None), ...}
E     
E     Omitting 1478 identical items, use -vv to show
E     Left contains 1 more item:
E     {('lodge/spec/berths/s-000010.md', 'current'): None}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_parses.py::test_one_bad_value_is_one_miss[truncated]
FAILED tests/gitstore/test_index_parses.py::test_one_bad_value_is_one_miss[joined-nulls]
FAILED tests/gitstore/test_index_parses.py::test_one_bad_value_is_one_miss[joined-adjacent]
3 failed, 6 passed in 0.40s

path-only exit 1
F                                                                        [100%]
=================================== FAILURES ===================================
___________________________ test_scan_equals_per_key ___________________________
tests/gitstore/test_index_parses.py:145: in test_scan_equals_per_key
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {('lodge/spec...'): None, ...} == {('lodge/spec...ne=None), ...}
E     
E     Omitting 981 identical items, use -vv to show
E     Differing items:
E     {('lodge/spec/berths/s-000288.md', 'current'): None} != {('lodge/spec/berths/s-000288.md', 'current'): Problem(path='288', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000092.md', 'current'): None} != {('lodge/spec/berths/s-000092.md', 'current'): Problem(path='92', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000158.md', 'current'): None} != {('lodge/spec/berths/s-000158.md', 'current'): Problem(path='158', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000416.md'...
E     
E     ...Full output truncated, use '-vv' to show
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_parses.py::test_scan_equals_per_key - Assert...
1 failed in 0.14s

end-on-exception exit 1
F                                                                        [100%]
=================================== FAILURES ===================================
__________________ test_one_bad_value_is_one_miss[truncated] ___________________
tests/gitstore/test_index_parses.py:177: in test_one_bad_value_is_one_miss
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {('lodge/spec...ne=None), ...} == {('lodge/spec...ne=None), ...}
E     
E     Omitting 10 identical items, use -vv to show
E     Right contains 1469 more items:
E     {('lodge/spec/berths/s-000011.md', 'current'): Problem(path='11', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000012.md', 'current'): Problem(path='12', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000013.md', 'current'): Problem(path='13', check=1, message='broken', line=None)}
E     {('lodge/spec/berths/s-000014.md', 'current'): Problem(path='14', check=1, message='broken', line=None)}...
E     
E     ...Full output truncated, use '-vv' to show
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_parses.py::test_one_bad_value_is_one_miss[truncated]
1 failed in 0.14s

no-scan-admission exit 1
F                                                                        [100%]
=================================== FAILURES ===================================
___________________ test_one_bad_value_is_one_miss[integer] ____________________
tests/gitstore/test_index_parses.py:177: in test_one_bad_value_is_one_miss
    assert scan_index.parses(keys) == expected
E   AssertionError: assert {('lodge/spec...ne=None), ...} == {('lodge/spec...ne=None), ...}
E     
E     Omitting 1479 identical items, use -vv to show
E     Left contains 1 more item:
E     {('lodge/spec/berths/s-000010.md', 'current'): 123}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/gitstore/test_index_parses.py::test_one_bad_value_is_one_miss[integer]
1 failed in 0.14s

```

## Whole-state lookup timings

Store: the existing synthetic `s90000` from `scripts/bench_store.py`, under `/var/tmp/lodge-bench/s90000`, with 160,800 keys from its committed listing.
The source store was used read-only; its populated parse index `index-8ebed69bd14ce4cc.sqlite` was copied through SQLite backup to `/var/tmp/lodge-bench/task-9c/lookup.sqlite`.
No record files were opened directly or written.
The initial table held exactly 160,800 parse units and used 145,293,312 bytes.
Commands, from this worktree:

```sh
uv run --frozen python -m compileall -q src .venv/lib
uv run --frozen python /var/tmp/lodge-bench/task-9c-bench.py
```

The benchmark uses the worktree's native-disk Python and dependencies for both implementations, with bytecode compiled, the cyclic collector disabled as in the CLI, and one explicit read transaction per lookup.
The per-key implementation is loaded in memory from `3e992c0:src/lodge/gitstore/index_parses.py`, the dispatch's starting commit; the scan uses the changed worktree module, with the same codec and validators.
Each timed interval covers the whole `find_parses` call, including its SQL, filtering, decoding, admission, and transaction boundaries.
Result comparison and result disposal are outside the timer.
Every run returns 160,800 hits, and the complete result mappings are equal between implementations.

For the cap run, older blob keys of the same synthetic units are inserted into the scratch table, retaining their valid encoded values.
Insertion uses savepoints and stops before the next unit would cross the used-page cap.
There are 117,377 older units, 278,177 rows in total, and 241,197,056 used bytes, just 2,944 bytes below the 241,200,000-byte cap, within one 4,096-byte page.
The reference store and its index are unchanged.

| Table | Per-key, best of three | Scan, best of three | Plan's per-key reference |
|---|---:|---:|---:|
| One working set | 1.421789 s | 1.067315 s | 1.435 s |
| Older units fill the table to the cap | 1.454742 s | 1.177357 s | 1.435 s |

Full timing output:

```text
Python 3.13.5 SQLite 3.47.1 keys 160800 cap 241200000
source index-8ebed69bd14ce4cc.sqlite used 145293312 rows 160800
per-key 1 1.470160 hits 160800
per-key 2 1.423054 hits 160800
per-key 3 1.421789 hits 160800
per-key best 1.421789
scan 1 1.075842 hits 160800
scan 2 1.077338 hits 160800
scan 3 1.067315 hits 160800
scan best 1.067315
normal equality: yes
at-cap used 241197056 cap gap 2944 older rows 117377 total rows 278177
at-cap-per-key 1 1.458819 hits 160800
at-cap-per-key 2 1.471411 hits 160800
at-cap-per-key 3 1.454742 hits 160800
at-cap-per-key best 1.454742
at-cap-scan 1 1.187253 hits 160800
at-cap-scan 2 1.199388 hits 160800
at-cap-scan 3 1.177357 hits 160800
at-cap-scan best 1.177357
at-cap equality: yes
```

## Concerns and hand-offs

The scan visits every row, so older units raise its cost even when their blobs are not requested; the at-cap measurement above includes that cost.
The cap policy itself is unchanged; parse-only cap enforcement remains Task 10a Step 3a, as the ledger specifies.
Removal of the unused settings digest is limited to the parse-only module; Task 10a must implement a settings digest for stored-state keys when that consumer exists.
This task does not claim to meet the changed-read target; the full-build cost and stop remain for the later tasks under the amended plan.
No unclear step or NEEDS_CONTEXT arose.

## Whole gate and delivery

`uv run --frozen ruff check`, `uv run --frozen mypy`, and `uv run --frozen vulture` passed before the whole gate.
The required `UV_FROZEN=1 sh scripts/check.sh` exited 0 before the task commit.
Ruff format, Ruff, strict mypy, Vulture, pytest, and `lodge check --gate` all passed.

```text
634 files already formatted
All checks passed!
Success: no issues found in 250 source files
1932 passed, 2 skipped in 82.54s (0:01:22)
ok
note: area storage: order changed
```

The storage-order note already appeared in Task 9's successful gates.
Full output is in `/var/tmp/lodge-bench/task-9c-check.log`.
`git diff --check` passed, and the added code, tests, and report passed a scan for personal paths and em dash characters.
Delivery is one commit, `Task 9c: scan large parse lookups once`, with explicit paths and the dispatched Codex trailer, followed by `git push -u origin read-speed-build`.
Task 9c is complete, with no blocking concern; the later-task hand-offs above remain unchanged.
