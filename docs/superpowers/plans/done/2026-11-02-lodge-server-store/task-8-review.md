# Task 8 review

Build commit 11806a5 on `server-store-b`, reviewed in a scratch worktree at that commit (since removed).
`sh scripts/check-ts.sh` there: Biome, `tsc`, dependency-cruiser, knip clean; `1125 pass, 0 fail, 2793 expect() calls, 84 files`.

## Files read

`CLAUDE.md`, `task-8-brief.md`, `task-8-report.md`, `task-7a-review.md` (m-2), `tests/gitstore/test_concurrent.py`, and in `ts/`: `src/store/{schema,sqlite-store,read-tree,events}.ts`, `tests/store/{concurrent.test,interleaving,interleaving.test,wal.test,support}.ts`, `tests/app/fakes.ts`, `tests/parity.json` (plan 2 rows), `knip.json`, and the commit's diff.
Not read: `src/app/writes.ts` beyond a grep, the rest of `tests/store/*.test.ts`, Task 4 and 7b reports, the plan's other tasks.

## Pass 1: correctness

The three carried titles keep Python's assertions: outcomes `[REJECTED, PUBLISHED]`, three entries, three decisions, the area order, and `checkState(...).ok`.
The two-connection case reads the final state through a third connection, as the brief says.
No fixture holds a personal path or real data; `ada`, `bo`, and `storage` stay synthetic, and `grep` of the diff for `/home`, `<user>`, and `.cache` is empty.

Mutations run (each in the scratch worktree, reverted by `git checkout` after the run; commands: `bun test tests/store`):

| # | Mutation | Result |
|---|---|---|
| M1 | `touchHead`: drop the `rev` predicate (`read-tree.ts:22`) | 4 fail: the three carried tests and `stale_base_is_rejected_and_writes_nothing` |
| M4 | `publish`: append the events even when `touchHead` fails, then return REJECTED (`sqlite-store.ts:92`) | 4 fail: the same four |
| W1 | `schema.ts:61`: the original pragma line (`journal_mode=WAL; busy_timeout=5000` in one `exec`, no check) | 1 fail: `contended_first_open_enters_wal`, `journal_mode` `delete` |
| W3 | `schema.ts:61`: keep the check, drop `busy_timeout` | 1 fail: same test (the `LodgeError` fires) |
| W2 | `schema.ts:64`: delete the `throw new LodgeError(...)` | 0 fail, survives (finding 2) |
| I1 | `Interleaved.trees`: fire on every call, not once | 2 fail |
| I2 | `Interleaved.trees`: fire before the inner read, not after | 2 fail |
| H11 | `Interleaved.publish`: do not record the outcome | 2 fail |
| H2 | `Interleaving.publish`: record rejected writes too | 1 fail |
| H3 | `Interleaving.publish`: record `writes`, not a copy | 1 fail |
| H4 | `Interleaving.publish`: do not count `attempts` | 1 fail |
| H5 | `Interleaving.publish`: land every queued change at once | 1 fail |
| H6 | `Interleaving.trees`: land the move before the read | 1 fail |
| H8, H9, H10 | forward `gate`, `commit`, `freshness` wrongly | each fails 1 or 2 |
| H1 | `Interleaving.files`: drop `attachmentTexts()` | 0 fail, survives (finding 1) |
| H12 | `Forwarding.attachmentTexts`: return an empty map | 0 fail, survives (finding 1) |
| H7 | `Interleaving.land`: accept a non-published outcome | 0 fail, survives (finding 3) |

Parked m-2: fixed as the 7a review asked (busy timeout first, answer of `PRAGMA journal_mode=WAL` checked, `memory` allowed for `:memory:`), and `contended_first_open_enters_wal` fails without it (W1 above: `delete` instead of `wal`, 854 ms, so the contention is real).
The test holds a read transaction from a child process on a new file and waits on a handshake before opening, so the contention does not depend on timing luck beyond the child's 800 ms hold.

### 1. Important: `files()` including attachments, and the forwarding of `attachmentTexts`, are not guarded

