# Plan review, correctness: plan 2, the events store and the operations

Reviewer: reviewer agent, correctness angle, on `server-store` at 7204ad3.
Probes ran in a detached scratch worktree at 7204ad3, removed afterwards.
Status: done.

## Findings

### I-1 · Important · an approval and a decline of one hold can both land, and one hold can be approved twice

Handle: plan line 546 (`approve` "reading the holds afresh at each attempt") and line 548 (`approved` and `declined` "set its state"; `publish` with `approves` "after the same compare-and-set").
The compare-and-set protects an approval only if the hold's state was read at or after the tree's revision, and the plan fixes no order between `store.held()` and `store.trees()`, which are two reads, and two transactions on the connection (probe 3).
Failure: `approve(7)` awaits `held()` (hold 7 open, rev 40); the same person's `decline(7, …)` runs its whole transaction (rev 41); `approve` then awaits `trees()` (rev 41), checks, and publishes with base 41, which matches, so the drafts land and an `approved` event follows a `declined` one; `applyEvent` sets the state to `approved` and nothing refuses.
The same interleaving of two `approve(7)` calls publishes the drafts twice under two freshly minted decision IDs when the hold holds no entry `create` that would collide (a confirmation, or a decision that only links), so one approved draft becomes two current decisions.
Both run in one server process, since `Lodge`'s awaits interleave between Kysely transactions; no test covers it (`app/held.test.ts` and `store/held.test.ts`, line 552 and 553).
Fix: in `SqliteStore.publish` with `approves`, after the compare-and-set and in the same transaction, require `held.state = 'open'` for that `seq` (else `REJECTED`, so the attempt reads again and `approve` answers `NotFound`); make `Store.decline` refuse a hold that is not `open` inside its own transaction; have `applyEvent` throw on `approved` or `declined` for a hold that is not open, so `rebuild` cannot replay an impossible history; add `a_declined_hold_cannot_be_approved` and `a_hold_is_approved_once` over the SQLite store, interleaving through `Interleaving`.

### I-2 · Important · Task 7b's test calls `Lodge.show`, which only Task 4 ports, while lane B may run before it

Handle: plan line 405 (`lodge_adds_through_the_store`: "`show` of the new entry reads it"), line 389 ("Consumes: Tasks 3 and 7a"), and the lanes table at line 188 (7b waits for 3 and 7a); `show` arrives in Task 4 (line 291).
Failure: with lane A at Task 3, lane B starts 7b, whose test cannot call `show`; the builder either stops BLOCKED or weakens the test to something the plan did not ask for.
Fix: make 7b wait for Task 4 (lanes table and line 389), or have the test read the entry through `trees()` and `load` of `#core` instead of `show`.

### I-3 · Important · a person's name can be an agent role already used in the project, which turns past agent records into a person's

Handle: d-kj59bz ("`decided_by` names a person when it names a member"); d-wx7d0f's pattern `^[a-z][a-z0-9-]{0,31}$` (plan line 175), which admits `planner`, `builder`, `reviewer`, and `coordinator`, the roles every agent decision of lodge uses (`lodge guide`'s example has `decided_by: coordinator`); `isAuthor(d, people)` and `parseThread(path, text, people)` (plan lines 482 and 483) read the whole state with today's members.
Failure: `addMember("work", "reviewer", "member", …)` makes every earlier `decided_by: reviewer` decision a person's decision without a quote, so check 3 fails on each and every read flags it `fails check` (s-q4s548 shows a record wrongly as failing); every thread message `by: reviewer`, written with a stamp and no `where`, now parses as a person's message and the thread file becomes a check 1 problem (`src/lodge/core/threads.py:85-88`); every later agent add as `reviewer` is held for a person.
The reverse also holds: an agent role equal to a member's name is that member, so the agent's add is held, which is the intended rule, but only by luck of naming.
Fix: `SqliteProjects.create` and `addMember` refuse a name that appears as `decided_by` of a decision or `by` of a thread message in the project's current state (`Conflict`, naming the record), with a test `a_name_used_as_a_role_cannot_join`; or record the agent roles and person names as disjoint name spaces in d-kj59bz and enforce it at both ends.

### I-4 · Important · `threadsWaiting` still splits threads by the literal `author`

