# Task 10 review: people in the core

Commit 2a1eeb6 on `server-store-c`, against `server-store` at c64c82f (the merge base).
Reviewer probes ran in a detached scratch worktree at 2a1eeb6; the branch under review was not edited.

## Is the work real?

Yes.
The diff touches every file the plan's Files list names, adds `ts/src/core/people.ts` (26 lines), and threads `people` through every `isAuthor`, `parseThread`, and `writeThread` call in `ts/src/core` and `ts/scripts`.
`ts/tests/core/people.test.ts` holds the ten tests Step 1 names, under those exact titles.
The test count rose by ten, not by one: with the task's sources reverted to c64c82f and `people.test.ts` kept, `bun test` gives `932 pass, 10 fail, Ran 942 tests`; at 2a1eeb6 it gives `942 pass, 0 fail`.
The 942 shared with lane A is a coincidence of two branches each adding to 932 (lane A's Task 2 also landing on 942 is the dispatch's observation; I did not rerun lane A).

## Mutation sweep

Each `people`-carrying call site was mutated back to lodge 0.2's author-only reading, one at a time, and `bun test tests/core` run (script `/tmp/t10probe/mutate.py`, sources restored after each).

| Mutation | Site | Core suite |
|---|---|---|
| person's `when` written unquoted | `threads.ts:127` | survives |
| person's `when` read as a stamp | `threads.ts:97` | 1 fail |
| `where` words, `where` check | `threads.ts:96` | 1 fail each |
| read-back without `people` | `threads.ts:133` | 1 fail |
| `load` parses threads without `people` | `snapshot.ts:58` | 1 fail |
| `load` drops the tree's `people` | `snapshot.ts:65` | 7 fail |
| `tree()` default empty | `snapshot.ts:24` | 25 fail |
| `restored` drops `people` | `apply-state.ts:70` | survives (equivalent: `status` never reads `isAuthor`) |
| `confirmedBy` author-only | `derive.ts:105` | survives |
| `confirmedByHer` author-only | `derive.ts:118` | survives |
| `countsFor` in `touchedByFlagged` | `derive.ts:124` | survives |
| `undone`: later author-only | `derive.ts:203` | survives |
| `undone`: other author-only | `derive.ts:206` | survives |
| `flagged` skips author-only | `derive.ts:211` | survives |
| `flagged` counts author-only | `derive.ts:212` | 1 fail |
| `cleared` author-only | `derive.ts:229` | 1 fail |
| immutable reasoning | `check-immutable.ts:37` | 1 fail |
| role, quote, confirms checks | `check-state.ts:100`, `:102`, `:116` | 1 fail each |
| `confirmableIds` author-only | `confirmation.ts:20` | survives |
| edit-back: own, replaced | `feedback.ts:92`, `:96` | survives both |
| quote, unquoted | `views.ts:64`, `:207` | 1 fail each |
| confirmation words | `confirmation.ts:63` | 1 fail |
| author branches of the words | `people.ts:4`, `:10`, `:13` | carried tests fail |

Ten sites with an observable effect survive every test.
For each I wrote a probe over `people = {ada}` (`/tmp/t10probe/zz-probe-people.test.ts`, kept after the scratch worktree is removed, nine tests; it runs from `ts/tests/core/`): all nine pass on 2a1eeb6, and each of the ten surviving mutations fails at least one of them.
So the code is right at every site; the gap is in the tests.

## Correctness

### Important

