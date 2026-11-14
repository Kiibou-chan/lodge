# Task 13 fix round 1 report

Fixed review findings 1 to 7 on `server-store-c`, starting at `288e95d`.

## Changes

- `ts/src/core/derive-flags.ts`: pass the decisions, full people set, and current person separately to `flagged`, preserving the full-set skip for non-imported decisions by any person while counting, undoing, and clearing per person.
  Replace the remaining gendered and author-specific helper names and comments with people terminology.
- `ts/src/core/people.ts`: keep one shared Oxford `listed`, add `personWords`, and choose the complete feedback sentence in `waitWords` from person data through `reasoningWords`.
- `ts/src/core/feedback.ts`: use the shared list and feedback sentence helpers.
- `ts/src/core/confirmation.ts`: use the shared list helper instead of its own spelling.
- `ts/src/core/views.ts`: test the awaiting map value directly and extract named confirmer grouping using `personWords`.
- `ts/tests/core/flags-people.test.ts`: add four regression tests, covering both owner-decision cases and all three surviving mutations.
  The original eight tests remain unchanged.

## Failing-first evidence

The owner-decision regression first ran against the unchanged source at `288e95d`.
It failed at the empty awaiting-map assertion: expected `Map {}`, received a decision mapped to `["ada"]`, with 11 pass and 1 fail.
A second run restored `derive-flags.ts` from `288e95d` and temporarily reversed the two cases, proving the entry-edit case also fails with the same unexpected awaiting person.
Both temporary changes were restored before the final gates.
The final test also checks that neither case produces waiting feedback.

Each mutation below ran independently against the original implementation with its new test, using `cd ts && bun test tests/core/flags-people.test.ts -t <test-name-prefix>`.
Every mutation was reverted immediately after its run.
Source handles refer to `288e95d`; test handles refer to the finished file.

| Mutation | Source handle | Regression test handle | First failing output |
| --- | --- | --- | --- |
| M3: remove code-point sorting of the people waiting on an entry | `ts/src/core/views.ts:188` | `ts/tests/core/flags-people.test.ts:98` | `entry_waiting_people_are_in_code_point_order`: expected `awaiting ada and bo on ...`, received `awaiting bo and ada on ...`; 0 pass, 1 fail |
| M4: join every list with ` and `, omitting the Oxford comma | `ts/src/core/people.ts:29` | `ts/tests/core/flags-people.test.ts:106` | `three_waiting_people_have_an_oxford_comma`: expected `awaiting ada, bo, and cy`, received `awaiting ada and bo and cy`; 0 pass, 1 fail |
| M5: count behind edits for all people instead of those still waited for | `ts/src/core/derive.ts:130` | `ts/tests/core/flags-people.test.ts:114` | `behind_edits_count_only_for_people_still_waited_for`: expected `touchedByFlagged.has(first.id)` false, received true; 0 pass, 1 fail |

The M4 mutation changed the short-list condition to always take `items.join(" and ")`, matching the review's surviving behaviour.
No carried test was added or changed, and none cannot hold in TypeScript.

## Validation

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `cd ts && bun test tests/core/flags-people.test.ts`: 12 pass, 0 fail after implementation.
- `cd ts && bunx --no-install biome check --write` with the six explicit changed TypeScript paths: checked 6 files, fixed formatting in 3.
- `git diff --check`: clean.
- `sh scripts/check-ts.sh`: exit 0; Biome, TypeScript, dependency-cruiser, knip, and tests green; 1036 pass, 0 fail.
- `sh scripts/differential.sh`: exit 0; 0 differences; 1 pass, 0 fail.

The two required gates were run again after writing this report, immediately before committing.
All changed modules remain below 300 lines, with the largest at 236 lines.
The core structure gate checks the catch guards, result literals, regular expressions, and sort comparators.
No dependency was installed and no earlier brief, report, or review was edited.
Pre-existing untracked task instructions, reviews, and execution logs were left outside this commit.
No outstanding concerns.