Handle: `src/lodge/app/threads.py:139-145` (`waiting_in`: `t.messages[-1].by == "author"` for `for_agent`, `!=` for `for_author`); Task 11 changes only `_message` of `threads.ts` (plan line 520), and Task 10's word table does not list it (lines 487 to 497).
Failure: with people `{ada}`, a question whose last message is `ada`'s is listed in `for_author` (waiting for the person) instead of `for_agent`, so `lodge waiting` tells the agent nothing waits for it and tells `ada` her own question waits for her; an agent's reply lands in `for_author` correctly only because it is not `author`.
No test of Task 11 catches it (`app/people.test.ts`, line 524).
Fix: Task 11 reads `people.has(t.messages.at(-1).by)` in `waiting_in`, with a test `a_persons_question_waits_for_an_agent` over people `{ada, bo}`.

### I-5 · Important · nothing ties a thread message's `by` to the actor, so any session writes a person's words in a thread

Handle: Task 11 (plan lines 516 to 521) binds the actor in `confirm` only; `ask`, `reply`, and `close` keep `by: string` (lines 149 to 151) and check it only against `people`; plan 3 passes `by` from the request body (`origin/server-api`, its plan line 185 and 186).
Failure: an agent token calls `reply("q-…", "ada", "Yes, retire it.", { where: "chat", when: "2026-11-02 10:00" })`; the message is stored as `ada`'s, with her `where` and a minute, and reads as her answer; the design's sign-in makes a person "a place an agent cannot reach" (design line 76), and the guide's "close a thread only when the author asked for it" is now enforceable but not enforced.
Fix: in Task 11, an agent actor writing `by` that names a person, or a person actor writing `by` other than their own name, throws `Forbidden("only <person> writes as <person>; nothing was written")`, with tests `an_agent_cannot_write_as_a_person` and `a_person_writes_only_as_themselves`; if the author wants agents to relay a person's words in threads, that is a question for her, not a silent default.

### I-6 · Important · members count as people, where the design makes the person who decides one of the project's owners

Handle: design line 74 ("'the author' becomes the person who decided, one of the project's owners") and line 261 (`owner` "decides, confirms"; `member` "works on tasks, answers questions, raises doubts"); plan line 518 and d-kj59bz ("owners and members alike"), and the test `members_are_the_people_of_the_tree` (line 525: owner `ada` and member `bo` give `{ada, bo}`).
d-kj59bz argues that one person signs in until step 7, but this plan builds `addMember` with roles now and writes a test that fixes members as deciding people, against the approved design.
Failure: plan 3 exposes `addMember` (its Task 4); a `member` `bo` then confirms (Task 11 refuses only agents, line 521), and an agent's flagged decision clears on a member's word, and `bo`'s decisions count as a person's decisions, which the design gives to owners.
Fix: `SqliteStore.trees()` gives `people` = the owners, the test asserts `{ada}` for owner `ada` and member `bo`, and d-kj59bz is narrowed to say so; or, if the planner holds that members must decide too, that changes what the design says and goes to the author, not into a test.

### I-7 · Important · `SqliteStore.publish` refuses less than lodge 0.2's store, so a bad path blocks the export and an attachment can be replaced

Handle: plan line 393 (refuses only "a path not under `lodge/`"); lodge 0.2's `check_writes` (`src/lodge/gitstore/plumbing.py:14-25`) also refuses an empty, `.`, `..`, or `.git` part, a backslash, and a NUL, and an existing attachment ("lodge never overwrites an attachment"), with the message `<path> is outside lodge/, which is all the store writes`; d-ae1vn5 keeps lodge 0.2's outcomes.
Failure: `publish(base, new Map([["lodge/../x", "…"]]), "x")` is accepted, since the path starts with `lodge/`, and is kept for good in an append-only table; plan 4's export writes every file of the project through a temporary index (its plan line 7), and `git update-index --add --cacheinfo` refuses `lodge/../x`, `lodge//x`, and `lodge/.git/x` with `Invalid path` (run here with an isolated git), so every export of that project fails from then on, while `lodge\x` is accepted by git as one odd file name.
A second `publish` of an existing `lodge/attachments/d-aaaaaa/run.log` replaces the evidence a published decision cites, and `trees()` and `attachmentTexts()` then give the new text as current.
Fix: port `check_writes` into `SqliteStore.publish` with lodge 0.2's two messages, before the transaction, against the attachments of the state the compare-and-set matches (inside it), and add `path_outside_lodge_is_refused` cases for `lodge/../x`, `lodge//x`, `lodge/.git/x`, `lodge\x`, and NUL, and `an_attachment_is_never_overwritten`.