**C-I1. Ten of the people call sites in `derive`, `confirmation`, `feedback`, and `writeThread` have no test that fails when they revert to author-only.**
Handles: `ts/src/core/derive.ts:105`, `:118`, `:124`, `:203`, `:206`, `:211`; `ts/src/core/confirmation.ts:20`; `ts/src/core/feedback.ts:92`, `:96`; `ts/src/core/threads.ts:127`.
Failure scenario: Task 13 rewrites `derive`'s flag code per person; a slip that reads `isAuthor(d)` without `s.people` at `derive.ts:211` makes `ada`'s replacement of her own decision wait for review (`awaitingAuthor` holds it), and `bun test` stays green; at `confirmation.ts:20` it lists `ada`'s own decisions as confirmable, so `ada`'s own decisions join the agent decisions awaiting confirmation; at `threads.ts:127` a person's `when` is written as a plain scalar (`when: 2026-10-28 10:00` where lodge 0.2 writes `when: "2026-10-28 10:00"` for `author`), which reads back the same, since the thread reader keeps every scalar a string (probed with `2026`, `null`, and `10:00`), so only the bytes on disk depart from row 8.
Review Focus 5 names "a flag cleared by a person other than the one it waits for"; the plan's own test list (Step 1) has one flag test, which pins `flagged`'s counting and `cleared` and nothing else.
The plan's Step 1 asks for `person_message_needs_where_and_a_minute` "parsed and written"; the written side of row 8 (`writeThread` quoting a person's minute, `threads.py:118`) is not asserted: the test round-trips a minute that YAML reads as a string either way.
Fix: add to `people.test.ts` the eight tests below (or their equivalents), each over `{ada}`, and an assertion that `writeThread(t, people)` contains `when: "2026-10-28 10:00"`:
`confirmable_and_confirmed_by_follow_the_person` (`confirmableIds` excludes `ada`'s decision; `confirmedBy` of the agent decision is `ada`'s confirmation);
`own_replacement_is_not_flagged`;
`agent_replaces_a_decision_she_confirmed` with `ada`;
`agent_edit_after_she_replaced_an_agent_edit_flagged` with `ada`;
`agent_edit_after_she_corrected_her_own_edit_flagged` with `ada`;
`touched_by_flagged_names_her_entry_edit`;
`edit_back_asked_of_a_person`;
`no_edit_back_when_she_replaces_her_own`.
Verified: the probes pass on 2a1eeb6 and each of the ten mutations fails one.
Cost if left: the per-person rework of Task 13 lands on code whose people wiring is unpinned, and the carried suite cannot catch it because every carried tree is `{author}`.

### Minor

**C-M1. `confirmationDraft` writes the person unquoted, so a name that is not a plain YAML scalar breaks the draft.**
Handle: `ts/src/core/confirmation.ts:62` (`decided_by: ${person}`).
Failure scenario (probed through `parseRecord` on the draft): `person = "a: b"` gives `the header is not valid YAML: Nested mappings are not allowed in compact mappings`, and `person = "#ada"` gives `decided_by must be a non-empty string`; `Ada Lovelace`, `o'neil`, and `yes` read back.
Whether such a name can reach the core depends on Task 11's sign-in and roles, which the plan does not restrict; `writeRecord` already quotes a non-plain `decided_by` (`ts/src/core/fileformat.ts:110`, `PLAIN` at `:71`), and `writeThread` a non-plain `by` (`threads.ts:126`).
Fix: write `decided_by` as `writeRecord` does, plain when it matches `PLAIN` and quoted otherwise, so `decided_by: author` keeps lodge 0.2's bytes; add a case with a non-plain name to `confirmation_draft_names_the_person`.

**C-M2. `person_message_needs_where_and_a_minute` accepts any `ValueError` from `writeThread`.**
Handle: `ts/tests/core/people.test.ts:91-96` (`toThrow(ValueError)`).
Failure scenario: a change that makes `writeThread` throw a `ValueError` for another reason (say, the `when` quoting at `threads.ts:127` refusing a minute) still passes, and row 7's words on the write side go unchecked.
Fix: `toThrow("the thread would not read back: a message by ada needs where")`.

## Checks that hold

