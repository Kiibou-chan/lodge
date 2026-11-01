# Plan fix round 3

Recheck: `plan-recheck-2.md` (V1 to V3 Important, V4 to V8 Minor).
Every finding was taken; none is parked.
The coordinator's ruling for this round is d-t3afj1, replacing d-6hb3yd: the class behind V1 and V2 is removed rather than patched, since nothing a kept state depends on is ever deleted.
The calls are d-4j98ph (replaces d-aej8rs; narrows d-dxqxsn and d-eby5pb), d-3ck8km (one file per build in WAL mode, replacing d-gvz66f and d-4n5tr6), and d-n6tqzq (narrows d-9r24jc and d-dqpf59).

## The index's consistency, rewritten (d-t3afj1)

The Global Constraints' invariants now say:

1. Parse units, with their words rows sharing the parse row's rowid, and facts are content-addressed and immutable, never deleted except by a whole-index clear in place.
2. A state owns only its own rows, written in one transaction with its state row last.
3. Eviction deletes only the evicted state's own rows, by its key, and no FTS row is ever deleted.
4. Every write transaction checks used pages against `INDEX_FILE_CAP` and clears in place when over it, provided a state was kept since the last clear or the units inserted since the last clear number at least the tree's file count (d-cqr414).
5. Transactions are explicit in WAL mode with `synchronous=NORMAL` (d-3ck8km).
6. A reader takes anything missing or short as a miss.

The sweep for paths that relied on the old eviction:

| Place | Before | Now |
|---|---|---|
| Task 9, files | one file per build, rollback journal, `synchronous=FULL`, journals pruned with their files | one file per build, WAL, `synchronous=NORMAL`, `-wal` and `-shm` pruned with their files under an exclusive lock when 7 days unwritten or beyond the four most recently touched builds |
| Task 9, parses | rows written in one transaction, evicted from Task 10a on | `INSERT OR IGNORE`, never updated or deleted; `test_parse_units_are_immutable` |
| Task 9, flag and conversion caches | kept in the index | kept in the process only (d-n6tqzq) |
| Task 9, growth | unbounded parse rows | the cap and an in-place clear; `test_cap_counts_used_pages`, `test_two_writers_over_the_cap_clear_once` |
| Task 10a, `keep_state` | wrote missing parse units, then evicted units no kept state referenced | inserts the misses its build found and the facts, evicts only the oldest state's own rows, replaces a re-kept key whole |
| Task 10a, eviction tests | `test_eviction_drops_only_what_the_state_owns` | `test_eviction_deletes_only_the_states_own_rows`, `test_revert_to_the_evicted_states_contents`, `test_unit_found_by_one_process_survives_another_keep` |
| Task 10a, concurrency tests | two tests that could not fail under rollback-journal isolation | `test_reader_keeps_its_snapshot_across_a_commit`, which fails under Python's default `sqlite3` mode |
| Task 10b, words | dropped with their parse unit | immutable with it, no key column, rowid shared |
| Task 10c, facts | kept for the idents kept states name | immutable, never evicted |
| Task 11, folder rows | one transaction | one `BEGIN IMMEDIATE` transaction, rows replaced in place, each carrying its own key |

## Recheck findings

| Finding | Change in the plan | Decision |
|---|---|---|
| V1, a unit only the evicted and the new state reference can be dropped | Nothing but a state's own rows is ever evicted; tests for the single-process and the two-process sequence | d-t3afj1, d-4j98ph |
| V2, the eviction's mechanism and cost | Eviction is a delete by state key of 1,024 buckets, answers, and citer rows; no reference counting; the cost table and Task 10a's Step 4 name it; the rebuild past the cap is a row of its own | d-t3afj1, d-3ck8km |
| V3, reads are not one transaction under Python's default mode | `isolation_level=None`, WAL, `BEGIN` ... `COMMIT` around every read and `BEGIN IMMEDIATE` around every write; a re-kept key replaces the state whole and becomes the newest; `test_reader_keeps_its_snapshot_across_a_commit`, `test_rekeep_replaces_the_state_whole` | d-t3afj1, d-3ck8km |
| V4, cache keys taken after the git call | Keys taken before the call and the stat again after it, the result kept only when the two are equal; the stat named; an interleaving test in Task 8b | d-n6tqzq |
| V5, a family root without a citer row | A citer row for every code and every family root; such a root among the search property test's queries | d-4j98ph |
| V6, `git status` turns a seen read into a write | Flag and conversion results live in the process only; the flags call's 0.020 s is in the cost table; `test_seen_read_writes_nothing` runs after a `git status` | d-n6tqzq |
| V7, the FTS key column is indexed | No key column; rowid shared with the parse row; column filters; `test_path_words_are_not_candidates` | d-4j98ph |
| V8, `keep_parses` callers and a cycle | `core.parse_words` holds the words of a parse; Task 10b lists `app/state.py` and `tests/app/fakes.py` | none needed |
