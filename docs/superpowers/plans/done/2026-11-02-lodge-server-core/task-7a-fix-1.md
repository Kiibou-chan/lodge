# Brief: Task 7a, fix round 1

You fix the findings of `docs/superpowers/plans/2026-11-02-lodge-server-core/task-7a-review.md` in this repository, on its current branch, a lane (author decision d-xdqsmf): Tasks 8c and 9b are built at the same time in other worktrees.
Read `CLAUDE.md`, then `task-7a-brief.md` (Task 7a's requirements and the plan's Global Constraints), then the review, in that folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.

## What to fix

- C-1 and C-2 (Important): as each finding's Fix says (both test-only); each new or changed test is shown failing against the mutations the finding names.
- The Minors: as each finding's Fix says, where the fix is in Task 7a's own files (`doubts.ts`, `derive.ts`, `derive-review.ts`, and their tests and helpers); for one that needs another task's file, say so in the report and leave it.
- Touch no file outside Task 7a's, and leave `ts/src/core/index.ts`, `ts/tests/parity.json`, and `ts/knip.json` alone unless a finding needs them.

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-7a-fix-1-report.md`: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
