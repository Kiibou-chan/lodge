# Plan recheck 3: plan 2, the events store and the operations

Rechecker, on `server-store`, fix round 5af878e..a035344, against the author's decision d-2v8vtk, `plan-fix-3.md`, and the twelve mismatches of `preflight.md`.
Line numbers are of the plan at a035344 (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`).
Python handles are of `server-store`; plan 1's of `/var/tmp/lodge-server-core/ts`.
No probe was run.
Status: done.

## d-2v8vtk, as Task 12c applies it

- Held relay · Implemented.
  An agent's `ask`, `reply`, or `close` under a person's name is checked and then given to `store.hold` as a `HeldMessage`, answering `Written` with `HELD` (line 647); `an_agent_relaying_a_persons_words_is_held` pins it (line 654).
- The thread keeps waiting for the person · Implemented for the decision's case, with one rule beyond it (Important R3-1 below).
  `the_thread_still_waits_for_the_person` pins that a relay leaves the thread in `forAuthor` with `reviewer`'s message last (line 654).
- A person under their own name is not held · Implemented (line 648), pinned by `a_persons_own_message_is_published_at_once`.
- Another person's name is refused · Implemented in Task 11 (line 564), pinned by `a_person_writes_only_as_themselves` (Task 11) and `one_person_cannot_write_as_another` (Task 12c).
- An agent relay without `where` is refused as lodge 0.2 refuses it · Implemented: lodge 0.2's refusals come first (line 647; `src/lodge/app/threads.py:32-34`), pinned by `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it`.
- Approval and decline · Implemented on the one hold machinery: `approve` runs the thread write as the person with the held `where` and `when` and publishes with `approves` (line 649), `decline` is Task 12b's for both kinds (line 650); the SQLite path is pinned by `a_relayed_message_lands_with_its_approval`.
- Every citation of d-x6vaw8 is gone from the plan and the ledger (`grep` gives none), and `questions.md` marks STORE-1 answered.

## Types, waits, and imports

- `HeldDraft = HeldAdd | HeldMessage` with `kind`, `Held = HeldDraft & { seq, at }`, and `Approved` (lines 125 to 137) agree with Task 12a's Files and Produces, Task 12b's `approve` answering `{ kind: "add", added }`, Task 12c's `{ kind: "message", written }`, and Task 6's front-door list, which now names `HeldAdd`, `HeldMessage`, and `Approved`.
- `Written` gains `awaits` and `held`, filled `null` by `written()`, in Task 12c, with `ports.test.ts` in its Files; `Added`'s in Task 12b likewise.
- Task 11 now refuses only another person (line 564) and leaves an agent's relay published until Task 12c; Task 12b's interim `LodgeError` for a `HeldMessage` is removed by Task 12c's Step 3; the two agree.
- `MIGRATIONS[1]` gains `at text not null`, copied from the `held` event (line 589), and `held()` reads the row.
- Task 12c waits for 12b, and its tests use `held.ts` (12b), `threads.ts` (Task 4), the port (12a), and `seeded` (Task 9), all among its waits.
- Imports: `held.ts → threads.ts → writes.ts → awaits.ts` and `held.ts → writes.ts` (lines 222 and 646); `threads.ts` reaches the holds through the `Store` port, and lodge 0.2's `threads.py` already imports from `writes.py` (`mint_unused`), so no edge runs back to `held.ts` and there is no cycle.
  The new waiting rule also touches `reads.ts`, which this list does not name (Minor R3-3).

## The preflight mismatches

1. Resolved: Task 10 lists `ts/scripts/differential.ts` and its line 41 becomes `load(tree({ … }))` (line 514); the Step 3 grep covers `ts/scripts` and `load({` (line 547), with a typo noted in R3-5.
2. Resolved: Task 11 lists `state.ts`, where `Wiring` gains `actor` (line 554).
3. Resolved: `Wiring` is declared in `state.ts` and `lodge.ts` holds a value of it (line 295).
4. Resolved: `fakes.ts` leaves `entry` in Task 3 (line 43, Task 3's Files and Step 3, Task 4's Files and Step 3 now naming three files).
5. Resolved: `tests/app/test_writes_retry.py:67` (line 467), which is the assertion.
6. Resolved: the `START.replace` rule is in Task 3 (line 297).
7. Resolved: `_newest_first` sorts descending on both the instant and the ID (line 317), as `src/lodge/app/reads.py:126-130` does with `reverse=True`, and `NEWEST` is given with `offsetMinutes` 60.
8. Resolved (line 589).
9. Resolved for Tasks 12b, 12c, and 13 (`held-approve.test.ts`, `held-messages-approve.test.ts`, `derive-flags.ts`); Task 7b's split is written wrongly, Minor R3-4.
10. Resolved (line 218).
11. Resolved: Tasks 8 and 9 no longer list `parity.json`; Task 14's `bun -e` reads `status` and `plan` (line 688), the field names `ts/tests/parity.json` uses.
12. Resolved: `ports.test.ts` in Tasks 12b (line 612) and 12c (line 640).

## New findings

### R3-1 · Important · the held-reply waiting rule moves a thread to `forAuthor` that waited for an agent, beyond "as before", and no test pins it

Handle: line 651 (a thread waits for a person "when its last published message is not a person's or when an open `HeldMessage` of a `reply` or `close` names it", and for an agent "only when its last published message is a person's and nothing is held for it"); d-2v8vtk ("the thread waits for that person as before, until that person, signed in, approves it"); the only waiting test, `the_thread_still_waits_for_the_person` (line 654), starts from a thread whose last message is `reviewer`'s, so it is in `forAuthor` with or without the second clause.
Failure: `ada` asks a question, so the thread waits for an agent (`forAgent`, `src/lodge/app/threads.py:139-145` read per person); a coordinator relays a follow-up line of hers from a chat; under line 651 the thread leaves `forAgent` for `forAuthor`, so `lodge waiting` no longer shows the agents her unanswered question, which the decision's "as before" does not ask for; and a builder who leaves the second clause out passes every listed test, so the rule ships or vanishes unobserved.
Fix: drop the second clause, so waiting follows the published messages as lodge 0.2's does and a held relay surfaces through `held()`, which keeps "as before" exactly; or, if the planner holds that a pending relay should move the thread, record that as a decision for the author, since it reads her ruling further than she wrote it, and add a test whose last published message is a person's.

### R3-2 · Minor · three of Task 12c's tests pass on arrival, and Step 2 says every new test fails

Handle: line 656 ("expected: the new tests FAIL"); `one_person_cannot_write_as_another` is Task 11's refusal (line 564), and `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it` and `a_relay_to_a_closed_thread_is_refused` are lodge 0.2's (`src/lodge/app/threads.py:32-34` and `:75-76`), each asserting nothing held, which is true on Task 12b's code since nothing holds a message yet; the Global Constraints ask for a targeted mutation for a test over code an earlier task wrote (line 24).
Failure: the builder sees three green tests at Step 2 and either reports a red that never happened or weakens nothing and moves on, so the ordering these tests exist for (refuse before holding) is never seen to matter.
Fix: name the three as green on arrival and give each a targeted mutation after Step 3, listed as a table: the hold placed before the `where` refusal, before the closed-thread refusal, and before the other-person `Forbidden`.

### R3-3 · Minor · Task 12c changes `waitingIn` but not `reads.ts`, whose `waitingAll` calls it with the state alone

Handle: line 639 (Files: `threads.ts`, `held.ts`, `results.ts`); line 651 ("Waiting (`waitingIn`, `threadsWaiting`, `waitingAll`) … the held messages are read once through `store.held()` beside the state"); lodge 0.2's `waiting_all` calls `threads.waiting_in(state)` (`src/lodge/app/reads.py:56-59`), and `waiting_in` takes the state only (`src/lodge/app/threads.py:139`).
Failure: `waitingIn` cannot reach `store.held()` from a `State`, so it gains a parameter, and `reads.ts`'s call stops compiling in a file the brief does not list; and no test calls `waitingAll` with a held message, so a builder who threads the holds into `threadsWaiting` only leaves `waitingAll` disagreeing with it.
Fix: list `ts/src/app/reads.ts` in Task 12c's Files, say `waitingIn(state, held)`, and assert `waitingAll`'s threads in `the_thread_still_waits_for_the_person` too.

### R3-4 · Minor · Task 7b's split lists the five moved tests in both files

Handle: line 434: "the second holds `lone_surrogate_outside_the_escapes_is_refused`, `path_outside_lodge_is_refused`, `a_path_holding_a_surrogate_is_refused`, `an_attachment_is_never_overwritten`, and `a_published_decision_is_never_rewritten`, and the first the rest:", followed by every test of the old file, those five included.
Failure: a literal port writes the five titles twice, the first file keeps its size, and the split does not do what preflight 9 asked.
Fix: cut the five from the list after "the first the rest:".

### R3-5 · Minor · d-n9nm8h is in this range but the plan still says the import runs lodge 0.2's state check

Handle: d-n9nm8h (coordinator, 5307e56): the import "runs the change check from an empty state with the store's settings and then with the project's", in place of d-j28rp0's state check; the plan's line 190 ("checks that store with lodge 0.2's state check first") and Calls made 10 (line 66, "after its own state check") cite neither the new wording nor d-n9nm8h.
Failure: a builder or plan 4's alignment reads the superseded check from plan 2's text.
Fix: at lines 66 and 190, say the import runs the change check from an empty state (d-n9nm8h, narrowing d-j28rp0); also mend the doubled comma at line 547 ("no `Tree` literal,,").

## Counts

d-2v8vtk: implemented as stated, but for one waiting clause beyond it (R3-1).
Preflight: 12 of 12 resolved (number 9 with R3-4).
New: 0 Blocking, 1 Important (R3-1), 4 Minor (R3-2 to R3-5).
