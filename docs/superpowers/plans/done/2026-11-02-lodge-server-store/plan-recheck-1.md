# Plan recheck 1: plan 2, the events store and the operations

Rechecker, on `server-store`, fix round be72406..61f87ad, against `plan-review-correctness.md`, `plan-review-practice.md`, and `plan-fix-1.md`.
Line numbers are of the plan at 61f87ad (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`).
Plan 1's API was read at `origin/server-core` 9e133ea, of which the plan's 579fb11 is an ancestor.
One probe ran in a detached scratch worktree of `server-core` under `/var/tmp`, removed afterwards.
Status: done.

## Correctness findings

- I-1 · Resolved.
  d-thvvzx holds: an approving `publish` reads the hold inside the compare-and-set's transaction and answers `REJECTED` unless it is open (line 582), `Store.decline` refuses a hold not open inside a write-first transaction (line 581), and `applyEvent` throws on a settled hold (line 583).
  The store tests settle each case on a fresh tree, so they exercise the in-transaction check rather than the compare-and-set (`a_declined_hold_cannot_be_approved`, `a_hold_is_approved_once`, `rebuild_refuses_an_impossible_history`, line 588); Task 12b's `approve` reads again on `REJECTED` and answers `NotFound` (line 612).
- I-2 · Resolved.
  `lodge_adds_through_the_store` reads through `load((await store.trees())[0])` and the tree's `attachments` (line 424), its names from Task 3 (`AREA`, `wired`), plan 1's `filesOf` (`ts/tests/core/builders.ts:80` at 9e133ea), and `decisionText` and `specText` (`ts/tests/core/applying.ts:32,45`); Consumes says so (line 408).
- I-3 · Resolved.
  `addMember` refuses a name the current state uses as `decidedBy` or a thread message's `by`, inside its write-first transaction (line 418), with `a_name_used_as_a_role_cannot_join` (line 425); d-vwsnz5's handles check (design lines 74 and 261, `src/lodge/core/threads.py:85-88`).
- I-4 · Resolved.
  `waitingIn` splits by `people.has(last.by)` (line 555), matching `ThreadsWaiting`'s field order (`src/lodge/app/results.py:83-87`), with `a_persons_question_waits_for_an_agent` (line 559).
- I-5 · Resolved by ruling, with the value question correctly sent to the author.
  d-x6vaw8's handles check: design lines 75 and 76 (SRV-2), `src/lodge/app/threads.py:139-145`; the refusal is at line 554 and STORE-1 is in `questions.md` in the confirmed format.
  One gap in the test's wording is Minor N-3 below.
- I-6 · Resolved.
  `readTree` gives the owners (line 551), `owners_are_the_people_of_the_tree` asserts `{ada}` and then `{ada, cy}`, and `confirm` refuses a non-owner (line 556); d-vwsnz5 replaces d-kj59bz and cites design lines 74, 261, and 302, each of which says what the decision says it does.
- I-7 · Resolved.
  `publish` ports `check_writes` with both messages (line 412), which match `src/lodge/gitstore/plumbing.py:14-25` word for word; `path_outside_lodge_is_refused` covers the eight paths and `an_attachment_is_never_overwritten` the second message (line 424).
- I-8 · Resolved, with one claim of d-pmaw3a too broad (Minor N-2 below).
  The store refuses a changed decision file inside the state the compare-and-set matches (line 412), with `a_published_decision_is_never_rewritten`; d-pprhpz is replaced, and Task 9's lead and Review Focus 4 follow it (lines 481 and 77).
- I-9 · Resolved.
  `isAuthor`, `parseThread`, and `writeThread` take a trailing `people = AUTHOR_ONLY` (line 514), plan 1's carried one-argument calls are named (line 517; checked at 9e133ea: `ts/tests/core/derive.test.ts:7-8`, `thread-text.test.ts:8-10`, `thread-files.test.ts:20-162`, `builders.ts:84`), and lane A's `writeThread(thread)` is stated (line 307).
- M-1 · Resolved: the row at line 48, and `ts/knip.json` in Task 8's and Task 9's Files.
- M-2 · Resolved: Task 12a lists `database.test.ts` and moves `schema_is_created_once` to 2 (line 590), and `schema_1_is_migrated_to_2` writes migration 0 out (line 588).
- M-3 · Resolved: Task 11 reads the first words (line 559) and Task 13 keeps them (line 632); Task 10 leaves the feedback line to Task 13, so the words in between are lodge 0.2's and also start that way.
- M-4 · Resolved: both constructors (line 444), and `files()` with `attachmentTexts()`.
- M-5 · Resolved: probe 11's three cases (line 392).
- M-6 · Resolved: `writeMessage` (line 307).
- M-7 · Resolved by d-pmaw3a: a surrogate path is refused (line 412).
- M-8 · Resolved by d-thvvzx: `create` and `addMember` open with a write, with `a_second_create_conflicts_across_connections` (line 425).
- M-9 · Resolved: `another_persons_add_is_held` (line 615).
- M-10 · Resolved: Task 11 waits for 9 (line 202), and Tasks 8 and 9 say the project's owner and actor (lines 462 and 479).

## Practice findings

- P-I1 · Resolved, as I-2 (line 424).
- P-I2 · Resolved: Task 9 waits for 6 and 8 (line 200) and its Consumes names `confirm`.
- P-I3 · Resolved, as I-9; Task 10's Step 3 and Task 11's Step 3 grep the call sites (lines 537 and 562).
- P-I4 · Resolved.
  The thirteen add-only tests are Task 3's (lines 287 and 289), and the list matches an AST pass over `tests/app/test_writes.py` (thirteen call only `add` or `mint`, six call `draft`); Task 4 names the six and the date tests with targeted mutations of `afterNewest`; the Global Constraint forbids a throw at a function's entry (line 24).
- P-I5 · Resolved: `reads.test.ts` takes eleven tests and `reads-checks.test.ts` thirteen, together the 24 of `tests/app/test_reads.py` (line 310); the thread-ops cut at Python line 156 splits 15 and 13 (line 329); the row names both files (line 26).
- P-I6 · Resolved, as M-3.
- P-I7 · Resolved differently, and adequately.
  The split runs port and stores first (12a), operations second (12b), the reverse of the review's; probe 10's TS2420 is a sound reason (`probes/p10-implements.ts`), since `MemoryStore`, `Interleaving`, and `Interleaved` all implement `Store`.
  The split introduced an import cycle, Important N-1 below.

Minors, as plan-fix-1 claims them:

- P-M1 · Resolved: `apply-areas.ts:65` is the only `tree({` call in `ts/src/core` at 9e133ea, and Task 10 passes `people` there (line 504).
- P-M2 · Resolved (line 50).
- P-M3 · Resolved (line 252).
- P-M4 · Resolved (lines 286 and 550).
- P-M5 · Resolved, as M-4.
- P-M6 · Resolved, as M-2.
- P-M7 · Resolved: `isAuthor` is at `ts/src/core/derive.ts:153` at 9e133ea, and there is no `derive-review.ts`.
- P-M8 · Resolved (line 26).
- P-M9 · Resolved by d-nf7wvx: probe 9's output matches the planted tests of line 394, and `STORE_NPM` sits beside `CORE_NPM` (`ts/tests/structure/table.ts:11` at 9e133ea), which `.dependency-cruiser.cjs:1` already reads.

## New findings

### N-1 · Important · Task 12b's `held.ts` and `writes.ts` import each other, which the `no-circular` rule fails

Handle: line 599 (`held.ts` holds "who an add awaits, and the operations `held`, `approve`, and `decline`"), line 600 (`writes.ts`: "`add`'s attempt holds where `held.ts` says"), and line 612 (`approve` "runs the held drafts through `add`'s attempts"); plan 1's rule `no-circular` (`ts/.dependency-cruiser.cjs:40-44` at 9e133ea, `from` `^(src|tests|scripts)/`, `to` `circular: true`, severity `error`).
So `writes.ts` imports `held.ts` for who an add awaits, and `held.ts` imports `writes.ts` for `add`'s attempts.
Verified: two modules planted in `ts/src/core` of a scratch copy at 9e133ea, each importing the other, give `error no-circular: src/core/held-a.ts → src/core/held-b.ts → src/core/held-a.ts` from `depcruise`.
Failure: the builder writes the files the plan names, `sh scripts/check-ts.sh` fails on dependency-cruiser, and the fix (a third module, or moving the approval into `lodge.ts`) is a design choice the brief does not make, so Codex stops BLOCKED or picks one; this is the trap d-d96y91 was written to remove.
Fix: name the cut in Task 12b: the rule of who an add awaits goes in `ts/src/app/awaits.ts` (or stays in `writes.ts`), which imports nothing of `held.ts`, and `held.ts` imports `writes.ts` for `add`'s attempts, so the edges run `held.ts → writes.ts → awaits.ts`; list the module under Create.

### N-2 · Minor · d-pmaw3a says no write of `app` rewrites a decision file, but a re-rendered decision with no field changed passes check 5 and reaches `publish`

Handle: d-pmaw3a's reasoning ("no write of `app` rewrites a decision file, since check 5 refuses an edit of a published decision before `publish`"); `src/lodge/core/apply.py:188` (an edit draft is written as `write_record(record)`, a fresh rendering), `src/lodge/app/writes.py:90` (`files` keeps every path whose text differs), and `src/lodge/core/check_immutable.py:49-52` (check 5 compares parsed fields, not text).
Failure: a decision file whose text is not lodge's own rendering, as plan 4's import copies a lodge 0.2 store byte for byte, is drafted and added back unchanged; the fields are equal, so check 5 passes, the rendered text differs, so `add` calls `publish`, and the store throws `LodgeError("… is a published decision, and lodge never rewrites a decision")` where lodge 0.2 publishes a reformatted file.
Nothing is lost or written, so this is Minor; but the decision's cost-if-wrong is stated for a later tool only, and Task 7b's `rebuild_gives_the_same_tables` ("three publishes, one rewriting a path", line 426) does not say the rewritten path must be an entry or an area, which a builder learns only from a red test.
Fix: amend d-pmaw3a's reasoning to "rewrites a decision's fields", naming the re-render case and its refusal as accepted; say "one rewriting an entry" at line 426.

### N-3 · Minor · the actor refusal comes after lodge 0.2's, so the test as worded meets the `where` refusal first

Handle: line 554 (`Forbidden` "after lodge 0.2's refusals"), line 559 (`an_agent_cannot_write_as_a_person`: an agent's `ask`, `reply`, and `close` "with `by: ada`: each `Forbidden`"); `src/lodge/app/threads.py:32-34` (a person's message without `where` is refused first, with a `LodgeError`).
Failure: the builder writes the three calls without `where`, as the line gives none, and each rejects with `LodgeError("a message by ada needs where, …")`; `rejects.toThrow(Forbidden)` fails, since `Forbidden` is the subclass, and the builder either reorders the refusals against line 554 or adds `where` unprompted.
Fix: say in the test that each call carries `where: "chat"`, so only the actor refusal is left.

### N-4 · Minor · the ledger still says there is no `questions.md`

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-store-progress.md:18` ("No value trade-off for the author, so no `questions.md`.") beside line 23 of the same file, which names STORE-1 in `questions.md`.
Failure: a reader of the ledger is told two opposite things about whether the author has a question waiting.
Fix: rewrite line 18 in place to say STORE-1 waits for the author (d-x6vaw8).

### N-5 · Minor · Task 10's Step 3 grep matches the three definitions, which pass no `people`

Handle: line 537 ("shows `people` passed at every call but `tree()`'s own definition"); at 9e133ea the same grep also prints `ts/src/core/derive.ts:153`, `threads.ts:25`, and `threads.ts:107`, the definitions of `isAuthor`, `parseThread`, and `writeThread`.
Failure: a literal builder reads the step as unmet, or a reviewer takes the step's evidence as checked when three lines were skipped by eye.
Fix: say "at every call but the definitions of `isAuthor`, `parseThread`, `writeThread`, and `tree`".

## Checked, no finding

- Lane waits against imports: Task 3's tests use Task 2's fakes and Task 3's `support.ts`; Task 7b's use Task 3, plan 1, and `#store`; Task 8's `Interleaved` takes a `Lodge` (Task 3); Task 9's use `show`, `draft`, `problems`, `check` (Task 4) and `confirm` (Task 6) through its waits on 6 and 8; Task 11 edits `threads.ts` (Task 4), `confirm.ts` (Task 6), and `read-tree.ts` (Task 7b) through 9 and 10; Task 12a edits `interleaving.ts` (Task 8) through 11; Task 12b uses only 12a's port and `MemoryStore`.
- Tasks 12a and 12b agree: the store's `decline` throws `NotFound` with the words `approve` and `decline` use, an approving `publish` answers `REJECTED` on a settled hold in both stores (lines 582 and 585), and 12b reads that as `NotFound` (line 612); `Interleaving` and `Interleaved` pass the new methods on (line 585), and `tests/app/fakes.py` is the only Python `Store` subclass in `tests/app`.
- Plan 1's API at 9e133ea: `checkChange(published, after, settings, now, current = null)` (`ts/src/core/check-change.ts:18-24`), `checkState(s)` (`check-state.ts:133`), `parseThread(path, text)` and `writeThread(thread)` (`threads.ts:25,107`), `confirmationDraft(confirms, scope, words, when, area)` (`confirmation.ts:38-44`), whose order Task 10's added trailing `person` keeps.
- `applyEvent`'s `heads` rule agrees between line 181's paragraph and Task 7a (an insert-or-update for `project`, an update for every other kind), and `create`'s first statement inserts the row at 0 before the `project` event moves it.
- The carried retry tests' concurrent changes (`tests/app/test_writes_retry.py:24,45,72,81`) write new attachments, an entry, and an area, none of which d-pmaw3a's refusals catch.

## Counts

Correctness: 9 Important and 10 Minor, all resolved.
Practice: 7 Important and 9 Minor, all resolved (P-I7 differently, adequately).
New: 0 Blocking, 1 Important (N-1), 4 Minor (N-2 to N-5).
