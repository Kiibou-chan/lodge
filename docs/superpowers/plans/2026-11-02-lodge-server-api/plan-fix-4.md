# Plan fix round 4: plan 3, the API, sign-in, and the command

Planner, fix round 4, on `server-api` from 4f91d77, answering `plan-recheck-2.md`'s N-7 and the author's answer C to plan 2's STORE-1 (d-2v8vtk), as plan 2's fix round 3 carries it (`origin/server-store` a035344, Task 12c, `plan-fix-3.md`, "For plans 3 and 4").
Status: done; N-7 fixed, the STORE-1 alignment applied; one ruling, d-4qv0xb, replacing d-81ps01.

## N-7

- Task 6's `held`: an entry's draft is read with `recordFromDraft(draft, id, held.at, area)`, `area` the draft's own `area` when its header holds a string and otherwise the placeholder `held`, which with the placeholder ID and the date never reaches the answer; `held_shows_the_drafts_as_core_reads_them` gains a second hold whose entry draft is `lodge draft` of the current entry (with `base`, no `area`), answered with its `title` and `text` and no `problem`.

## STORE-1, answered C (d-2v8vtk)

- Ruling d-4qv0xb replaces d-81ps01: the hand-edit half is unchanged; a relayed `--by author` message is held, and the carried test asserts the held line and approves it through the person's session, reading the thread's ID from the approval; Calls made 15 and every citation now name d-4qv0xb.
- Global Constraints, Porting: d-bwb1tt's third substitution covers an add or a thread message held for a person; the refusal clause for relayed messages is gone.
- "Names consumed from plan 2": Task 12c's held relay (`Written` with `HELD`, `awaits`, `held`, provisional ask ID minted at approval), `HeldDraft = HeldAdd | HeldMessage` by `kind`, `Held = HeldDraft & { seq, at }`, `Approved`, the two refusal sentences, and a held message changing no thread's waiting state (the coordinator's ruling on plan 2's recheck R3-1, which drops Task 12c's rule that a held `reply` or `close` makes the thread wait for the person); d-x6vaw8 and STORE-1's interim text removed; "Order and lanes" says Tasks 4 to 9 wait for plan 2's Task 12c.
- Parity: `test_threads.py`'s row names `author_words_are_recorded_exactly`'s held relay as the third substitution; `test_waiting.py`'s row is `ported` again with the same note; the held paragraph covers relayed messages and drops the STORE-1 B sentence.
- Task 5: `agent_cannot_write_as_the_person` becomes `agents_relay_is_held` (200, `held for approval`, `awaits` `ada`, a `held` number, no thread listed).
- Task 6: `held` answers each hold by `kind`, a message as `{seq, at, by, kind, operation, ref, raises, text, where, when}`; `approve` answers `Approved`, 422 on a `CHECK_FAILED` of either kind; new tests `held_lists_a_relayed_message`, `approve_publishes_the_relayed_message`, and `decline_drops_the_relayed_message` (the last asserting `nothing is held under number <seq>`); `approve_makes_the_held_decision_current` expects `kind` `add`.
- Task 7a: `runThread` prints the held line for a held message, exit 0; `TestServer.approve` takes either kind; `asPerson` is gone from `TestServer` and `Project`, since no test writes as the person any more; `waiting_groups_threads` and `author_words_are_recorded_exactly` assert the held line and approve the hold before asserting as Python does; `author_message_needs_where_and_when_exit_2` keeps lodge 0.2's message; the guide's line 24 clause says a message `--by author` waits for the author's approval on the server's page.
- Task 9: the page shows held messages beside held adds by `kind` (operation, record or thread, text, `where`, `when`), each with Approve and Decline.

## For plan 4

Names plan 4 consumes that changed: none of its table's (`Store`, `Projects`, `ApiOptions`, `lodgesOver`, `handler`, the person's operations and their `forbidden` sentence, `Accounts`, `world.ts`, `server.ts`, `Io`, `run`, `parse`, `Command`, `readSettings`, `CliError`, `main.ts`); the person's `approve` operation now answers `Approved` and `held` answers both kinds, and `TestServer` lost `asPerson`, which plan 4 does not use.

## After the coordinator's ruling on plan 2's R3-1

- "Names consumed from plan 2" now says a held message changes no thread's waiting state, which follows the last published message only; no test of this plan asserted the dropped rule, and `waiting_groups_threads` approves the held question before it asserts, as before.
