# Plan fix round 1: plan 2, the events store and the operations

Planner, fix round 1, on `server-store` from be72406, answering `plan-review-correctness.md` (0 Blocking, 9 Important, 10 Minor) and `plan-review-practice.md` (0 Blocking, 7 Important, 9 Minor).
Status: done.

## Rulings recorded

- d-pmaw3a (replaces d-pprhpz, narrows d-fv20kp): `SqliteStore.publish` refuses what lodge 0.2's `check_writes` refuses, a path holding a surrogate, and a changed text for an existing decision file; it runs no other check (I-7, I-8, M-7).
- d-vwsnz5 (replaces d-kj59bz): a person is an owner of the project; `isAuthor`, `parseThread`, and `writeThread` take the people as a defaulted trailing parameter; a name the records use as a role cannot join (I-3, I-6, I-9, P-I3).
- d-x6vaw8: only a person writes a thread message under their own name; the author is asked STORE-1 in `questions.md` (I-5).
- d-d96y91 (narrows d-t7er56): a lane's tests call only what its waits provide; a ported function's new parameter has a default; Task 12 splits into 12a and 12b (I-2, P-I1, P-I2, M-3, P-I6, M-10, P-I7).
- d-nf7wvx: a dependency-cruiser rule `store-imports` (P-M9; probe 9).
- d-thvvzx: a store transaction that reads before it writes opens with a write, and a hold settles once (I-1, M-8).

## Findings

Each finding is answered by a change to the plan, named by the section that holds it, or by a ruling; "the plan" is `docs/superpowers/plans/2026-11-02-lodge-server-store.md` at this round's commit.

### Correctness

