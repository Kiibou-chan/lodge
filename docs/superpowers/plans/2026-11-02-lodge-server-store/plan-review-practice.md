# Plan review, practice angle: plan 2, the events store and the operations

Reviewer: practice angle, from the builder's seat (Codex, one task per brief, no network, no sockets, read-only git index).
Plan under review: `docs/superpowers/plans/2026-11-02-lodge-server-store.md` at 7204ad3 on `server-store`.
Status: done.

## Findings

### P-I1 (Important): Task 7b's test calls `show`, which lane A ports in Task 4, while lane B waits only for Task 3

Handle: plan line 405 (`lodge_adds_through_the_store`: "and `show` of the new entry reads it"), line 389 (Consumes: Tasks 3 and 7a), line 188 (7b waits for 3, 7a), line 198 ("lane B needs only `#app`'s ports and `Lodge.add`"); `Lodge.show` is first produced at line 291 (Task 4).
Failure: lane B reaches 7b while lane A is still on Task 4, as the lanes are meant to run; `lodge.show` does not exist on `Lodge`, `tsc` fails on the test, and Codex either stops BLOCKED or invents a stub, which is plan 1's Task 11 `checkChange` trap again.
The same test also "adds the pair of `ts/tests/app/writes-attach.test.ts`": those drafts are locals of a `.test.ts` file (`tests/app/test_writes_attach.py:9-16`), and importing a test file from another registers its tests a second time.
Fix: assert the add through the store without `show`, as `load((await store.trees())[0]).entries.has("s-bbbbbb")` and the decision's attachment path in `attachments`; build the drafts in the test from `applying.ts` (`decisionText`, `specText`), naming them in the plan.

### P-I2 (Important): Task 9 calls `confirm`, which Task 6 ports, but waits only for Tasks 4 and 8

Handle: plan line 460 (`a_refused_write_leaves_no_event`: "a failing add, a failing confirmation, and a dry run"), line 447 (Consumes: Tasks 4 and 8), line 190 (Waits for 4, 8).
Failure: Task 8 finishes before lane A reaches Task 6, the coordinator starts Task 9 as the table allows, and `Lodge.confirm` is missing, so the test does not compile.
Fix: Task 9 waits for 6 (table row and Consumes), or the test drops the failing confirmation and Task 11's `an_agent_cannot_confirm` asserts the event count instead.

Verified: in the scratch worktree, a `b.test.ts` importing one constant from `a.test.ts` ran 2 tests, the imported file's test among them.

### P-I3 (Important): Task 10's new required parameters break carried core tests and lane A's `app/threads.ts`

Handle: plan lines 482-483 (`isAuthor(d, people)`, `parseThread(path, text, people)`, `writeThread(thread, people)`, no default stated, unlike `confirmationDraft` at line 484), line 505 ("every carried core test unchanged"), line 198 ("lane C touches only `ts/src/core` and `ts/tests/core`").
Plan 1's carried tests call the old shapes: `ts/tests/core/derive.test.ts:7-8` (`isAuthor(decision(...))`), `ts/tests/core/thread-text.test.ts:8-10` and `ts/tests/core/thread-files.test.ts:20,26,47,77` (`writeThread(t)`, `parseThread(path, text)`), on `server-core` at f09e6a6.
Lane A's Task 4 ports `src/lodge/app/threads.py:81`, `core.write_thread(thread)`, into `ts/src/app/threads.ts` (plan line 293).
Failure 1: with required parameters `tsc` fails on the three carried test files, which Step 4 forbids editing, so Codex has two contradictory instructions and stops or edits carried tests.
Failure 2: if Task 4 has merged before Task 10, `ts/src/app/threads.ts` stops compiling after Task 10, outside its Files and outside lane C's claim; if Task 10 merges first, Task 4's brief says nothing about `people`, and its builder passes whatever compiles.
Fix: give the three functions a trailing `people: ReadonlySet<string> = AUTHOR_ONLY` (exported from `people.ts` as the one default), as `confirmationDraft` has; state that carried calls stay as they are; Task 11 already passes the snapshot's `people` from `app` (line 520), and its Step 3 adds `grep -n "writeThread(\|isAuthor(" ts/src/app` showing two arguments at every site.

### P-M1 (Minor): `tree()`'s new default hides a core call site that drops the tree's people

