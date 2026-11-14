# Task 13 review: review flags per person

Build commit 288e95d on `server-store-c`, against the plan's Task 13 (`docs/superpowers/plans/2026-11-02-lodge-server-store.md:666-684`), its brief, and `lodge spec`.
Probes ran in a scratch worktree at 288e95d (`/var/tmp/lodge-review-13`) and one at the parent d6e49da (`/var/tmp/lodge-review-13-base`), both removed when done.

## Correctness

### 1. Blocking: a person's own decision is flagged for another person

Handle: `ts/src/core/derive-flags.ts:12-14` with `:82`.
`reviewFlags` runs `flagged` once per person with `people` narrowed to that person alone (`flagged({ ...s, people }, …)`), so inside ada's pass bo's decisions are not a person's and pass the skip at `:82`.
The spec flags agent decisions only: "An agent decision is flagged as awaiting the author when it replaces or narrows an author decision, or changes a specification entry whose last change was an author decision" (s-01k42c), and feedback "says so when an agent decision will raise a review flag" (`lodge spec`, line 434 of its output).
The plan's rule opens the same way: "a decision that lodge 0.2 flags is flagged for each person P" (plan line 676), and lodge 0.2, read with `people` as the set, never flags a person's non-imported decision; the parent commit's `flagged` skipped `isAuthor(d, s.people) && d.importedFrom === null` with the full set.
Probe, people `{ada, bo}`, bo's decision narrowing ada's: at 288e95d `derive(s).awaiting` is `[["d-002000", ["ada"]]]`, `level1` shows `awaiting ada` on bo's decision, and `feedback` tells bo `this decision will wait for ada: it takes effect at once, …`; at d6e49da `awaitingAuthor` is empty.
The same holds for bo editing an entry ada edited last (`[["d-005000", ["ada"]]]`).
Failure scenario: after the merge with Task 11, bo, an owner, adds his own decision narrowing ada's through `Lodge.add`; it is published (Task 12b holds only a person's decision drafted by someone else), and from then on it sits in the waiting list for the author (`src/lodge/app/reads.py:58` reads `awaiting_author`) and in ada's flags until she confirms a decision her co-owner made, which no spec entry asks for.
No test pins either reading: every flagged decision in `ts/tests/core/flags-people.test.ts` is an agent's.
The differential (`sh scripts/differential.sh`: `0 differences`) cannot see it, since lodge's own records have one person.
Fix: give `flagged` the one person and the full set separately; skip a decision whose `decidedBy` is in the full `people` and is not imported (lodge 0.2's skip), and read the one person only for `counts`, `hers`, `undone`, and `cleared`.
Add a test `a_persons_decision_is_not_flagged_for_another` (bo narrowing ada's decision, and bo editing an entry ada edited last: `awaiting` empty, no feedback line).
If the per-person extension is wanted instead, it changes what the spec says and goes to the author.

### 2. Minor: three behaviours the plan names are not guarded by any test

Mutations, each run with `cd ts && bun test tests/core` in the scratch worktree and reverted:

| Mutation | Where | Result |
| --- | --- | --- |
| M1: `cleared`'s `oldest.indexOf(target) < oldest.indexOf(later)` replaced by `true` | `derive-flags.ts:103` | caught: `confirm_dated_before_does_not_clear` |
| M2: the people loop unsorted, `[...s.people]` | `derive-flags.ts:12` | caught: `touching_two_people_waits_for_both` |
| M3: the persons of `awaiting P on X` unsorted | `views.ts:188-190` | survives |
| M4: `listedPeople` without the Oxford comma, `items.join(" and ")` for any length | `people.ts:28-31` | survives |
| M5: `touchedByFlagged`'s behind edits counted for every person, `countsForPeople(oldest, s.people, d)` | `derive.ts:130` | survives |
| M6: `undone` without its not-a-person's test | `derive-flags.ts:77` | caught: three carried tests |
| M7: `confirmed by` groups unsorted | `views.ts:199` | caught: `confirmed_by_names_each_person` |
| M8: feedback's `author decision` branch removed | `feedback.ts:92` | caught: `decision_derive_flags_waits_for_author` |
| M9: `awaiting` words without `the author` | `views.ts:184` | caught: `level1_status_who_flags` |
| M10: `hers` from every person | `derive-flags.ts:13` | caught: `a_confirmed_agent_text_counts_for_its_confirmer` |
| M11: a confirmer named without `the author` | `views.ts:201` | caught: `confirmed_decision_shows_confirmation_and_keeps_decided_by` |
| M12: `hers` counting imported confirmations | `derive-flags.ts:33` | caught: `imported_confirmation_does_not_make_a_decision_hers` |
| M13: `flagged` given the full snapshot, not the one person | `derive-flags.ts:14` | caught: four of the new tests |

Failure scenarios for the survivors: M3, a spec entry touched by two flagged decisions, one waiting for bo and the next for ada, reads `awaiting bo and ada on …` against the plan's code-point order; M4, three persons read `awaiting ada and bo and cy` against the plan's "the Oxford comma for three or more" (plan line 678); M5, ada's decision behind an agent edit she has since confirmed is listed as `awaiting bo on <agent decision>` although bo waits on another part of it.
Fix: one test each in `flags-people.test.ts`: two flagged decisions on one entry waiting for different persons in reverse order; a flag over three persons (`awaiting ada, bo, and cy`); and an agent decision narrowing bo's decision and editing an entry after ada's edit, confirmed by ada, whose `touchedByFlagged` lacks ada's decision.

## Practice

### 3. Minor: `listedPeople` is a third copy of the Oxford list

Handle: `ts/src/core/people.ts:28-31`, identical to `listed` at `ts/src/core/feedback.ts:139-142`, and a third spelling at `ts/src/core/confirmation.ts:53-58`.
The coordinator's note on this task was to share `PLAIN` rather than keep a copy; the build did that and added a new copy of another helper.
Failure scenario: a later change to the list's words (an "or", a cap) reaches one of the three.
Fix: keep one `listed` (in `people.ts` or `text.ts`) and call it from `feedback.ts` and `confirmation.ts`.

### 4. Minor: the feedback line compares its own rendered words and re-spells `reasoningWords`

Handle: `ts/src/core/feedback.ts:90-93`.
`people === "the author"` tests the output of `waitingPeople` to choose `author decision`, which `reasoningWords("author")` in `people.ts:13-19` already gives; the plan puts the functions that choose a person's words in `people.ts` (plan line 533).
Failure scenario: a change to `waitingPeople`'s words for `author` silently switches the feedback to `a later decision of the author`, which M8 shows the carried test then catches only by its exact text.
Fix: a `waitWords(people: readonly string[])` in `people.ts` that returns the whole sentence, choosing on `people` rather than on rendered text.

### 5. Minor: names and comments in `derive-flags.ts` still say "author" and "her"

Handle: `ts/src/core/derive-flags.ts:30` (`confirmedByHer`), `:63` (comment: "a non-imported author replacement when they are not hers"), `:84-90` (`touchesAuthor`, `followsAuthor`) and `:109` (`followsAuthorChange`), `:96` (comment: "a later, non-imported author decision").
Each now runs for one person of `people`, so the comments state something no longer true, and the reader of `reviewFlags` cannot tell that `hers` is the one person's.
Fix: `confirmedBy(person)`, `touchesPerson`, `followsPersonChange`, and the comments in terms of "the person".

### 6. Minor: the flags in `views.ts` grew a dense inline expression and a misnamed call

Handle: `ts/src/core/views.ts:184` and `:194-205`.
`d.awaiting.get(id) ?? []` behind `d.awaitingAuthor.has(id)` is a fallback that cannot be taken, since `awaitingAuthor` is the map's keys (`derive.ts:121`), and if it ever were it would print `awaiting ` with nothing after it.
The `confirmed by` line nests a `filter` inside a `map` inside a template inside `listedPeople`, and names each confirmer through `waitingPeople([person])`, a function named for who waits.
Failure scenario: a reader changing the waiting words (finding 4) changes the confirmers' words with them.
Fix: read `const awaiting = d.awaiting.get(id)` and test it, as `feedback.ts:89` does; move the confirmer grouping into a named function, and name the one-person words `personWords(person)` in `people.ts`.

## Design

### 7. Minor: `reviewFlags` narrows the people by building a fake snapshot

Handle: `ts/src/core/derive-flags.ts:14`, `flagged({ ...s, people }, …)`.
Spreading a `Snapshot` to swap one field makes every helper below read one set as both "the persons" and "this person", which is the cause of finding 1, and couples `flagged` to the snapshot's whole shape when it reads only `people` and `decisions`.
Fix: with finding 1, pass `decisions`, the full `people`, and the one `person` as parameters.

## Checked and clean

- The core-only rules: no `catch` added, no `ok` key, the one regular expression touched (`PLAIN`, `fileformat.ts:72`) keeps its `u` flag and is used with `test` without `g`, and every `sort` added has `byCodePoint`.
- File sizes: `derive.ts` 169, `derive-flags.ts` 118, `views.ts` 229, `feedback.ts` 182, `people.ts` 34 lines, all under 300.
- Fixtures: `ada` and `bo`, made up; no personal path.
- `cleared` reads order by `indexOf` in `oldest` where it read `compareOrderKeys`; `oldest` is sorted by `compareOrderKeys` (`derive.ts:88`), a total order with the ID as tie-break, so the two agree (M1 is caught).
  Its cost is negligible: `derive` on 3000 decisions with three persons took 19.4 ms at 288e95d and 16.1 ms at d6e49da (a scratch timing test, the mean of five runs).
- Task 11's first words: the feedback line still starts `this decision will wait for`.
- The coordinator's note: `PLAIN` is exported once from `fileformat.ts` and read by `confirmation.ts:63`.
- `sh scripts/check-ts.sh` in the scratch worktree at 288e95d: exit 0, `1032 pass`, `0 fail`, no dependency violations.
- `sh scripts/differential.sh` in the scratch worktree: `0 differences`, `1 pass`.
- The report's eight failing-first outputs match the eight tests the plan names.

## Files read and not read

Read: `CLAUDE.md`; the plan's lines 1-230 and 516-698; `task-13-brief.md` (its Task 13 section and the coordinator's note); `task-13-report.md`; `task-13-codex-final.txt`; the design's lines 70-80; `lodge spec` (its flag lines) and `lodge show d-4spcem`, `lodge search "review flag"`; the source diff of 288e95d; `ts/src/core/derive.ts` whole; `derive-flags.ts`, `people.ts`, and `flags-people.test.ts` whole; `views.ts:170-210`; `feedback.ts:80-96` and `:136-145`; `confirmation.ts:45-65`; `ts/tests/core/builders.ts:32-43`; `scripts/differential.sh`; `src/lodge/app/reads.py:58` by grep.
Not read: the rest of `views.ts` and `feedback.ts`; `snapshot.ts`; the carried core tests beyond the names the mutations reported; `src/lodge/core/derive.py` (the port of Task 10's state stands in for it, and the differential agrees); `task-13-codex.log`.

Verdict: 1 Blocking, 0 Important, 6 Minor
