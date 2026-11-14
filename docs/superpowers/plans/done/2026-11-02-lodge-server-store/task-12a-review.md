# Task 12a review

Reviewed commit f103fc0 on `server-store`, in a scratch worktree at that commit (removed after).
Gate `sh scripts/check-ts.sh` there: exit 0, 1248 pass, 2 todo, 0 fail.
Method: read the diff and the surrounding source, then applied 20 one-edit mutations to `src` and the `MemoryStore` fake, running `bun test tests/app tests/store` after each and reverting.
Fourteen mutations were killed; M3, M6, M8, M9, M10, and M15 survived (below).

## Pass 1: correctness

The behaviour matches the plan and d-znagqe, d-2v8vtk, d-thvvzx for what the code does.
- `publish` with `approves` runs the compare-and-set first (`ts/src/store/sqlite-store.ts:137`), then the open-hold read (`:138-146`), then the file events and the `approved` event in one transaction (`:147-152`); a hold not open answers `REJECTED` with nothing appended.
- A refusal thrown before the transaction (`:117-134`) leaves the hold open.
- `applyEvent` throws on a settle of a hold not open (`ts/src/store/events.ts:79-91`), and `rebuild` runs in one transaction, so an impossible history rolls back (`rebuild_refuses_an_impossible_history` fails against M4 and M5).
- Migration 1 from schema 1 keeps events (`schema_1_is_migrated_to_2` fails against M13).
- `MemoryStore` answers as the SQLite store does for: unknown hold on decline (`NotFound`), unknown or settled hold on approving publish (`REJECTED`), stale base (`REJECTED`, checked before the hold), listing order, and the rev moving on hold, decline, and approval (M16 to M20 killed).
- Settle-once holds for both `HeldAdd` and `HeldMessage` because the stores read only `person`.

No Blocking finding.

### I-1 (Important) `a_settled_hold_cannot_be_declined` does not tell `NotFound` from a plain `Error`

`ts/tests/store/held.test.ts:92-94` asserts `.rejects.toThrow(new NotFound(...))`; bun compares an error object by message only.
Failure scenario: M3 deletes the `if (!held) throw new NotFound(...)` in `decline` (`ts/src/store/sqlite-store.ts:57`); `applyEvent`'s plain `Error` carries the same words, so all tests pass, while plan 3 maps `NotFound` to 404 and the same refusal would reach it as an untyped 500.
Fix: assert the class, `rejects.toBeInstanceOf(NotFound)` plus a message check (as `fakes-held.test.ts:24` does with `toThrow(NotFound)`).

### I-2 (Important) `holds_rebuild` empties `held` itself, so `rebuild`'s own `deleteFrom("held")` is untested

`ts/tests/store/held.test.ts:119` runs `deleteFrom("held")` before `rebuild`.
Failure scenario: M6 removes `await tx.deleteFrom("held").execute()` from `rebuild` (`ts/src/store/events.ts:98`); every test still passes, yet `rebuild` over a database with holds then dies on the primary-key conflict of the first replayed `held` event, which is the plan's "`rebuild` empties and refills `held` too".
Fix: drop line 119, so `rebuild` runs over the populated table and gives the same rows.

### I-3 (Important) Nothing tests that holds are scoped to their project

`ts/src/store/sqlite-store.ts:36`, `:44` (`decline`), and `:141` (`publish`) filter on `project`; M8, M9, and M10 each remove one filter and all tests pass, since every store test uses one project.
Failure scenario: `held()` without the filter lists another project's held drafts, with a person's quote, to this project's session; an approving `publish` or `decline` with another project's number settles a foreign hold (hold numbers are the global event `seq`, `:29`).
The plan requires "unless it is this project's and open" (Task 12a, `decline` and `publish`).
Fix: one test with two projects (`projects.create("other", "ada")`, a store each): `held()` lists only its own; `decline` and an approving `publish` with the other's number answer `NotFound` and `REJECTED`, and write no event.

### I-4 (Important) d-thvvzx's write-first rule for `decline` and an approving `publish` has no test

`ts/tests/store/write-first.test.ts:7` covers `create`, `addMember`, and `publish` without `approves`; M15 removes `decline`'s opening `touchHead` and all tests pass, so the missing-project `NotFound("no project named …")` is untested as well.
d-thvvzx names `decline` and the approving `publish` explicitly; the plan's Task 12a test list omits it, so the builder was not told.
Failure scenario: a later edit reads the hold before the write; two connections racing then fail with `database is locked` instead of a typed answer, which is the failure d-thvvzx closes.
Fix: add `decline` and an approving `publish` (with a held `seq`) to the `test.each` and a missing-project case for `hold` and `decline`.

## Pass 2: practice

### P-M1 (Minor) The hold lookup is written twice

`ts/src/store/sqlite-store.ts:44-50` and `:138-146` are the same select on `held`.
Fix: one `openHold(tx, project, seq)` in `read-tree.ts` or `events.ts`, used by both.

### P-M2 (Minor) `MemoryStore.hold` hard-codes a stamp

`ts/tests/app/fakes.ts:57` repeats the literal of `START` (`:26`) instead of `stampOf(START)`.
Failure scenario: a task 12b test using a `FixedClock` with another start reads a `Held.at` that disagrees with the clock, which the SQLite store would take from the clock.
Fix: `at: stampOf(START)`, or give `MemoryStore` an optional clock.

### P-M3 (Minor) `decline` drops its reason in `MemoryStore`

`ts/tests/app/fakes.ts:64` names it `_reason` and records nothing, so a 12b test cannot assert the reason reached the store.
Fix: keep `declined: [seq, reason][]` on the fake.

Modules: all under 300 lines (largest test file `database.test.ts`, 204; `sqlite-store.ts`, 157).
No new dependency (`ts/package.json` and `bun.lock` untouched).
No em-dashes or non-British spellings in the diff.
The two files in `git status` (`task-12a-codex.log`, `-final.txt`) are untracked builder output, not part of the commit.

## Pass 3: design

- The port, both stores, and `Interleaving` carry the three methods and `approves`; `tsc` holds them together, as probe 10 predicts.
- `HeldDraft` is stored as unvalidated JSON and read back with a cast (`ts/src/store/sqlite-store.ts:41`, `events.ts:70`); that is the plan's choice (the stores read only `person`) and a corrupt body fails loudly at the NOT NULL column, so no finding.
- The plan assumes `MemoryStore` and `SqliteStore` answer alike; the differences left are only the size of a rev step (`land` adds one per publish, SQLite one per event) and hold numbers (the store's rev against the global event `seq`), neither observable to the operations of Task 12b.
- The `held` table has no index on `(project, state)`; `held()` scans by primary-key order with a filter, fine at this scale.
- No plan rule is broken that a test could check beyond I-1 to I-4.

## Files

Read: `task-12a-brief.md` (head and the SQLite section), `task-12a-report.md`, the plan (Task 12a, 12b, 12c, Interfaces, Global Constraints, Calls made), `lodge spec`, d-znagqe, d-2v8vtk, d-thvvzx, d-d96y91, the full diff of f103fc0, and the whole of `events.ts`, `read-tree.ts`, `schema.ts`, `sqlite-store.ts`, `fakes.ts`, `rebuild.test.ts`, `write-first.test.ts`, `support.ts`.
Not read: the rest of the brief (the Global Constraints repeat the plan's), the other `ts/tests` files, `projects.ts`, and the Python source.
Not run: a concurrent-connection race over an approval (the plan's Task 12a asks for none).

Verdict: 0 Blocking, 4 Important, 3 Minor