Handle: plan line 480 (`tree()` fills `people` with `author` alone); `ts/src/core/apply-areas.ts:65` on `server-core` at f09e6a6 (`restored`) builds `load(tree({ rev: add.tree.rev, files: … }))`, and Task 10's Files (line 473) do not name `apply-areas.ts`.
Failure: today that after-state is read only for `derive(...).status`, which does not depend on who decided, so nothing visible breaks; but the default turns any later site that forgets `people` into a silent `{author}` that compiles, and Task 13 makes `derive` per person.
Fix: Task 10 passes `people: add.tree.people` at `apply-areas.ts:65`, and its Step 3 runs `grep -n "tree({" ts/src` and requires `people` at every hit outside `snapshot.ts`.

### P-I4 (Important): Task 4's carried write tests turn red only because `draft` is missing, and 13 of them never turn red

Handle: plan lines 287 and 297-298 (Task 4 carries `writes.test.ts` and `writes-dates.test.ts`; "expected: the new tests FAIL"); `add` and `mint` are Task 3's (line 265).
Of the 19 tests of `tests/app/test_writes.py`, 13 call only `add` or `mint` (for example `test_add_fills_id_and_date_from_ports`, `:30-35`, and `test_mint_gives_up_after_ten_draws`), so over Task 3's code they pass on arrival and Step 2's expectation is false for them; the other 6 call `draft`.
All 6 tests of `tests/app/test_writes_dates.py` build their drafts through `edit()`, which calls `wired(store).draft(...)` (`:14-18`), so they fail in Step 2 only because `Lodge.draft` does not exist: a whole-function red, the trap plan 1 hit, while the code they are about (`_after_newest`, Task 3) is never shown to matter.
Task 5 (line 312) and the Global Constraint (line 24) ask for "a mutation of that code the report names", which a throw at the top of `threads.write` satisfies for all 27 thread tests at once.
Failure: a wrong `afterNewest` reading (plan line 268, for example `>=` for `>` against `WAITS`) ships with six green date tests that were never red for a reason of their own.
Fix: Task 4's Step 2 names the 13 add-only tests and the 6 date tests as tests over Task 3's code and requires, after `draft` exists, a targeted mutation per group that leaves every other test green: the sleep skipped in `afterNewest` (the 6 date tests), the dry run publishing, the check skipped, `mintUnused`'s ten draws raised to eleven; tighten line 24 to "a targeted mutation, not a throw at the function's entry, one per test or per named group, listed in the report as a table", as Task 8c of plan 1 did (its ledger line 78).

### P-I5 (Important): two carried test files will pass 300 lines, and the parity rows name one file each

Handle: plan line 287 (`reads.test.ts`), line 307 (`thread-ops.test.ts`); `tests/app/test_reads.py` is 282 lines and `test_thread_ops.py` 250 (`wc -l`); `ts/tests/structure/calls.ts` `sizeViolations` counts `tests/` too, limit 300 (`table.ts`).
On plan 1, the TypeScript port of a core test file ran 0.79 to 1.51 times its Python lines, median about 1.1 (computed over every `ported` row of `ts/tests/parity.json` at f09e6a6), and app tests add an `await` or a `.rejects` to most lines; 282 at 1.1 is 310, and four plan 1 files over the limit were split (`test_fileformat.py` to 300 and 82 lines, `test_derive.py`, `test_feedback.py`, `test_apply.py`), each row's `ts` naming both.
Failure: Codex writes `reads.test.ts` whole, the structure test fails on size, and splitting it means editing a parity row's `ts` list and a Files list the brief did not give, so the builder stops or splits at random.
This is an estimate from plan 1's ratios, not a measured port.
Fix: name the split now: `reads.test.ts` and `reads-flags.test.ts` (or another cut by topic, the Python test names listed per file), `thread-ops.test.ts` and `thread-ops-staged.test.ts`, and say each task sets its row's `ts` to both files.

### P-I6 (Important): Task 11's flag test and Task 13's new flag words race, since the two run in parallel