### I-8 · Important · an unchecked `publish` that rewrites a decision reads clean on the server, against d-pprhpz's stated cost

Handle: d-pprhpz's "Cost if wrong: a later caller of `publish` without a check writes an unchecked state, which reads then flag as failing, as lodge 0.2's reads flag a hand edit"; d-ae1vn5 and plan line 174 make the published state the current one, so `read_checked` (`src/lodge/app/state.py:59-79`) compares a state with itself and checks 4, 5, and 6 can find nothing.
Verified: over lodge 0.2's `MemoryStore(AREA, ENTRY, FIRST)` with one state, as the SQLite store gives, a hand edit of `d-aaaaaa`'s statement gives `show flags ()`, `problems [] True`, and `gate [] True` (scratch script `onestate.py`, run with `uv run --frozen`).
Failure: plan 3's `handEdit` writes through `publish` to stand for lodge 0.2's hand edits (its plan line 494); any carried command test that expects a hand-edited published decision to read `fails check` cannot pass, and any later caller of `publish` rewrites a decision invisibly, which s-q4s548 and must-not 2 forbid.
Fix: make the store keep decisions immutable itself: `SqliteStore.publish` refuses (`LodgeError`) a write to an existing `lodge/decisions/` path whose bytes differ, inside the compare-and-set's transaction, with a test; then correct d-pprhpz's cost with a narrowing decision; plan 3's alignment round then rereads which carried tests a hand edit of a decision can still stand for.

### I-9 · Important · Task 10 changes `#core` signatures that lane A's `app` calls, so the lanes are not independent

Handle: plan line 198 ("lane C touches only `ts/src/core` and `ts/tests/core`, which no task of lanes A and B edits"); Task 10 changes `writeThread(thread)` to `writeThread(thread, people)` and `parseThread(path, text)` to take `people` (line 483), with no default stated, unlike `confirmationDraft`'s (line 484); Task 4's `threads.ts` calls `writeThread` (`src/lodge/app/threads.py:81`), and Task 10's Files (line 473) hold no `app` file.
Failure: Task 4 merges first; Task 10's lane then turns `tsc` red on `ts/src/app/threads.ts` at merge, a file its brief does not let the builder edit; or Task 10 merges first and Task 4's builder ports a call the plan describes without `people`.
Fix: give `parseThread` and `writeThread` a trailing `people` defaulting to `new Set(["author"])`, as `confirmationDraft`'s person defaults to `author`, so `app` compiles unchanged until Task 11 passes `current.people`; state it at line 483 and in the lanes paragraph.

### M-1 · Minor · `Interleaving` is first read in Task 9 but is missing from "Exports read in a later task"

Handle: plan lines 40 to 46 (the table) and 421 to 424 (Task 8 produces `Interleaved` and `Interleaving`; Task 8's own test uses only `Interleaved`, line 428; `Interleaving` is first read by Task 9's `writes-retry.test.ts`, line 457); Task 8's Files (line 415 to 417) hold no `ts/knip.json`.
Failure: knip reports `Interleaving` unused in Task 8, so the builder's gate is red on a file the task may not edit.
Fix: add the row `tests/store/interleaving.ts` · Task 8 · `Interleaving` (9) · Task 9, and list `ts/knip.json` under Modify in Tasks 8 and 9.

### M-2 · Minor · Task 12 raises `user_version` to 2 but leaves Task 7a's test asserting 1

