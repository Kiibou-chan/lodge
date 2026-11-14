# Plan recheck 4: plan 2, the events store and the operations

Rechecker, on `server-store`, fix round a035344..4b1c486, against R3-1 to R3-5 of `plan-recheck-3.md`, the answers in `plan-fix-4.md`, and the coordinator's ruling on R3-1 (a held message changes no thread's waiting).
Line numbers are of the plan at 4b1c486 (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`).
No probe was run.
Status: done.

## Findings of recheck 3

- R3-1 · Resolved, per the ruling.
  The held-reply clause is gone: waiting stays Task 11's, by the last published message only, and a held message reaches its person through `held()` (line 651); no other text of the plan or ledger keeps the clause (`git grep` for "open held" and "nothing is held for it" at 4b1c486 finds none).
  Both directions are pinned through `threadsWaiting` and `waitingAll` (line 654): `the_thread_still_waits_for_the_person` (last published message `reviewer`'s: `forAuthor` with the relay pending, `forAgent` once `ada` approves) and `a_persons_thread_still_waits_for_an_agent` (last published message `ada`'s: `forAgent` with the relay pending and after approval).
  The second test fails under the dropped clause, since the clause would move that thread to `forAuthor` while the relay is pending, so the ruling is observed and not only stated.
- R3-2 · Resolved for two of three; the third mutation does not reach its test (Minor R4-1 below).
  Step 2 names the three tests as green on arrival with a mutation each (line 656).
  `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it`: with the hold before the `where` refusal, the agent's reply is held and answers `HELD`, so the expected `LodgeError` is not thrown and the test fails.
  `a_relay_to_a_closed_thread_is_refused`: with the hold before the closed-thread refusal (`src/lodge/app/threads.py:75-76`), the reply is held, `held()` lists it, and the test's "nothing held" fails.
- R3-3 · Resolved, by falling away with R3-1: `waitingIn` keeps the state alone, Task 12c's Files no longer change it (line 639), and both waiting tests assert `waitingAll`.
- R3-4 · Resolved: `sqlite-store.test.ts` holds eight tests and `sqlite-store-refusals.test.ts` five, each once, together the thirteen of the old list (line 434).
- R3-5 · Resolved: Calls made 10 (line 66) and line 190 cite d-n9nm8h and its change check from an empty state; the doubled comma is gone (line 547).

## New findings

### R4-1 · Minor · the mutation for `one_person_cannot_write_as_another` leaves that test green

Handle: line 656 ("the hold placed before the other-person `Forbidden`"); the test's actor is the person `bo` (line 654), while Task 12c holds only an agent's message under a person's name (line 647) and Task 11 refuses a person writing as another (line 564).
Failure: the hold branch is guarded by the actor being an agent, so moving it before the `Forbidden` changes nothing for `bo`'s call, which is still refused, and the builder's report shows a mutation that never turned the test red; the test is then never seen to pin that a person's write under another's name is refused rather than held.
Fix: name a mutation that reaches `bo`: the other-person `Forbidden` replaced by a hold, so any actor other than the named person is held.

## Preflight rows marked RECHECK-R3, re-run at 4b1c486

| Row | Pair | At 4b1c486 |
|---|---|---|
| P19 | 9 -> 11 | match: Task 11's Files give every `Lodge` of Tasks 7b to 9's store tests `person("author")` (line 554), and Task 12c's store test builds on `seeded`, owner `author` |
| P20 | 3, 4 -> 11 | match: `state.ts` in Task 11's Files, `Wiring` gaining `actor` (line 554) |
| P21 | 10 -> 11 | match: `confirmationDraft(…, person = "author")` is trailing (line 526 of Task 10), and `confirm` passes the actor's name |
| P24 | 11 -> 12a | match: `fakes.ts` in Task 12a's Files, the holds added beside Task 11's `people` option |
| P25 | 12a -> 12b | match: `HeldDraft = HeldAdd \| HeldMessage` (line 125), `Held` with `seq` and `at`, and `at` a column of `held` (line 589) |
| P26 | 12b -> 2 | match: `ports.test.ts` in Task 12b (line 612) for `added()` |
| P28 | 13 -> 11 | match: unchanged; Task 13 keeps the first words `this decision will wait for` |
| P33 | 6 -> 14 | match: the front-door list names `HeldAdd`, `HeldMessage`, `Held`, and `Approved`, exported by Tasks 12a and 12b |
| Task 11 | itself | match: Files hold `state.ts`; `_message` refuses another person only (line 564), an agent's relay being Task 12c's |
| Task 12a | itself | match: Files cover the port's union, both stores, `interleaving.ts`, the migration with `at`, and `database.test.ts`; `a_held_message_round_trips` tests the union |
| Task 12b | itself | match: `awaits.ts` and `held.ts` created, `held.ts → writes.ts → awaits.ts`; `approve` answers `Approved` and refuses a `HeldMessage` with the interim `LodgeError` |

## New preflight rows for Task 12c

| Row | Pair | Finding |
|---|---|---|
| P34 | 12a -> 12c | match: the `HeldMessage` Task 12c builds (`person`, the agent's `actorText` as `by`, `operation`, `ref`, `raises`, the cleaned text, `where`, `when`; line 647) has the fields the port declares (lines 131 to 135); a `close` without text is lodge 0.2's `text or ""` (`src/lodge/app/lodge.py:90-100`), which fits `text: string \| null` |
| P35 | 12b -> 12c | match: Task 12c fills `approve`'s `message` branch in `held.ts` and removes 12b's interim refusal (Step 3); `Approved`'s `{ kind: "message", written }` is declared in 12b |
| P36 | 11 -> 12c | match: Task 12c reads the actor from Task 11's `Wiring`; it holds after lodge 0.2's refusals and leaves Task 11's other-person `Forbidden` as it is (lines 647 and 648) |
| P37 | 4 -> 12c | match: `threads.ts` (Task 4) gains the hold; `held.ts → threads.ts → writes.ts → awaits.ts`, `threads.ts` reaching `hold` through the port, so no cycle (line 646) |
| P38 | 9 -> 12c | match: `store/held-messages.test.ts` builds on `seeded` (Task 9), a declared wait through 12b |
| P39 | 12c -> results | match: `Written` gains `awaits` and `held`, `written()` fills `null`, and `ports.test.ts` checks them (line 640) |
| P40 | 12c -> 14 | match: Task 14's checks need nothing of 12c beyond the front door and the passing tests; its rebuild step does not name a held message, which Task 12a's `a_held_message_round_trips` and `holds_rebuild` cover |
| Task 12c | itself | match but R4-1: Files, waits, and thirteen tests across three files agree; Step 2 names the three green-on-arrival tests |

## Counts

Recheck 3's findings: 5 of 5 resolved, R3-2 with one of its three mutations ill-aimed (R4-1).
Preflight: 11 RECHECK-R3 rows re-run, all match; 8 rows added for Task 12c, all match.
New: 0 Blocking, 0 Important, 1 Minor (R4-1).
