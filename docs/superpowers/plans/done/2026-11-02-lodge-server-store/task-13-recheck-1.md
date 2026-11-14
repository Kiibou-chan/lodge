# Task 13 recheck of fix round 1

Fix diff `288e95d..6a2f47a`, run in a scratch worktree at 6a2f47a (removed after).

## Findings

1. Answered: `ts/src/core/derive-flags.ts:14` passes `s.decisions`, the full `s.people`, and the one `person` to `flagged`; the skip at `:84` reads the full set, and `counts`, `undone`, `cleared`, and `confirmed` read the one person.
   Test `a_persons_decision_is_not_flagged_for_another` (`ts/tests/core/flags-people.test.ts:82`) covers both cases (narrowing, entry edit): `awaiting` empty and no feedback line.
   Mutation probe: the skip narrowed back to the one person fails exactly that test (11 pass, 1 fail).
2. Answered: each survivor now has a test, and each mutation, applied to the fixed code, fails exactly its test.
   M3 unsorted persons (`views.ts:188`): `entry_waiting_people_are_in_code_point_order`.
   M4 no Oxford comma (`people.ts:29`): `three_waiting_people_have_an_oxford_comma`.
   M5 behind edits for every person (`derive.ts:130`): `behind_edits_count_only_for_people_still_waited_for`.
3. Answered: one `listed` at `people.ts:28`, used by `feedback.ts`, `confirmation.ts:58`, and `views.ts`.
4. Answered: `waitWords` (`people.ts:39`) chooses on the person list through `reasoningWords`; wording unchanged for one person and for several.
5. Answered: `confirmedByPeople`, `touchesPerson`, `followsPerson`, `followsPersonChange`, and the comments at `derive-flags.ts:63` and `:98` speak of the person.
6. Answered: `views.ts:184-185` tests `d.awaiting.get(id)` directly; the confirmer grouping is `confirmedPeople` (`views.ts:223`), naming through `personWords`.
7. Answered: no snapshot spread remains; `flagged` takes its inputs as parameters.

## Gates and rules

- `sh scripts/check-ts.sh`: exit 0, 1036 pass, 0 fail.
- `sh scripts/differential.sh`: `0 differences`, 1 pass.
- Core-only rules: no `catch`, no `ok` literal, no regular expression added, the one added `sort` uses `byCodePoint`.
- Sizes: people 45, views 236, derive-flags 125, feedback 174, confirmation 61 lines.
- Tests: the eight earlier tests are unchanged; four are added; none weakened.

## New problems

None found.

Verdict: 0 Blocking, 0 Important, 0 Minor