Handle: plan line 524 (`an_agent_edit_of_a_persons_entry_waits`: "gives the review flag's feedback line"), line 570 (Task 13 rewrites that line from `this decision will wait for the author: …` to `this decision will wait for P: …`), line 199 ("Tasks 11 and 13 may also run in parallel"); the line's lodge 0.2 text is `src/lodge/core/feedback.py:83-87`.
Failure: Task 11 is built while Task 13 is unmerged and asserts lodge 0.2's words, the only ones that exist then, for `ada`'s entry; Task 13 merges and the line reads `this decision will wait for ada: …`, so Task 11's test fails on `server-store` after a merge whose own tests are green; nothing in the plan fixes which of the two merges first.
Fix: Task 11's test asserts that a feedback line starts with `this decision will wait for` and that `derive`'s `awaitingAuthor` holds the decision, never the person's words; or Task 11 waits for Task 13.

### P-I7 (Important): Task 12 is two reviews' worth, across the port, the operations, the fakes, the schema, and the store

Handle: plan lines 534-535 (ten files modified, among them `ports.ts`, `results.ts`, `writes.ts`, `lodge.ts`, `schema.ts`, `events.ts`, `sqlite-store.ts`, `fakes.ts`, `interleaving.ts`; two new test files with 14 tests), lines 546-548 (approval re-running `add`'s attempts as another person, a migration, three new event kinds, and `publish`'s `approves` under the same compare-and-set).
d-mfayy5 split plan 1's tasks at about 1,100 lines of module and test, and every other task here keeps the app and the store apart.
Failure: one Codex run carries the hold rule, the approval, and the migration at once; a review that rejects the migration also sends back the operations, and `writes.ts`, already about 214 Python lines ported (`src/lodge/app/writes.py`) plus Task 11's people, takes the hold logic and nears the 300-line limit with no module named for it.
Fix: split into 12a (the port's three methods and `approves`, `HeldDraft`, `Held`, `AddOutcome.HELD`, `Lodge.held`, `approve`, `decline` in a new `ts/src/app/held.ts`, `MemoryStore` and `Interleaving`, `app/held.test.ts`) and 12b (`MIGRATIONS[1]`, the `held`, `approved`, and `declined` cases of `applyEvent`, `SqliteStore`'s methods, `store/held.test.ts`), 12b waiting for 12a; `approval_and_files_land_together` calls `publish(base, writes, message, seq)` directly so 12b needs no `Lodge`.

### P-M2 (Minor): the Kysely table interfaces, as the plan words them, fail knip

Handle: plan line 361 ("The Kysely interfaces are `EventsTable` …, `HeadsTable`, `FilesTable`, and `MembersTable`"), line 168 (`#store` exports `Tables` only); likewise `MIGRATIONS` (line 360, read again by Task 12) and `NewEvent` (line 364) once `events.ts` leaves `entry` in Task 7b.
Verified: in the scratch worktree, a `schema.ts` exporting `EventsTable` and `HeadsTable` behind an `index.ts` re-exporting `Tables` made knip 6.42.0 report `Unused exported types (2)`, failing the gate.
Failure: Codex exports them because the plan names them as interfaces of the module, and spends a round on knip, as plan 1's builders did on `entry` bookkeeping.
Fix: say that `EventsTable`, `HeadsTable`, `FilesTable`, `MembersTable`, and `MIGRATIONS` are declared without `export`, and that `NewEvent` is exported only if `sqlite-store.ts` names the type.

### P-M3 (Minor): the fakes' constructors are positional while the plan cites d-vd3175 for them

Handle: plan line 239 ("d-vd3175 for its constructors"), lines 242-243 (`FixedClock(start = START, stepMs = 0)`, `CountingIds(first = 1, step = 1)`), line 273 (`wired(store, clock = …, ids = …)`); the carried tests call them with keywords, `CountingIds(step=0)` (`tests/app/test_writes.py:149`), `CountingIds(first=9, step=-1)` (`tests/app/test_thread_ops.py:186`), `FixedClock(step=timedelta(seconds=1))` (`tests/app/test_writes.py:39`); d-vd3175's reasoning binds `app` only.
Failure: the cited ruling and the stated signature disagree, so Task 2's builder picks one; if it takes the ruling, `new CountingIds({ step: 0 })` and the plan's signature no longer match, and Task 4's brief, which quotes the signature, is wrong about the code it builds on.
Fix: drop "d-vd3175 for its constructors" and say the test helpers stay positional, with the keyword calls above written out (`new CountingIds(1, 0)`, `new FixedClock(START, 1000)`).