Handle: `schema_is_created_once` ("at `user_version` 1", line 375); Task 12's `MIGRATIONS[1]` ("so `user_version` becomes 2", line 548); Task 12's Files (line 534) do not list `ts/tests/store/database.test.ts`, and the Global Constraints let a test change only where a task says so (line 24).
Failure: Task 12's gate fails on a test it may not edit; `schema_1_is_migrated_to_2` also needs "a file with Task 7a's schema" while `MIGRATIONS` holds two entries, and the plan does not say how the test builds it.
Fix: write `schema_is_created_once` against the number of migrations from the start (Task 7a), or list the file in Task 12; say that `schema_1_is_migrated_to_2` writes migration 0's statements through a raw `bun:sqlite` connection and sets `user_version` to 1 before `openDatabase`.

### M-3 · Minor · Task 11's feedback test and Task 13's new words race in parallel

Handle: Task 11's `an_agent_edit_of_a_persons_entry_waits` asserts "the review flag's feedback line" (line 524); Task 13 changes that line to `this decision will wait for P: …` (line 570); line 199 lets 11 and 13 run in parallel, and Task 13's Files (line 562) hold no app test.
Failure: if 11 merges first with lodge 0.2's words (`this decision will wait for the author: …`, `src/lodge/core/feedback.py:83-87`), Task 13 turns 11's test red on a file it may not edit.
Fix: Task 11's test asserts the line's prefix `this decision will wait for`, or Task 13 lists `ts/tests/app/people.test.ts` and updates its expected line to `… wait for ada: …`.

### M-4 · Minor · `Interleaved` needs its drafts as a parameter, and `Interleaving.files()` must include attachments

Handle: Python's `Interleaved` hard-codes `A_DRAFTS` (`tests/gitstore/test_concurrent.py:32-35`), while Task 9's `every_write_is_checked_against_the_state_it_lands_on` runs a different add through it (line 459); the plan gives no constructor (line 423).
`test_ref_moving_between_reads_retries` asserts `"lodge/attachments/d-aaaaaa/0.txt" in store.files` (`tests/app/test_writes_retry.py:43-48`), and over the SQLite store that path is in `Tree.attachments`, not `files` (line 392); "`files()` reads the inner store's current files" (line 427) is ambiguous.
Failure: a builder reads `files()` as `trees()[0].files`, and the carried assertion fails, or is weakened.
Fix: state `new Interleaved(inner, during, drafts)` and that `files()` gives the tree's files together with `attachmentTexts()`.

### M-5 · Minor · probe 7's seven byte strings miss a decoder that swallows the byte after a broken sequence

Handle: `decode_utf8_like_surrogateescape` (line 374) runs probe 7's cases only; Python gives `e2c2a9` as U+DCE2 U+00A9, `e28241` as U+DCE2 U+DC82 `A`, and `f09f41` as U+DCF0 U+DC9F `A` (run here with `uv run --frozen`), where a decoder that escapes a whole maximal run, or the next byte, differs; plan 4's `decodeStored` already tests 20 edge strings (its plan line 138).
Failure: a decoder that escapes `e2 c2` together passes all seven cases and turns a valid `©` after a stray lead byte into two escapes, so a file's text and its `contentHash` differ from lodge 0.2's.
Fix: add those three cases, or reuse plan 4's 20 cases, since both plans port one codec (d-0q54zn, d-ryss91).

### M-6 · Minor · a port of `threads.write` named `write` trips the call rule

Handle: `lodge.py` delegates to `threads.write` (`src/lodge/app/lodge.py:77`); plan 1's call rule reports any call whose name is in `writes`, `write` included, in every package but `git` (`ts/tests/structure/calls.ts` at `origin/server-core`, the `writes` set and `report(node, "file writing outside git")`).
Failure: Task 4's builder ports the function as `write`, and `calls.test.ts` fails with "file writing outside git" on `ts/src/app/lodge.ts`.
Fix: name the TypeScript function in Task 4 (`writeMessage`, say).

### M-7 · Minor · `path` is a `text` column, which corrupts a lone surrogate in a path

Handle: plan line 171 (`path text`) and line 360 (`files(… path text not null …)`); probe 1 (`lone_low differs: 61 30062`); lodge 0.2 decodes paths with `surrogateescape` (`src/lodge/gitstore/trees.py:32`), so a 0.2 store's file with a non-UTF-8 name reaches plan 4's import as a path holding U+DCxx.
Failure: the path is stored as a different string, joined with the next character, so the import does not round-trip and the export writes another name.
Fix: `SqliteStore.publish` refuses a path holding any surrogate (`LodgeError("<path>: …")`), with a test; or keep paths as `blob`s too.