- I-1 (approval and decline both land; one hold approved twice): ruled d-thvvzx; fixed in Task 12a: an approving `publish` reads the hold inside its transaction after the compare-and-set and answers `REJECTED` unless it is open, `decline` refuses a hold not open inside its own write-first transaction, and `applyEvent` throws on an approval or decline of a hold not open; tests `a_declined_hold_cannot_be_approved`, `a_hold_is_approved_once`, `a_settled_hold_cannot_be_declined`, and `rebuild_refuses_an_impossible_history` (store), `memory_store_settles_a_hold_once` (fake), and `a_declined_hold_cannot_be_approved` in Task 12b (operations); Task 12b's `approve` answers `NotFound` when a re-read finds the hold settled.
- I-2 (Task 7b calls `show`): ruled d-d96y91 (the second option, to keep lane B parallel); fixed in Task 7b's `lodge_adds_through_the_store`, which reads through `load((await store.trees())[0])` and the tree's `attachments`, its drafts built from `applying.ts`.
- I-3 (a person's name equal to an agent role): ruled d-vwsnz5 (the first option, refusing at the join, with no reserved list); fixed in Task 7b's `addMember`, which refuses a name the current state uses as `decidedBy` or a thread message's `by` with `Conflict`, and test `a_name_used_as_a_role_cannot_join`; `create` needs no check, since a new project holds no records.
- I-4 (`threadsWaiting` splits by the literal `author`): fixed in Task 11: `waitingIn` splits by `people.has(last.by)`, with test `a_persons_question_waits_for_an_agent`.
- I-5 (nothing ties a thread message's `by` to the actor): ruled d-x6vaw8, and the value trade-off goes to the author as STORE-1 in `questions.md`; fixed in Task 11's `_message`: a `by` naming a person other than the actor is `Forbidden`, with tests `an_agent_cannot_write_as_a_person` and `a_person_writes_only_as_themselves`; a person writing under a role stays allowed, since the carried tests write `by: agent`, `reviewer`, and `coordinator` through `wired`'s `person("author")` (25 such calls in `tests/app/*.py`).
- I-6 (members counted as deciding people): ruled d-vwsnz5, replacing d-kj59bz, following design lines 74 and 261; fixed in Task 11 (`readTree` gives the owners; `owners_are_the_people_of_the_tree` asserts `{ada}` for owner `ada` and member `bo`), in "Interfaces for plans 3 and 4", and in `confirm`, which refuses a person not among the people (`a_person_not_among_the_people_cannot_confirm`).
- I-7 (`publish` refuses less than lodge 0.2): ruled d-pmaw3a; fixed in Task 7b's `publish` (lodge 0.2's `check_writes` ported with its two messages) and its tests `path_outside_lodge_is_refused` (eight paths) and `an_attachment_is_never_overwritten`.
- I-8 (an unchecked `publish` rewriting a decision reads clean; d-pprhpz's cost false): ruled d-pmaw3a, replacing d-pprhpz with the store refusing a changed decision file (the reviewer's fix) and a cost that holds; fixed in Task 7b (`a_published_decision_is_never_rewritten`), in "Interfaces for plans 3 and 4", in Task 9's `reads-published.test.ts` lead, and in Review Focus 4.
- I-9 (Task 10's signatures break lane A): ruled d-vwsnz5 and d-d96y91; fixed in Task 10: `isAuthor`, `parseThread`, and `writeThread` take `people = AUTHOR_ONLY` last, with the lanes paragraph saying so.
- M-1 (`Interleaving` missing from the exports table): fixed: a row for `tests/store/interleaving.ts` (into `entry` in Task 8, out in Task 9), and `ts/knip.json` in both tasks' Files.
- M-2 (Task 12 raises `user_version` under Task 7a's test): fixed in Task 12a, which lists `database.test.ts` and moves `schema_is_created_once` to 2, and says how `schema_1_is_migrated_to_2` builds its file (the first option of P-M6 and M-2: a raw `bun:sqlite` connection with migration 0's statements written out, since `MIGRATIONS` stays unexported for knip).
- M-3 (Task 11's feedback test races Task 13): ruled d-d96y91 (the first option); fixed in Task 11's `an_agent_edit_of_a_persons_entry_waits`, which reads the line's first words and `derive`'s `awaitingAuthor`, and in Task 13, which keeps those first words.
- M-4 (`Interleaved`'s drafts; `Interleaving.files()` and attachments): fixed in Task 8: both constructors written out, the drafts a parameter, and `files()` the tree's `files` with `attachmentTexts()`.
- M-5 (probe 7 misses a decoder that swallows the next byte): fixed in Task 7a with probe 11's three cases in `decode_utf8_like_surrogateescape`; plan 4's twenty cases stay plan 4's, since d-ryss91 has it test the codec it consumes.
- M-6 (`write` trips the call rule): fixed in Task 4: Python's `threads.write` is `writeMessage`.
- M-7 (`path` is a `text` column): ruled d-pmaw3a (the first option, refusing, over a `blob` path for a name only a hand-made file has); fixed in Task 7b's `publish` and `a_path_holding_a_surrogate_is_refused`.
- M-8 (create and addMember fail as `database is locked`): ruled d-thvvzx (the first option, a write first, so no deployment rule is needed); fixed in Task 7b's `create` and `addMember`, with `a_second_create_conflicts_across_connections`, and in "Interfaces for plans 3 and 4".
- M-9 (no test that one person's add of another's decision is held): fixed in Task 12b, `another_persons_add_is_held`.
- M-10 (Tasks 9 and 11 both edit the store tests): ruled d-d96y91; fixed in the lanes table (Task 11 waits for 9), in Task 8 and Task 9 (project owner `author`, each `Lodge` acting as `person("author")` once Task 11 lands), and in Task 11's Files.

### Practice

- P-I1 (Task 7b's test calls `show`; the drafts are a test file's locals): as I-2; the drafts come from `decisionText` and `specText` of `ts/tests/core/applying.ts`, named in Task 7b.
- P-I2 (Task 9 calls `confirm` but waits only for 4 and 8): ruled d-d96y91; fixed in the lanes table and Task 9's Consumes (Tasks 6 and 8).
- P-I3 (required parameters break carried tests and `app/threads.ts`): as I-9; Task 10 gives the three a trailing `people = AUTHOR_ONLY` from `people.ts`, names the carried calls that stay, and its Step 3 greps the core's calls; Task 11's Step 3 greps `app`'s.
- P-M1 (`tree()`'s default hides `apply-areas.ts:65`): fixed in Task 10's Files (`restored` passes `people: add.tree.people`) and Step 3 (`grep … tree({` shows `people` at every call but the definition).
- P-I4 (carried write tests red only for want of `draft`; thirteen never red): fixed in Task 3, which now carries the thirteen add-only tests of `test_writes.py` by name, red for want of the code they test; in Task 4, which names the twelve tests that call `draft` and requires a targeted mutation table for them, with mutations of `afterNewest` named for the date tests; and in the Global Constraints, whose test-first line now asks for a targeted mutation, never a throw at a function's entry, listed as a table.
- P-I5 (two carried test files over 300 lines): fixed in Task 4 (`reads.test.ts` and `reads-checks.test.ts`, the Python tests listed per file) and Task 5 (`thread-ops.test.ts` and `thread-ops-publish.test.ts`, cut at `tests/app/test_thread_ops.py:156`), each row's `ts` naming both, which the Global Constraints now say.
- P-I6 (Task 11's flag test races Task 13): as M-3.
- P-I7 (Task 12 two reviews' worth): ruled d-d96y91; Task 12 is now 12a (the port's held drafts with `SqliteStore`, `MemoryStore`, and `Interleaving`, the migration, and the store tests) and 12b (`held.ts`, `AddOutcome.HELD`, and the operations); the order is the reverse of the review's, since a method added to `Store` fails `tsc` until both stores implement it (probe 10, TS2420), so the port and its implementations cannot be split apart.
- P-M2 (Kysely table interfaces fail knip): fixed under "Exports read in a later task" and in Task 7a: `EventsTable`, `HeadsTable`, `FilesTable`, `MembersTable`, `HeldTable`, and `MIGRATIONS` are declared without `export`, and `NewEvent` is exported only if another module names it.
- P-M3 (positional fakes cited to d-vd3175): fixed in Task 2: the citation dropped, the constructors positional, and the three keyword calls written out.
- P-M4 (`wired` needs `Store`): fixed in Task 3 (`wired(store: Store, …)`) and Task 11.
- P-M5 (`Interleaved` has no constructor): as M-4.
- P-M6 (`schema_1_is_migrated_to_2` needs a schema-1 file): as M-2.
- P-M7 (Task 10's Files hedge): fixed: Task 10 lists `derive.ts` (where `isAuthor` is at `server-core` 579fb11, `derive.ts:153`; there is no `derive-review.ts` there) and `apply-areas.ts`, and Task 13's Files drop `derive-review.ts`.
- P-M8 (whether a flipped row gains `task`): fixed in the Global Constraints' porting line.
- P-M9 (the store's import rule not enforced): ruled d-nf7wvx (the second option, a rule, since it makes the stated constraint true and tightens only); fixed in the Global Constraints' structure line and Task 7a (the rule, `STORE_NPM`, and three planted tests), probe 9 having planted it.

## Changes to the lanes

- Task 9 waits for Tasks 6 and 8 (was 4 and 8); Task 11 waits for Tasks 9 and 10 (was 6, 8, and 10); Task 12 is 12a (waits for 11) and 12b (waits for 12a); lanes A, B, and C keep their tasks.
- Lane B's Task 7b reads the store through `load` and needs only Tasks 3 and 7a; lane C's new parameters are defaulted, so lanes A and C merge in either order.

## For plans 3 and 4 (also in the ledger)

- Plan 3: thread messages are bound to the actor (d-x6vaw8): an agent token writing `by: <person>` is `Forbidden`, so its carried command tests that write `--by author` with where and when through the agent token (`tests/e2e/test_threads.py`'s `author_words_are_recorded_exactly` and `test_waiting.py`'s `waiting_groups_threads`) write through the person's session or change, until STORE-1 is answered; the refusal comes after lodge 0.2's own, so `author_message_needs_where_and_when_exit_2` keeps its message.
- Plan 3: `publish` refuses a changed decision file, a path lodge 0.2 refuses, an existing attachment, and a surrogate path (d-pmaw3a); a hand edit through `projects.storeFor(…, agent("hand"))` can still write a new file, an entry, an area, or a thread, but `broken-agent-decision-warns-above-show` rewrites an existing decision (`tests/e2e/test_broken_agent_decision_warns_above_show.py:15-16`), and `check-and-gate`'s hand edit must write a new file, as its second half does.
- Plan 3: `Tree.people` are the owners, not the members (d-vwsnz5), and `confirm` refuses a person who is not an owner; `addMember` refuses a name the records use as a role, with `Conflict`.
- Plan 3: `applyEvent` updates `heads` for every kind but `project` and never upserts, so its account events of the empty project add no row (as its alignment asked); `create`'s first statement is the `heads` insert, so a racing create is `Conflict`.
- Plans 3 and 4: Task 12 is now 12a (the port's `hold`, `held`, `decline`, and `approves`, with both stores) and 12b (`Lodge`'s `held`, `approve`, `decline`, and `AddOutcome.HELD`); an approving `publish` of a hold not open answers `REJECTED`, and `Store.decline` of one throws `NotFound`; plan 4's Task 6 (the export wrapper passing the Task 12 methods) waits for 12a, and plan 3's `approval_failing_the_check_answers_422` cites a test now in Task 12b.
- Plan 4: `parseThread` and `writeThread` take `people` as a defaulted last parameter (unchanged names); `publish` refuses a path holding a surrogate, so a lodge 0.2 store with a non-UTF-8 file name fails the import's publish with `LodgeError` unless plan 4's own check refuses it first; a lodge 0.2 record whose role equals the owner's name would read as the owner's after import, which plan 4's state check may wish to refuse.