### P-M4 (Minor): `wired` and the store tests need `Store`, not `MemoryStore`

Handle: plan line 273 (`wired(store, …)`, no type), Python's `wired(store: MemoryStore, …)` (`tests/app/support.py:26-29`); Task 9 passes a `SqliteStore` and an `Interleaving` (lines 450 and 457), and Task 11 changes `wired` (line 517).
Failure: Task 3's builder ports the annotation, and Task 9's builder must widen a helper outside its Files.
Fix: state `wired(store: Store, clock = new FixedClock(), ids = new CountingIds())` in Task 3.

### P-M5 (Minor): `Interleaved` has no constructor in the plan, and Python's hard-codes its drafts

Handle: plan lines 421-424 (no signature for `Interleaved` or `Interleaving`), `tests/gitstore/test_concurrent.py:29-36` (`self.drafts = A_DRAFTS`); Task 9's `every_write_is_checked_against_the_state_it_lands_on` runs a different add through it (line 459), and Task 9's Files do not name `interleaving.ts` (line 443).
Failure: a line-for-line port keeps `A_DRAFTS` inside the class, and Task 9's builder edits a file its brief did not give or copies the class.
Fix: give `constructor(inner: Store, during: Lodge, drafts: readonly (readonly [string, string])[])` with `outcomes: PublishOutcome[]`, and `Interleaving`'s `constructor(inner: Store)` with `attempts`, `publishes`, `rejectNext`, `movesAfterRead`, and `async files()`.

### P-M6 (Minor): `schema_1_is_migrated_to_2` needs a schema-1 file the plan does not say how to make

Handle: plan line 553; `openDatabase` always migrates to the newest schema (line 358), and `MIGRATIONS` is module-internal.
Failure: Codex exports `MIGRATIONS` or adds a version option to `openDatabase` to build the fixture, widening `#store` for one test.
Fix: say that the test writes Task 7a's schema through a raw `bun:sqlite` connection from the statements of line 360, sets `user_version` to 1, appends one event, and then opens it with `openDatabase`.

### P-M7 (Minor): Task 10's Files hedge on a place plan 1 has already settled

Handle: plan line 473 ("`ts/src/core/derive-review.ts` (or wherever plan 1 left `isAuthor`)", "and the core modules that call them").
On `server-core` at f09e6a6, `isAuthor` is `ts/src/core/derive-review.ts:4`, re-exported by `derive.ts:8` and called at `derive.ts:101`, which the Files list omits.
Failure: Codex's brief gives a guess where a path is known, and `derive.ts` reaches the task as an unlisted file.
Fix: list `derive.ts` and `apply-areas.ts` (P-M1) and drop the hedge.

### P-M8 (Minor): the plan does not say whether a flipped parity row gains `task`

Handle: plan lines 25 and 252 ("flips its rows"); plan 1's rows carry `"task": ["5a"]` and the like (`ts/tests/parity.json`, for example `tests/core/test_fileformat.py`), though no parity test reads it (`ts/tests/parity.test.ts:30-50`).
Failure: half the rows of plan 2 carry `task` and half do not, and plan 3's builders copy whichever they see.
Fix: one clause in line 25: "and sets `task` to the task's number".

### P-M9 (Minor): "`store` imports only `kysely` and `bun:sqlite`, and uses no process" is not enforced

Handle: plan line 30; `ts/.dependency-cruiser.cjs` has `core-imports` and `app-imports` but no rule on `store`'s npm imports, and `ts/tests/structure/calls.ts:67` bans `process` and `Bun` only where `pkg` is `core` or `app`.
Failure: a builder imports another npm package or reads `process.env` in `store`, and the gate stays green, so the plan states a rule no test holds.
Fix: either word line 30 as what the gate checks (`fs`, `fetch`, sockets, and `bun:sqlite` confinement), or record a decision adding a `store-imports` rule allowing only `kysely`, which tightens rather than loosens, with a planted test in `imports.test.ts`.

## Verified, no finding