Handle: `ts/tests/store/interleaving.test.ts:36` and `ts/tests/app/fakes.ts:60`; run H1 and H12 above (both pass).
`MemoryStore.attachmentTexts` filters on `` `${ATTACHMENTS}/` ``, and `ATTACHMENTS` is `"lodge/attachments/"` (`src/core/snapshot.ts:36`), so the filter looks for `lodge/attachments//` and always returns an empty map.
Separately, `MemoryStore.trees().files` already holds attachment paths, so `Interleaving.files()` returns the attachment whether or not it merges `attachmentTexts()`.
Failure scenario: someone makes `files()` return `current.files` alone, or makes `Forwarding.attachmentTexts` return an empty map; over `SqliteStore`, whose tree keeps attachments out of `files` (`read-tree.ts:36`), Task 9's attachment assertion then fails with no test here naming the cause.
I confirmed a probe over `SqliteStore` (`setup()` from `tests/store/support.ts`, publish `lodge/attachments/d-aaaaaa/log.txt`, assert `files().get(path)`) passes on the build and fails under H1.
Fix: add that probe to `interleaving.test.ts`; and correct the filter in `fakes.ts:60` to `path.startsWith(ATTACHMENTS)` (I ran the full suite with it: 1125 pass), so `expect(await store.attachmentTexts()).toEqual(await inner.attachmentTexts())` compares something non-empty.
The `fakes.ts` edit is an earlier task's file; the coordinator may rule it into this round or Task 9.

### 2. Minor: the `LodgeError` branch for an unexpected journal mode has no test

Handle: `ts/src/store/schema.ts:63-64`; run W2 (0 fail).
The brief's fix is "refuse unless `wal`"; the refusal is the reason the check exists, and it is unexercised.
Failure scenario: a refactor drops the check, and a database on a filesystem that cannot do WAL, or a contended open past the 5 s timeout, runs in rollback-journal mode again, silently.
Fix: a test needs a contention longer than `busy_timeout` (a 5 s holder, slow) or a second, injectable timeout; either is a design choice for the coordinator, so a parked minor is fair.

### 3. Minor: `Interleaving.land`'s refusal of a non-published change has no test

Handle: `ts/tests/store/interleaving.ts:67-68`; run H7 (0 fail).
Failure scenario: `rejectNext` called with a change that itself loses (over `SqliteStore` after a stale base) throws in the helper only because of this guard; without it the helper would quietly swallow the loss.
Fix: one test over a `MemoryStore` subclass or a stub whose `publish` answers REJECTED, expecting `rejects.toThrow`.

## Pass 2: practice

### 4. Minor: the `knip.json` entry is not needed

Handle: `ts/knip.json:8`; `bunx knip` with the line removed in the scratch worktree exits 0.
`Interleaving` is read by Task 8's own `interleaving.test.ts` and `Interleaved` by `concurrent.test.ts`, so d-tha8st's reason ("first reader comes in a later task") does not hold for these exports.
The entry also exempts every export of the file from knip, so an unused helper added later would not be reported.
Fix: drop the line; the plan's table row ("Out of entry: Task 9") then has nothing to remove, and the coordinator should note that when updating the ledger.

### 5. Minor: `openDatabase` refuses any path other than `":memory:"` that does not give `wal`

Handle: `ts/src/store/schema.ts:62`.
`""` (SQLite's private temporary database) and a `file::memory:` URI answer `memory` or `delete`, and now throw `LodgeError`; nothing in the repository opens either today (`grep -rn "openDatabase(" ts` shows only `":memory:"` and file paths), so this is a note on the contract only.
Fix: none needed now; if a later task opens such a path, compare against the mode SQLite reports for it.

Otherwise clean: names follow the repository's style, comments state facts (none added), the files stay far under 300 lines (largest new file 100), British English and no em-dashes in the report, and the report's mutation table matches what I reran (M1 three titles failing; the report names a smaller set because `stale_base_is_rejected_and_writes_nothing` also fails, which is only a bonus).

## Pass 3: design

- `Forwarding` as a private base class keeps `Interleaved` and `Interleaving` small and gives each a single reason to change; both conform to `Store` through it (`tsc` clean).
- The helpers differ from `MemoryStore`'s own `rejectNext` and `movesAfterRead` in that they land through `inner.publish`, so the store's real compare-and-set rejects, as the brief says; the interleaving test checks the semantics only over `MemoryStore`, and no test here runs `Interleaving` over `SqliteStore` (Task 9 will; finding 1's probe covers the first such case).
- The two-writer tests all run in one process: `bun:sqlite` calls are synchronous, so the interleaving is deterministic and the second connection never waits on the first's lock.
  This is what the brief asked (two connections on one file, as two server processes would hold), and the cross-process locking behaviour is covered only by the new WAL test; there is no plan rule that asks for more, so this is a note, not a finding.
- `parity.json` row: `changed` to `ported` with `"task": ["8"]` matches how the plan's other ported rows read; the `why` text is kept.
- Plan rules no test enforces: d-tha8st's entry-then-leave rule (finding 4) is applied by the builder without checking that knip needs it.

Verdict: 0 Blocking, 1 Important, 4 Minor