### M-8 · Minor · creating a project or a member is a read and then a write, which fails as `database is locked` across two connections

Handle: plan line 397 and 399 (`create` "in one transaction refuses an existing project with `Conflict`", `addMember` "refuses a member already there"); probe 4 (a deferred transaction that reads, lets the other connection commit, then writes fails with `database is locked`); plan 3 maps a racing create's `Conflict` to 409 (its plan line 360).
Failure: two server processes, as Task 8's test stands for, create one project at once; one gets an untyped SQLite error, answered as a 500, not `Conflict`.
Fix: open each with a write as its first statement (`insert into heads … on conflict do nothing` and a row count, as the compare-and-set does), or say that one process holds the file.

### M-9 · Minor · no test that one person's add of another person's decision is held

Handle: the rule "a person other than the actor" (line 540); the tests (line 552) cover an agent's add, a person's own add, and approval by `bo`, not an add by `bo` of `ada`'s decision.
Failure: an implementation that holds only agents' adds passes every listed test, and `bo` writes `ada`'s decision as current.
Fix: add `another_persons_add_is_held` (actor `bo`, `decided_by: ada`: `HELD`, `awaits` `ada`).

### M-10 · Minor · the order of Tasks 9 and 11 is open while both edit the store tests

Handle: Task 11 edits "every test that builds a `Lodge` without `wired` (`ts/tests/store/*.test.ts`)" (line 511) and waits for 6, 8, and 10, not 9 (line 192); Task 9 creates `checked-writes.test.ts` and `seed.ts` building `Lodge`s (lines 442 to 462); neither task is in a lane.
Failure: run side by side, Task 9's new tests construct `Lodge` with four arguments and break when Task 11 makes the actor required; Task 8's and Task 9's projects name no owner or actor, so after Task 12 an add of a `decided_by: author` draft by an unspecified actor may be held.
Fix: make Task 11 wait for 9, and say in Tasks 8 and 9 that the project is created with owner `author` and the `Lodge`s act as `person("author")` once Task 11 lands, as `wired` does.

## Alignment with plans 3 and 4 (for the alignment round, not blocking here)

- Plan 3 at `origin/server-api` 3e4c29c already approves by the hold's number (`approve(project, seq)`, its plan line 410) and builds on `Projects` (its line 306), so the planner report's first two alignment items are out of date; plan 3 adds `settings` to `Projects.create`, `names()`, and `settings()` (its line 306 to 320) and puts them in plan 2's `project` event body.
- Plan 3's account events carry `project` = the empty text (its line 313); plan 2's `applyEvent` "sets `heads.rev` to the row's `seq` for every kind" (plan line 369), which must be an update and never an upsert, or the empty project gains a `heads` row.
- Plan 3's `handEdit` stands for lodge 0.2's hand edits through `publish` (its line 494), which on one state flags nothing for checks 4 to 6 (I-8).
- Plan 3 passes a thread message's `by` from the request (its lines 185 to 187); see I-5.
- Plan 4 keeps thread messages `by: author` while mapping `decided_by: author` to the owner (its d-bh93bn, line 43 and 287); with plan 2's people (the members, Task 10 rows 7 and 8, Task 11's `_message`), `author` is then not a person, so each imported author message's minute `when` fails `read_stamp` and the thread is a check 1 problem; plan 4's IMP-1 question to the author (its line 53) touches the same pull between design lines 78 and 284.
- Plan 4 still says the import writes "through plan 2's check on every write" (its line 352), which d-pprhpz corrected.
- Plan 4 names the codec `decodeStored` and `encodeStored` (its line 129) where plan 2 has `decodeUtf8` and `encodeUtf8`; both put them in `text.ts`, so two lanes would write one function twice.

## The decisions against the design

