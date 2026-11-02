# Plan fix round 4: plan 2, the events store and the operations

Planner, fix round 4, on `server-store` from a035344, answering `plan-recheck-3.md` (0 Blocking, 1 Important, 4 Minor) with the coordinator's ruling on R3-1.
Status: done.

## Findings

- R3-1 (Important, the held-reply waiting clause goes beyond d-2v8vtk): fixed by the coordinator's ruling: the clause is dropped from Task 12c, so a held message changes no thread's waiting; waiting is decided by the last published message only, as Task 11 has it, and a held message reaches its person through `held()`; `the_thread_still_waits_for_the_person` now starts from a thread whose last published message is `reviewer`'s (in `forAuthor` with the relay pending, in `forAgent` once `ada` approves), and the new `a_persons_thread_still_waits_for_an_agent` from one whose last published message is `ada`'s (in `forAgent` with the relay pending, and still there once the approved relay is its last message); both check `threadsWaiting` and `waitingAll`.
- R3-2 (three tests green on arrival): fixed in Task 12c's Step 2: `one_person_cannot_write_as_another`, `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it`, and `a_relay_to_a_closed_thread_is_refused` are named as passing on arrival, and each is seen failing after Step 3 against a targeted mutation listed as a table: the hold placed before the other-person `Forbidden`, before the `where` refusal, and before the closed-thread refusal.
- R3-3 (`reads.ts`'s `waitingAll` and `waitingIn`'s parameter): falls away with R3-1: `waitingIn` keeps taking the state alone, so neither `reads.ts` nor `threads.ts`'s waiting changes in Task 12c, whose Files no longer say `waitingIn` reads the holds; the two waiting tests assert `waitingAll` beside `threadsWaiting`.
- R3-4 (Task 7b's split lists the five moved tests twice): fixed: Task 7b's Step 1 lists eight tests in `sqlite-store.test.ts` and the five refusal tests in `sqlite-store-refusals.test.ts`, each once.
- R3-5 (d-n9nm8h): fixed at Calls made 10 and in "Interfaces for plans 3 and 4": the import runs the change check from an empty state with its store's settings and then the project's (d-n9nm8h, narrowing d-j28rp0); the doubled comma in Task 10's Step 3 is mended.

## For plans 3 and 4

One rule they consume changed since `plan-fix-3.md`; the names are unchanged.

- `threadsWaiting` and `waitingAll`: a held message changes no thread's waiting; a thread waits for a person or an agent by its last published message only, as before; a held relay is listed by `held()` and becomes the thread's last message when approved. This replaces `plan-fix-3.md`'s line that a thread with an open held `reply` or `close` waits for the person.
- Plan 3's carried tests: `waiting_groups_threads` still approves the relayed author question through the person's session before its assertions, since a held `ask` makes no thread until it is approved; `author_words_are_recorded_exactly` likewise.
- Plan 4: the import's check is d-n9nm8h's (the change check from an empty state), which plan 2 now cites; nothing plan 4 consumes from plan 2 changed.
