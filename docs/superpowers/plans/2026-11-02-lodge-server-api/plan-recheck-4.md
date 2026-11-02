# Plan recheck 4: plan 3, the API, sign-in, and the command

Rechecked: fix round 4, `git diff 4f91d77 851ae58` on `server-api` (`cdbf926` and `851ae58`), against `plan-recheck-2.md`'s N-7, `plan-fix-4.md`, d-4qv0xb, and the author's d-2v8vtk as plan 2's Task 12c carries it at `a035344` of `origin/server-store`.
"Plan line N" is a line of `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `851ae58`; "plan 2 line N" a line of `docs/superpowers/plans/2026-11-02-lodge-server-store.md` at `a035344`.

## N-7 · Resolved

Plan line 443: an entry's draft is read with `recordFromDraft(draft, id, held.at, area)`, `area` the draft's own `area` when a string and otherwise the placeholder `held`, and `null` for a decision or an area; the placeholder never reaches the answer.
This matches recheck 3's run at `origin/server-core` 7d5ecbc: any non-null `area` makes an edit draft without `area` read as a `spec` with its title, since `name` throws only when both are set and differ, or both are missing.
Plan line 458 adds a second hold whose entry draft is `lodge draft` of `seed`'s entry once current (with `base`, no `area`), answered with its `title` and `text` and no `problem`, the case that was untested.

## STORE-1's answer C (d-2v8vtk) through the plan

- What the decision states: an agent may relay a person's words with where and when; the message is held until that person, signed in, approves it; a person's own message is not held; one person under another's name is refused (`lodge show d-2v8vtk`, author, quote "C").
  Plan line 120 states all four, with lodge 0.2's refusals first, as plan 2 lines 647-648 have it.
- API: Task 5's `agents_relay_is_held` (plan line 403) answers 200 with `outcome` `held for approval`, `awaits` `ada`, and a `held` number, and lists no thread; Task 6's `held` answers a message hold as `{seq, at, by, kind, operation, ref, raises, text, where, when}` (line 443), which is plan 2's `HeldMessage` (plan 2 lines 130-134) less `person`, the signed-in person; `approve` answers `Approved` with 422 on a `CHECK_FAILED` of either kind; the new tests `held_lists_a_relayed_message`, `approve_publishes_the_relayed_message`, and `decline_drops_the_relayed_message` (line 458) cover listing, approval, and decline.
- Command: `runThread` prints `held for approval by <awaits> as hold <held>; nothing is current until they approve it` and returns 0 for a held message (plan line 497, Task 7a), the line `seed` and the add tests already use.
- Page: Task 9 (plan line 610) shows a held message by `kind` with its operation, the record or thread, its text, `where`, and `when`, each with Approve and Decline.
- Guide: the line 24 clause now says a message `--by author` waits for the author's approval on the server's page; line 26 stays verbatim for `guide_says_waiting_first`.
- The coordinator's ruling (a held message changes no thread's waiting state, which follows the last published message only) is stated at plan line 120; it reads d-2v8vtk's "the thread waits for that person as before" as the state before the relay, which a reply relayed to `reviewer`'s question already gives (its last published message is not a person's).
  Plan 2 at `a035344` still carries the extra clause (plan 2 line 651, "or when an open `HeldMessage` of a `reply` or `close` names it"), which plan 2's round 4 drops by the coordinator's account; no test of plan 3 depends on either reading, since every carried test approves before it asserts waiting.

## Names consumed from plan 2, against `a035344`

- `HeldDraft = HeldAdd | HeldMessage` by `kind`, with the fields plan line 121 lists: plan 2 lines 125-134. Match.
- `Held = HeldDraft & { seq, at }`: plan 2 line 135. Match.
- `Approved`, `{ kind: "add", added } | { kind: "message", written }`: plan 2 line 137; `approve(seq): Promise<Approved>`, plan 2 line 174. Match.
- `Written.awaits` and `Written.held`, filled `null` by `written()`: plan 2 lines 150 and 645. Match.
- The two refusal sentences, `NotFound("nothing is held under number <seq>")` and `Forbidden("only <person> approves this; nothing was written")`: plan 2 line 625 (and 592 for the store's `decline`). Match.
- The held relay's answer (`HELD`, `ids` the thread's ID or a provisional ask ID minted at approval, `awaits`, `held`): plan 2 lines 647 and 649. Match.

## Carried tests

- `waiting_groups_threads` (plan line 543, Task 7a): the author's question exits 0 with the held line, `approve` gives the thread's ID standing for `author.out.split()[-1]`, then the rest as Python asserts (`tests/e2e/test_waiting.py:42-65`: both codes 0, the author's thread under "waiting for an agent", the agent's doubt under "waiting for the author"); approval publishes `author`'s message, so the thread's last published message is a person's and it waits for an agent, as Python's does.
- `author_words_are_recorded_exactly` (plan line 563, Task 7b): the held line, `approve` gives `<q>`, then `thread <q>` and the stored file are asserted as `tests/e2e/test_threads.py:121-129` asserts them; plan 2 line 649 approves with the held `where` and `when`, so `author · 2026-10-31 12:00 · chat` and the exact text hold.
- `author_message_needs_where_and_when_exit_2` keeps lodge 0.2's message, since Task 2's grammar refuses `--by author` without both before any request (plan line 230).
- No other carried test writes `--by author` (`grep -n '"author"' tests/e2e/test_*.py`: only `test_threads.py:51,114` and `test_waiting.py:49`).
- `asPerson` is gone from `TestServer` and `Project`, and nothing in the plan still names it, d-81ps01, d-x6vaw8, or the STORE-1 interim (`grep` at `851ae58`; STORE-1 survives only as the name of the author's answer at plan line 120).

## Parity rows

- `test_waiting.py` is `ported` again with the held-and-approved note (plan line 163), as `test_add_import.py` is `ported` with its held add: d-bwb1tt's third substitution is a port, not a change. Honest.
- `test_threads.py` stays `changed` for its dropped `thread_files_are_staged_not_committed`, and names the held relay as the third substitution (plan line 162). Honest.
- The held paragraph (plan line 168) now covers adds and relayed messages and drops the STORE-1 B sentence.

## d-4qv0xb

Its handles hold: `src/lodge/core/check_state.py:130-136` (check 3), probe 8 (rerun in recheck 1), design line 79, `src/lodge/core/check_change.py:37-41`, d-j28rp0 on `server-store`, and plan 2's Task 12c and `plan-fix-3.md`, "For plans 3 and 4" (line 32 at `a035344`); its cost if wrong ("one line each") is consistent with the tests above.

## Lane waits

"Order and lanes" (plan line 79) has Tasks 4 to 9 wait for plan 2 merged with its Task 12c; the lane table's "plan 2" in Task 4's Needs carries it, and Tasks 5 to 9 wait on Task 4 or later, so every task that names `HeldMessage`, `Approved`, or `Written.held` (5, 6, 7a, 7b, 9) waits for 12c.

## New findings

### N-8 · Minor · `agents_relay_is_held` names no record to ask about

Handle: plan line 403 (`an ask with by: "ada", where: "chat", and when: "2026-10-29 09:00" through the token`, no `ref`); `world.ts` creates the project `work` with no records (plan line 398); plan 2 line 647 resolves the ref before holding.
Failure: an `ask` on a ref the empty project lacks answers `not-found`, so the builder must seed a record the plan does not name, or the test asserts the wrong thing.
Fix: say the test first adds an entry (or uses a record `world.ts` seeds) and asks about its ID.

Nothing else new: the plan text of line 443 now places the clause "since a decision needs an `id` and a `date` …" after the `area` clause, which reads oddly but changes nothing a builder does.

## Counts

N-7: resolved.
STORE-1's answer C: applied as d-2v8vtk states, through the API, the command, the guide, and the page; names consumed from plan 2 match `a035344`; carried tests approve before asserting and match their Python assertions; parity rows honest; d-4qv0xb's handles hold; lane waits right.
New: 0 Blocking, 0 Important, 1 Minor (N-8).
