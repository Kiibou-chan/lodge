# Plan fix round 3: plan 2, the events store and the operations

Planner, fix round 3, on `server-store` from fbc31e4, applying the author's decision d-2v8vtk (her answer C to STORE-1, replacing d-x6vaw8) and the mismatches of the preflight scan (`preflight.md`).
Status: done.

## The author's decision d-2v8vtk

- One hold machinery: `HeldDraft` becomes the union `HeldAdd | HeldMessage`, told apart by `kind` (Interfaces for plans 3 and 4, Task 12a); the stores keep a hold's body as JSON and read only its `person`, so a relayed message is held, listed by `held()`, approved, and declined as an add is, and d-thvvzx's settle-once covers both (`a_held_message_round_trips` in Task 12a).
- A `HeldMessage` holds the person, the relaying agent's `actorText`, the operation (`ask`, `reply`, or `close`), the ref or thread, `raises`, the text, `where`, and `when`.
- `approve(seq)` answers `Approved`: `{ kind: "add", added }` for a held add (Task 12b) and `{ kind: "message", written }` for a held message (Task 12c), which runs the thread write as the person with the held `where` and `when`, mints an asked thread's ID at the approval, and publishes the thread file and the `approved` event in one transaction; until Task 12c lands, Task 12b's `approve` of a held message throws a `LodgeError` that Task 12c removes.
- Writing (Task 12c): an agent's `ask`, `reply`, or `close` under a person's name passes lodge 0.2's refusals first (so a relay without `where` is refused with its words), is checked as a published message would be, and is then held, answering `Written` with `outcome` `HELD`, `awaits`, and `held`; a person's own message is published at once, and one person under another's name is `Forbidden` (Task 11, whose agent refusal and `an_agent_cannot_write_as_a_person` test are removed).
- Waiting (Task 12c): a held message is not the thread's last message until approved; a thread waits for a person when its last published message is not a person's or an open held `reply` or `close` names it, and for an agent only otherwise; a held `ask` has no thread and is listed by `held()` only.
- Tests, test-first in Task 12c: `an_agent_relaying_a_persons_words_is_held`, `the_thread_still_waits_for_the_person`, `the_person_approves_and_the_message_is_published` (its `where` and `when` kept, the thread moving to `forAgent`), `a_relayed_question_mints_its_thread_at_approval`, `decline_publishes_nothing`, `a_persons_own_message_is_published_at_once`, `one_person_cannot_write_as_another`, `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it`, `a_relay_to_a_closed_thread_is_refused`, `another_person_or_an_agent_cannot_approve_a_message`, `approval_after_the_thread_closed_leaves_it_held`, and over the SQLite store `a_relayed_message_lands_with_its_approval`.
- Citations: every citation of d-x6vaw8 in the plan and the ledger now cites d-2v8vtk; STORE-1 is marked answered in `questions.md`.
- Lanes: Task 12c waits for 12b; the imports run `held.ts → threads.ts → writes.ts → awaits.ts` and `held.ts → writes.ts`, `threads.ts` reaching the holds through the `Store` port only, so no module imports `held.ts` but `lodge.ts` and plan 1's `no-circular` rule holds.

## Preflight

1. `ts/scripts/differential.ts:41`, a `Tree` literal: fixed in Task 10's Files (it becomes `load(tree({ … }))`) and Step 3, whose grep now covers `ts/scripts` and `load({`.
2. Task 11's Files omitted `state.ts`: fixed; `Wiring` there gains `actor`, which `threads.ts` and `confirm.ts` read.
3. `lodge.ts` "holds `Wiring`": fixed in Task 3: `Wiring` is declared in `state.ts`, and `lodge.ts` holds a value of it, so no cycle.
4. `fakes.ts` leaves knip's `entry` in Task 3, whose tests read all four names; fixed in the exports table and Tasks 3 and 4.
5. The attachment assertion is `tests/app/test_writes_retry.py:67`; fixed in Task 8.
6. The `START.replace(microsecond=999_999)` reading moves to Task 3, where `add_fills_id_and_date_from_ports` uses it.
7. Task 4's ordering sentence now names `reads.py`'s `_newest_first` only, descending on both instant and ID, and gives `writes-dates.test.ts`'s `NEWEST` as `{ epochMs: instant(FIRST.date), offsetMinutes: 60 }`.
8. The `held` table gains `at`, copied from the `held` event by `applyEvent`, so `held()` reads one table (Task 12a).
9. Size: Task 7b splits `sqlite-store.test.ts` and `sqlite-store-refusals.test.ts`, Task 12b `held.test.ts` and `held-approve.test.ts`, Task 12c `held-messages.test.ts` and `held-messages-approve.test.ts`, the tests named per file; Task 13 creates `derive-flags.ts` for the per-person flags, since `derive.ts` is 238 lines.
10. The lanes paragraph says Tasks 2 and 7a meet a textual conflict in `ts/package.json`'s `imports` and `ts/knip.json`'s `entry`, which the integrator resolves by keeping both sides.
11. Tasks 8 and 9 no longer list `parity.json` with nothing to change; Task 14 prints each `planned` row with its plan instead of counting them.
12. Tasks 12b and 12c list `ts/tests/app/ports.test.ts`, which checks `added()`'s and `written()`'s new defaults.

## For plans 3 and 4

Changed or new names they consume:

- `HeldDraft` is now `HeldAdd | HeldMessage` with a `kind` field; `HeldAdd` holds the fields `HeldDraft` had; `HeldMessage` holds `person`, `by` (the relaying agent), `operation` (`ask`, `reply`, or `close`), `ref`, `raises`, `text`, `where`, and `when`; `Held` is `HeldDraft & { seq, at }` (Task 12a).
- `Lodge.approve(seq)` answers `Approved`, `{ kind: "add", added: Added }` or `{ kind: "message", written: Written }`, instead of `Added` (Tasks 12b and 12c).
- `Written` gains `awaits: string | null` and `held: number | null`, and a held message answers `Written` with `outcome` `AddOutcome.HELD` (`"held for approval"`) (Task 12c).
- The refusals' words: an unknown or settled hold is `NotFound("nothing is held under number <seq>")`, and another actor's approval or decline `Forbidden("only <person> approves this; nothing was written")`, for both kinds.
- `threadsWaiting` and `waitingAll`: a thread with an open held `reply` or `close` waits for the person (`forAuthor`) until that message is approved.
- Plan 3's approval page lists `held()`, which now returns held messages beside held adds; it shows each by `kind`, a message with its thread or record, text, `where`, and `when`, and its approve and decline answer as for an add.
- Plan 3's carried command tests: `author_words_are_recorded_exactly` (`tests/e2e/test_threads.py:106`) and `waiting_groups_threads` (`tests/e2e/test_waiting.py:41`) write `--by author` with where and when through the agent token, which is now held, not `Forbidden`: each approves the held message through the person's session before its assertions, so the first finds the words recorded exactly and the second finds the author's question in the agent's list; `author_message_needs_where_and_when_exit_2` keeps lodge 0.2's message, since that refusal comes first.
- Plan 4: its export wrapper passes `Store.hold`, `held`, and `decline` on unchanged, whatever the kind; the `held` table gains an `at` column in `MIGRATIONS[1]`, so a later plan's migration is `MIGRATIONS[2]` as before.