- Plan Step 3's grep (`isAuthor(`, `parseThread(`, `writeThread(`, `tree({`, `load({` over `ts/src/core` and `ts/scripts`): every call passes `people`, the only lines without it being the four definitions; the one `tree({` (`apply-state.ts:69`) passes `people: add.tree.people`; `differential.ts:44` goes through `tree()`.
- Words, rows 1 to 9 of the plan's table against `ts/src/core/people.ts`: each keeps lodge 0.2's text for `author`, character for character (the carried `check_3_author_lookalike`, `check_3_confirms_on_a_non_author_decision`, and `check_5_agent_reasoning_changed_in_any_way_fails` fail when the author branches of `people.ts:4`, `:10`, and `:13` are forced off), and reads as the right column otherwise.
- The words the plan leaves to Task 13 still read as lodge 0.2's: `feedback.ts:89`, `views.ts:185`, `views.ts:189`.
- `parseThread` and `writeThread` follow `src/lodge/core/threads.py:85-88` and `:118` with `by in people` for `by == "author"`; a person's `when` stays an unvalidated string, as lodge 0.2's author minute is.
- Core rules: no new `catch`, regex, `sort`, or `ok` key in the diff; `sh scripts/check-ts.sh` exits 0 in the scratch worktree (`942 pass, 0 fail`), structure tests included.
- `#core`'s front door is unchanged (`ts/src/core/index.ts` not in the diff), so `people.ts` stays inside the core, as the plan's Produces says.
- `git diff --stat server-store..server-store-c -- ts/tests/core` names only `people.test.ts` and `builders.ts`, whose one line gives `snapshotOf`'s literal `Snapshot` its `people`.
- `sh scripts/differential.sh` in the scratch worktree: `377 records, 10 areas, 0 threads, 0 problems, 117 queries, 387 rewritten files`, `0 differences`; lodge's own records hold no thread, so the differential does not exercise the thread changes, which the carried thread tests do.

## Practice

No findings beyond C-M2.
`people.ts` holds one small function per row, each choosing on the condition the plan's table names (`people.has("author")` for rows 1 and 3, `person === "author"` for the rest), with no comment and no duplication of the words elsewhere.
The report's claims check out: ten new tests, carried test bodies unchanged, no parity row (Task 10 has no flip step), and the minute kept a string.

## Design

**D-M1. The rule that every call passes the snapshot's `people` is held by a grep, and a defaulted parameter hides a missed one.**
Handles: `ts/src/core/derive.ts:158`, `ts/src/core/threads.ts:28`, `:116` (`people = AUTHOR_ONLY`); plan Task 10 Step 3 and Task 11 Step 3 (the greps).
Failure scenario: Task 11 or 13 adds `isAuthor(d)` in `app` or `derive`; it compiles, every carried test runs over `{author}` and passes, and a `{ada}` project silently reads `ada` as an agent; C-I1 shows the present tests would not catch it at ten of the sites.
The defaults are the plan's (d-d96y91, so lane A's one-argument `writeThread` call compiles), so this is not a fault of the build.
Fix, for the coordinator to weigh: once Task 11 has passed `people` at every `app` call, a structure check in `ts/tests/structure/calls.ts` that every call of `isAuthor`, `parseThread`, and `writeThread` under `ts/src` passes two arguments turns Step 3's grep into a test; adding a rule is a structure change, so it is recorded with `lodge add` before it lands.

Integration with lane A holds: `server-store-a` builds its trees through `tree()` (`ts/tests/app/fakes.ts:42`, `:44`, `:59`; `ts/tests/app/ports.test.ts:23`), so the now required `Tree.people` does not break its compile whichever lane merges first.

## Files read

Read: `CLAUDE.md`; the plan's Global Constraints, Calls made, Review Focus, Tasks 10 and 11; `task-10-brief.md` (lanes and Task 10 section, compared with the plan); `task-10-report.md`; the whole diff `server-store..server-store-c -- ts`; `ts/src/core/derive.ts:80-240`, `ts/src/core/feedback.ts:85-120`, `ts/src/core/apply-state.ts`; `ts/tests/core/people.test.ts`, `builders.ts:1-60`, `feedback-edit-back.test.ts:1-60`, `derive-confirmed-retired.test.ts:1-45`; `src/lodge/core/threads.py:80-122`; design lines 74-78, 94, 101, 258-263, 302 (by grep); `lodge show d-vwsnz5`; `server-store-a`'s `ts/tests/app/fakes.ts` (grep).
Not read: the rest of the design document, lodge 0.2's `check_state.py`, `check_immutable.py`, `views.py`, and `confirmation.py` (the words were checked through the carried tests that pin them), the other carried core tests, `task-10-codex.log`, and the plan's other tasks.

## Verdict

0 Blocking, 1 Important, 3 Minor.