- Task 1's pin: `npm view kysely time` gives 0.29.7 published 2026-10-17T15:49Z, 16 days before 2026-11-02, and 0.29.8 published 2026-11-01, too new; 0.29.7 has no `dependencies` or `peerDependencies` (its `package.json`), so `bun.lock` gains three lines and nothing else.
- Kysely 0.29.7 over `bun:sqlite` with `probes/db.ts`'s wrapper, in a scratch worktree at `server-core` f09e6a6 with `#app` and `#store` planted: `tsc` 6.0.3 under the repository's strict `tsconfig.json` (with `exactOptionalPropertyTypes`) clean, Biome 2.5.15 `--error-on-warnings` clean, dependency-cruiser clean (`bun:sqlite` resolves; `sqlite-confinement` allows `store`), and knip reports no unlisted dependency for `bun:sqlite`.
- The schema as Task 7a words it, in `bun test`: the two triggers refuse `update` and `delete` with `events are append-only`; a migration and `pragma user_version = 1` run in one Kysely transaction; a second open keeps `user_version` 1 and `journal_mode` `wal`; `user_version` 9 is refused; a `blob` returns `ef bb bf 80` unchanged.
- Two `openDatabase` connections on one file in one process: a compare-and-set whose first statement is the `update` returns `numUpdatedRows` `0n` on a stale base at once, with no lock wait; `insert … returning seq` works through the wrapper (`reader` is true for it).
  `numUpdatedRows` is a `bigint`, and `tsc` refuses a comparison with a number (TS2367), so no builder can test it against `0` by mistake.
- No builder step needs a socket or the network; only Task 1 installs, outside the sandbox.
- The "Exports read in a later task" table matches the import lines of `src/lodge/app/*.py` (`reads.py:11`, `threads.py:10-11`), and every `#core` name the app port calls (`newestLast`, `cleanText`, `parseCoreSettings`, `SettingsError`, `writeThread`, `threadPath`, `appended`, `checkChange`, `behindArea`, `confirmableIds`, `searchCounted`, `restsOnTree`, `level1`, `VIEWER`, `pyRepr`, `instant`, `isStamp`) is exported by `ts/src/core/index.ts` at f09e6a6, directly or through `export *`.
- Lane C does not touch Task 7a's `text.ts` or `fileformat.ts`, and `derive(...).status` does not read who decided (`src/lodge/core/derive.py:43-62`).

## Not verified

- WAL's `-shm` file and `fcntl` locks inside Codex's sandbox under the system's temporary folder: I ran the probes outside it.
- The 300-line estimate of P-I5 is from plan 1's ratios, not a port.

## Files read

The plan, its ledger, `probes.md`, `planner-report.md`, `planner-brief.md`, and `probes/db.ts`, `probes/p5-cas.ts`, `probes/package.json`; `CLAUDE.md`; lodge decisions d-vd3175, d-t7er56, d-tha8st, d-mfayy5, d-s2rdn2, and d-hshapm through `lodge show`; `src/lodge/app/*.py` (imports and function lines; `lodge.py`'s delegation), `src/lodge/core/feedback.py:78-110`, `src/lodge/core/derive.py:40-75`; `tests/app/fakes.py`, `support.py`, `conftest.py`, `test_writes_attach.py:1-40`, `test_writes.py:25-50`, `test_writes_dates.py`, `test_thread_fix_paths.py`, `tests/gitstore/test_concurrent.py`; on `server-core` at f09e6a6: `ts/package.json`, `ts/knip.json`, `ts/tsconfig.json`, `ts/biome.json`, `ts/.dependency-cruiser.cjs`, `ts/tests/structure/calls.ts`, `ts/tests/structure/table.ts`, `ts/tests/parity.test.ts` (test lines), `ts/src/core/index.ts` and `snapshot.ts:1-30`, `apply-areas.ts:55-75`, greps of `ts/src/core` and `ts/tests/core`, plan 1's ledger (grep).
Not read: the server design, plan 1 in full, plans 3 and 4, `tests/app/test_reads.py`, `test_thread_ops.py`, `test_confirm.py`, `test_writes_retry.py`, and `test_reads_published.py` beyond their import and call lines, and the decisions behind the model changes (d-kj59bz, d-znagqe, d-4spcem, d-wje1cn), which are the correctness and design angles' ground.

## Counts

0 Blocking, 7 Important (P-I1 to P-I7), 9 Minor (P-M1 to P-M9).
Status: done.
