# Brief: Task 8a, fix round 1 (with Task 7a's D-2 and Task 7b's Minors)

You fix findings of `docs/superpowers/plans/2026-11-02-lodge-server-core/task-7b-8a-review.md` and Task 7a's D-2 (`task-7a-review.md`) in this repository, on its current branch, a lane (author decision d-xdqsmf): Tasks 8c and 9b are built at the same time in other worktrees.
Read `CLAUDE.md`, then `task-8a-brief.md` and `task-7b-brief.md` (the requirements and the plan's Global Constraints), then the two reviews, in that folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.

## What to fix

- Ruling d-qe513h (`uv run --frozen --quiet lodge show d-qe513h --reasoning`):
  - `check-state.ts` exports `checkResult(problems, notes)`, which computes `ok`; `checkState` and `checkChange` (`check-change.ts`) build their results with it, and nothing builds a `CheckResult` literal by hand; a test that a result built from a failing problem list is not `ok` (8a-D-1), seen failing against the getter-on-a-literal form.
  - `derive.ts` exports `compareOrderKeys` (the instant through `orderInstant`, then the ID by code point), `derive.ts` itself sorts with it, and `confirmation.ts` and `views.ts` use it in place of their own comparisons (7a-D-2); C-1's test of Task 7a's fix round pins it.
- The Minors of Tasks 7b and 8a in `task-7b-8a-review.md`: as each finding's Fix says, where the fix is in those tasks' files; for 8a-D-2, add the tests it names for the problem sort and the de-duplication of `rests_on` and attachments.
- Each new or changed test is shown failing against the code before your fix (or the mutation the finding names).
- Touch only the files these findings name, plus `ts/knip.json` if a new export needs it; leave `ts/src/core/index.ts` alone (the two exports stay inside the package).

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-8a-fix-1-report.md`: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