- d-59q4jc, d-ae1vn5, d-vd3175, d-rp74dr, and d-wx7d0f hold against the design and the code they cite.
- d-wje1cn holds: probes 1 to 5 and 8 reproduce as `probes.md` quotes them; a further probe of six processes, 300 compare-and-set publishes each on one WAL file (`busy_timeout` 5000), gave 1,497 events, `heads.rev` 1,497, and no error, so no publish was lost or doubled.
- d-t7er56's lanes do not follow the import graph in two places (I-2, I-9).
- d-kj59bz counts members as deciding people against design line 74 (I-6), and its name space meets agent roles (I-3).
- d-znagqe's rule matches SRV-2 and design line 75; its approval races (I-1).
- d-4spcem matches design line 77; clearing by replacement as well as confirmation is lodge 0.2's `_cleared`, read per person, which the design does not forbid.
- d-fv20kp holds for `add`, the thread writes, confirmations, and approvals, each of which runs `check_change` on the state its compare-and-set publishes onto (`src/lodge/app/writes.py:96`, `src/lodge/app/threads.py:89`); d-pprhpz's cost if wrong is false (I-8).

## Coverage of the requirements

- The events table, append-only by triggers, and `rebuild` with one `applyEvent`: Task 7a (`events_are_append_only`, `rebuild_derives_the_tables_from_raw_events`) and Task 7b (`rebuild_gives_the_same_tables`).
- A file's bytes exactly: Task 7b (`file_bytes_survive_exactly`, `lone_surrogate_outside_the_escapes_is_refused`) and Task 7a's codec tests (M-5).
- `app` at parity: Tasks 2 to 6 carry every `tests/app/` file the parity table gives plan 2, `test_thread_fix_paths.py`'s two command tests left to plan 3 (d-rp74dr); `test_reads_published.py` and `test_writes_retry.py` changed in Task 9, and `test_concurrent.py` in Task 8, each keeping every Python name under Task 9's parity rule.
- `decided_by` names a person: Tasks 10 and 11 (I-3, I-4, I-6).
- A person's decision drafted by another waits: Task 12 (I-1, M-9).
- A flag clears only by its person: Task 13.
- The check on every write with `add`'s feedback: Task 9 (`a_refused_add_carries_its_feedback`, `every_write_is_checked_against_the_state_it_lands_on`); `publish` itself checks nothing (I-8).

## Not verified

- Kysely 0.29.7's publication date (plan 1's probe 11); no network lookup was made.
- How dependency-cruiser resolves `bun:sqlite` under `not-to-unresolvable`; plan 1's `sqlite-confinement` rule assumes it does.

## Files read

- The plan, its ledger, `planner-brief.md`, `planner-report.md`, `probes.md`, and every file in `probes/`.
- The server design; plan 1's Global Constraints, Calls made, Review Focus, "The rest of build step 1", "Settled for the later plans", and the parity table (lines 1 to 276).
- `src/lodge/app/*.py` but `reads.py`; `src/lodge/core/snapshot.py` (lines 1 to 80), `check_state.py` (lines 110 to 150), `check_immutable.py` (lines 15 to 30), `threads.py` (lines 80 to 120), `feedback.py` (lines 75 to 110), `views.py` (lines 190 to 212), `fileformat.py`'s `content_hash`; `src/lodge/gitstore/plumbing.py` and `trees.py`.
- `tests/app/fakes.py`, `support.py`, `conftest.py`, `test_writes_retry.py`, `test_reads_published.py`, `test_thread_fix_paths.py`, parts of `test_writes.py` and `test_writes_dates.py`, the import lines and operation calls of every `tests/app/test_*.py`; `tests/gitstore/test_concurrent.py`.
- At `origin/server-core`: `ts/src/core/index.ts`, the exports of `snapshot.ts`, `stamps.ts`, `text.ts`, `model.ts`, `threads.ts`, `confirmation.ts`, `derive.ts`, `derive-review.ts`, `fileformat.ts`'s `contentHash`, `.dependency-cruiser.cjs`, `tests/structure/calls.ts`, `tests/structure/table.ts`, `tests/parity.test.ts`, and three rows of `tests/parity.json`.
- The twelve decisions with `--reasoning`; plan 3 and plan 4 by `grep` only.

Not read: `src/lodge/app/reads.py`, the rest of `src/lodge/core` and its tests, plan 1's tasks, plan 1's ledger, `tests/app/test_reads.py`, `test_confirm.py`, and `test_thread_ops.py` in full, and plans 3 and 4 beyond the lines cited.

## Summary

0 Blocking, 9 Important, 10 Minor.
