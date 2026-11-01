# Review of e4fd032 (Task 9c: one ordered scan of large parse lookups; `settings_key` removed)

Counts: 0 Blocking, 0 Important, 5 Minor.
Verdict: the scan is correct.
Every returned parse belongs to its key, B1 and B3 hold, the results equal the per-key lookup on every shape I tried, and all four named mutants are caught.
The remaining findings are one test gap, one cost caveat the plan already accepts, and three small items.

## Method

Own detached worktree at e4fd032 (`/var/tmp/lodge-review-t9c/wt`, removed at the end); nothing run in `/var/tmp/lodge-build`.
Scratch copies of `/var/tmp/lodge-bench/s900` and `s9000` with their own `.git/lodge` index (populated by `lodge check` of this build); `/var/tmp/lodge-bench` itself only read, and its s90000 index copied by SQLite backup.
The shared index under the repository's `.git/lodge` was never opened.
Baseline for "per-key" is `3e992c0:src/lodge/gitstore/index_parses.py`, loaded in memory.

## Correctness pass (F1, B1, B3)

Verified by running:

- Real stores: `diff_real.py` on s900 (1,607 keys) and s9000 (16,120 keys): the full listing and five random subsets (1,000 to 2,340 keys each, with 50 absent keys, 30 duplicated keys, and 60 keys pairing a real path with another path's blob) give a dictionary equal to the per-key lookup, with the same types.
- Fuzz on a synthetic table (`fuzz.py`, 2,682 rows over 400 paths, five blobs per path interleaved, 20 per cent of rows corrupt with truncated, `null,null`, `123`, `"text"`, `{}`, `[""]`, empty values): 200 requests of 999 to 3,000 keys with duplicates, absent keys and cross-paired keys all equal to the per-key lookup, and each hit's own `path` field equals its key (association checked by content, not only by equality with the baseline).
- F1 by construction: `found[(path, blob)]` is keyed from the row that was decoded (`src/lodge/gitstore/index_parses.py:34-40`), so no value can move to another key; `null,null` and the adjacent-fragment pair are each one miss.
- B1: `_parse_value` (`index_parses.py:23-27`) holds the admission check and both branches call it; `123`, `"text"`, `{}`, `[""]`, and a `Level1` are misses (tests pass, and the `no-scan-admission` mutant fails `[integer]`).
- B3: `IndexDB.parses` (`index_db.py:136-141`) keeps `transaction(self.db)` around `find_parses`; the scan is one statement, so it reads one snapshot by SQLite's own rule, and the test's `interleaved` asserts `db.in_transaction`.
  Both interleavings pass: a pinned snapshot returns the pre-clear units, a clear before the first read returns misses.
- A clear between the scan and the use cannot touch the result: `find_parses` returns decoded in-memory objects, and `snapshot_of` (`app/state.py:64-79`) only keeps misses afterwards.
- Query plan is `SCAN parses` with no sort (`EXPLAIN QUERY PLAN`), so `ORDER BY rowid` costs nothing.
- `UNIQUE(path,blob)` (`index_db.py:88-90`) makes duplicate rows impossible, so "later row overwrites an earlier hit" cannot arise.

Mutants: the builder's four, rerun in my worktree by a copy of its script writing to my own folder: joined-values (3 tests fail), path-only (1), end-on-exception (1), no-scan-admission (1); each fails on the result assertion, before the SQL-count assertion, as the report says.
Five more of mine (`mut2.py`): blob-only, threshold `>`, no `ORDER BY`, `None` dropped are caught; cross-product survives (M1).

Gate: ruff check and format, mypy, vulture clean; `pytest -q` 1,932 passed, 2 skipped (my run).

## Timing at s90000 (new build, once)

160,800 keys from `committed(...).blobs`, the index copied by backup (160,800 units): 1.090 s, 160,800 hits (builder: 1.067 s best of three; plan: 1.089 s).
Extra, to find the break-even (best of three, both implementations, same table): 1,000 keys of 160,800 rows 0.0112 s per-key against 0.1412 s scan; 5,000 keys 0.058 against 0.170; 20,000 keys 0.229 against 0.264; 50,000 keys 0.584 against 0.451.

## Findings

### M1 Minor: tests cannot tell a membership test on path and blob separately from the pair

`tests/gitstore/test_index_parses.py:97-126` (`scan_index`, `requested_keys`), `find_parses` line 35.
Scenario: a refactor tests `path in requested_paths and blob in requested_blobs` instead of `(path, blob) in requested`.
Every requested blob in the fixture is `"current"` and every other row is `"older"`, so no row has a requested path with another key's blob; the mutant passes all 22 tests in the file (run: `22 passed`).
In real data it is a file whose older content equals another file's current content, e.g. a row `(p1, b2)` with `p1` requested at `b1` and `b2` requested for `p2`; the mutant then returns an extra key and decodes an unrequested row.
Fix: give the fixture distinct blob names per unit, and add to the table rows `(path_of_unit_a, blob_of_unit_b)` for requested units a and b; assert the result has exactly the requested keys.

### M2 Minor: `SCAN_FROM` counts requested keys only, so the scan's cost depends on the table, not the request

`src/lodge/gitstore/index_parses.py:20,32`.
Scenario: 1,000 keys against a table of 160,800 rows costs 0.141 s instead of 0.011 s (13 times slower), and the break-even is near a quarter of the table (about 40,000 of 160,800).
Today nothing bounds a parse-only table (`keep_parses` does not enforce the cap; that is Task 10a Step 3a), so a long-lived index in a repository whose current tree has few thousand files can reach this.
Once Task 10a wires the cap (`max(16 MiB, 1,500 bytes per file)`, about 1.7 rows per file) the ratio stays small, and the plan fixes the threshold at 1,000, so this is not a defect against the plan.
Fix: none needed now; Task 10a Step 4 should time a 1,000-key lookup against a table at the cap, or `find_parses` should scan only when `len(keys)` times a constant exceeds `SELECT max(rowid)` (one b-tree probe).

### M3 Minor: an SQL error in the middle of the scan loses every hit, where the per-key reader keeps the rest

`index_parses.py:34` (the cursor iteration is outside the per-row `try`) with `index_db.py:136-141` (`except Exception: return {}`).
Scenario: a damaged page or a failed read at row 700 of 1,500: run (`sqlerr.py`) gives 0 of 1,500 hits for the scan, against partial hits per key (999 of 999 on the same fault with the per-key branch).
Safe (all misses, the files are reparsed and `keep_parses` re-inserts), but it is the one case where the scan's result is not the per-key result, and `test_lookup_keeps_partial_hits` covers only the per-key branch.
Fix: wrap the loop so that an exception from the cursor returns `found` as collected, and add a case to `test_index_fixes.py`; or accept and record it in the report.

### M4 Minor: the plan still tells Task 10a to use the function this commit removes

`docs/superpowers/plans/2026-10-31-lodge-at-scale.md:637` ("use `settings_key` when constructing the stored state's key") and `docs/superpowers/plans/2026-10-31-lodge-at-scale-progress.md:87`; the report (`task-9c-report.md`, Concerns) says Task 10a must implement a digest, but the plan was not edited.
Scenario: the Task 10a builder follows line 637, finds no `settings_key`, and either rewrites it with `to_plain` (which `task-9-review.md` M5 showed fails on a new `CoreSettings` field) or asks.
Fix: change line 637 to "add a settings digest, `sha1(repr(settings).encode()).hexdigest()` (not `to_plain`, task-9-review M5), when constructing the stored state's key", and the ledger line to match.

### M5 Minor: three things only a builder needs

- `tests/gitstore/test_index_parses.py:188`: the comment "Exercise the new branch in this case too before implementing it." explains the edit, not a fact; the same test (`test_scan_reads_once[999]`) also checks two things (999 keys do 999 lookups, then 1,500 keys scan once) and passes for any count only by running a second request; split it or drop the second half, since the 1,000 and 1,500 cases already cover the scan.
- `tests/gitstore/test_index_fixes.py:76-80`: `forbidden` is monkeypatched onto a name that no longer exists (`raising=False`), so it can never fire; `test_parse_only_module_has_no_settings_key` (line 56) already guards the removal. Delete `forbidden`, the `setattr`, and the then-unused `CoreSettings` import if nothing else uses it.
- `task-9c-report.md` lines 40 to 180 paste about 140 lines of red pytest output (15 near-identical tracebacks); keep the command and the count.

## Design pass

No boundary change: the port and `find_parses` keep their signatures, and the decoder is shared by both branches, which is what keeps "scan equals per key" true by construction.
`SCAN_FROM` is a bare module constant read by one function; fine.
Removing `settings_key` also removes the `CoreSettings` import from `index_db.py`, leaving `gitstore` free of a `core` settings dependency in the parse-only module; `sha1` is still used by `build_digest`.
Plan rule without a test: "the scan visits only requested rows' values" (decode only requested rows) is true in the code but untested; a mutant decoding every row would pass and cost seconds at the cap. Covered by M1's fix if the test also counts `from_plain` calls (optional).

## Files read

`src/lodge/gitstore/index_parses.py`, `index_db.py` (lines 1-200), `src/lodge/app/state.py` (40-110), `src/lodge/app/ports.py` (parses), `index_space.py` (cap constants); the diff of e4fd032 in full; `tests/gitstore/test_index_parses.py`, `test_index_fixes.py` (parts); the plan's Task 9c and Task 10a Step 3a, the progress ledger lines on 7b; `review-codex-67.md` F1, `review-codex-7b.md` B1, B3; `task-9c-report.md` (all); `/var/tmp/lodge-bench/task-9c-mutants.py`, `task-9c-bench.py` (head).
Not read: Task 8c material, other tasks' reports, `plan-fix-6/` files other than the two reviews, the viewer and cli code.
