# Task 9 review

Commit 16d2366 on 72ce4c6, reviewed in a scratch worktree at 16d2366 (removed afterwards; `ts/node_modules` was symlinked, never installed).
`sh scripts/check-ts.sh` there: exit 0, `1218 pass`, `2 todo`, `0 fail`, 93 files.

Files read: the brief, the report, the plan's Task 9 and Global Constraints, `ts/tests/store/seed.ts`, `ts/tests/app/reads-published.test.ts`, `ts/tests/app/writes-retry.test.ts`, `ts/tests/store/checked-writes.test.ts`, `ts/tests/parity.test.ts`, `ts/tests/parity.json`, `ts/tests/store/interleaving.ts`, `ts/tests/store/support.ts`, `ts/tests/app/support.ts`, `ts/knip.json`, `ts/src/app/writes.ts`, `ts/src/app/confirm.ts`, `ts/src/store/sqlite-store.ts`, `ts/src/store/read-tree.ts`, and the Python originals `tests/app/test_reads_published.py` and `tests/app/test_writes_retry.py`.
Files not read: `ts/src/core/*` beyond a grep for the check 5 message, `ts/tests/store/concurrent.test.ts`, the Python viewer and gitstore tests, and the codex log files.

## Correctness

Eight Python titles and three parametrised cases of `test_writes_retry.py` and the six titles of `test_reads_published.py` are all present with their Python assertions, class and message both (`raises(..., Conflict, "it changed since the draft was made")` and the `three times` match, `exitCode` 1 and 2, `attempts`, `publishes`).
Where Python had no message (area and entry conflicts, usage errors) none is added, so nothing is weakened.
Fixtures match Python's (`project()` is `seeded(AREA, ENTRY, FIRST)`, `MemoryStore(AREA)` is `seeded(AREA)`, `MemoryStore()` is `seeded()`).
The reads tests change by design (d-fv20kp, the plan's text): the edit goes through `add`, is refused with check `[5]`, no event is written, and the reads stay clean.
I probed that the reads are not vacuous: `search("transcripts")` finds `s-aaaaaa` and `d-aaaaaa`, and the timeline holds `d-aaaaaa`, so `items[0]?.flags` is defined; bun's `not.toContain` on `undefined` would throw, not pass.

Mutations I re-ran (each reverted; counts over the three suites, 20 tests):

| Mutation | Result |
| --- | --- |
| `ATTEMPTS = 1` in `writes.ts` | 5 fail, including `every_write_is_checked_against_the_state_it_lands_on` |
| compare-and-set predicate removed in `touchHead` | 7 fail |
| compare-and-set result ignored in `SqliteStore.publish` | 7 fail |
| every refusal classified `Conflict` | 4 fail, all three `unhashable` cases among them |
| store `gate` returns an empty published tree | 2 fail |
| `checkChange(after, after)` (published state ignored) | 8 fail |
| mine: check skipped on a retry only (`first === s`) | 1 fail, the race test, so that test does prove the check runs on the state the write lands on |
| mine: dry run falls through to publish | 1 fail, `a_refused_write_leaves_no_event` |

No Blocking found.

## Findings

1. Minor, `ts/tests/store/checked-writes.test.ts:41`: the "failing confirmation" leg of `a_refused_write_leaves_no_event` is `confirm([FIRST.id], "Read.")`, and `FIRST` is decided by the author, so `confirmDecisions` throws `StaleList` at `ts/src/app/confirm.ts:57` before `add` runs.
The leg therefore proves the stale-list guard writes nothing, not that a check failure on a confirmation does; no mutation of the write path can make it fail (the dry-run mutation fails the third leg, the skipped check the first).
The plan's wording allows it, and a confirmation that reaches `add` and fails the check is hard to build on a valid server state.
Fix: say so in a one-line test comment or in the ledger line, or build the leg through `Interleaved` so the confirmation lands on a retired entry.

2. Minor, `ts/tests/parity.test.ts:41,46,50`: the changed-row predicate `r.status === "ported" || (r.status === "changed" && ...)` is written three times, with `[1, 2].includes(r.plan ?? 0)` in one and `r.plan === 2` in the others.
Scenario: a later plan-3 changed row is added to one rule and not the others.
No in-repo test covers the new selection (`a_ported_file_losing_a_name_fails` calls `rowMissing` directly; the builder's parity mutations were by hand), so reverting the predicate to `ported` only would pass the gate.
Fix: one `held(r)` helper, and a planted-fixture test that a plan 2 `changed` row losing a name fails.

3. Minor, `ts/tests/store/seed.ts:8-12`: the `opened` list, `afterEach` close, `FixedClock`, and `SqliteProjects.create` repeat `setup()` in `ts/tests/store/support.ts:5-17`, which differs only in the project and owner names (`storage`/`ada` against `storage-notes`/`author`).
Fix: let `setup` take the names (defaults unchanged) and `seeded` call it, so one hook closes the databases.

4. Minor, `ts/tests/app/reads-published.test.ts:12,18` against `ts/tests/store/support.ts:19`: the events are read with an unordered `selectFrom("events").selectAll().execute()` twice, while the shared `events(database)` helper orders by `seq`.
Scenario: `toEqual(before)` over an unordered result relies on SQLite's rowid order.
Fix: use `events` (move it out of `store/support.ts` or import it).

5. Minor, `ts/tests/app/writes-retry.test.ts:76-142`: five tests repeat `try { await ...; throw new Error("expected conflict") } catch (e) { expect(e).toBeInstanceOf(...) }` where `raises` of `support.ts` exists.
It fails correctly if nothing throws, but with the message `Expected instance of Conflict` rather than the real cause.
The same tests assert `exitCode` in a way `raises` does not, so a small `caught(promise)` helper returning the error would serve all five.

6. Minor, `ts/tests/app/writes-retry.test.ts:141`: the `test.each` gives the three cases one title, so a failure (the M6 mutation printed three identical `(fail) unhashable_names_are_usage_errors` lines) does not say which case broke.
Python's ids (`area-name-list`, `entry-id-list`, `entry-id-mapping`) are lost.
Fix: add the id as a second, unprinted column only if `parity-names.ts` still reads the title; otherwise leave, since the plan fixes the title.

7. Minor, plan text `docs/superpowers/plans/2026-11-02-lodge-server-store.md:216,220` and the brief's "three changed files": the plan miscounts.
Judgement on the builder's note: correct.
`parity.json` holds exactly two `changed` rows with `plan` 2 (`test_reads_published.py`, `test_writes_retry.py`); `checked-writes.test.ts` has no Python original, and `every_python_test_file_is_in_the_table` forbids a row for a file that does not exist in `tests/`; `test_concurrent.py` is a `ported` row of Task 8.
No code change; the ledger line should record two files, and the plan's "three" is a wording slip to fix when the plan is next touched.
The plan's `ts/knip.json` step is likewise vacuous: the file holds no `tests/store/interleaving.ts` entry at 16d2366 or before, and knip passes, so nothing was left to remove.

8. Minor, `ts/tests/store/checked-writes.test.ts:51`: `expect((await store.gate(current)).published).toBe(current)` holds for any store whose `gate` echoes its argument (`ts/src/store/sqlite-store.ts:41-43` does exactly that), so the identity check proves nothing about the database; the real proof is the `check(true)` equals `problems()` line above it.
The plan words it this way, so it stays, but the report's claim that it tests the gate result is stronger than the assertion.

## Practice and design

All four new files and `parity.test.ts` are well under 300 lines (24, 62, 147, 68, 75).
No personal path, name, or email appears in the new files (grepped); fixtures are the made-up `storage` area, the owner `author` as the plan's `seed.ts` text requires.
No production file changed, and `ts/knip.json`, `package.json`, and Python are untouched.
The report is dense and its mutation table is accurate in everything I re-ran; it does not list a mutation for the dry-run leg or the confirmation leg of `a_refused_write_leaves_no_event` (findings 1 and the dry-run result above).
Boundaries hold: the tests import only `#app`, `#core`, `#store`, and sibling test helpers, and `Interleaving` and `Interleaved` are read, so knip is satisfied.

Verdict: 0 Blocking, 0 Important, 8 Minor
