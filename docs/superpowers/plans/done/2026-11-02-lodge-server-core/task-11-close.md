# Brief: the closing step of Task 11

You finish Task 11 of `docs/superpowers/plans/2026-11-02-lodge-server-core.md` in this repository, on its current branch, after its lanes have merged (ruling d-442r2f, `uv run --frozen --quiet lodge show d-442r2f --reasoning`).
Read `CLAUDE.md`, then `docs/superpowers/plans/2026-11-02-lodge-server-core/task-11-brief.md` (Task 11's requirements and the plan's Global Constraints): its `front-door.test.ts` bullet and its Step 4 are this step.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Task 12 runs at the same time in another worktree; touch only the files below.

## What to do

- Write `ts/tests/core/front-door.test.ts` exactly as Task 11's brief describes; besides the constructors the brief names, `checkResult` of `check-state.ts` is the constructor of `CheckResult` (ruling d-qe513h) and passes as such.
- Every `#core` export the test finds missing or extra: fix `ts/src/core/index.ts`; if a name of `__all__` has no TypeScript counterpart at all, stop with BLOCKED and the name.
- Every plan 1 row of `ts/tests/parity.json` is `ported` or `changed`, none `planned`, and `grep -c '"planned"' ts/tests/parity.json` counts only rows of plans 2 to 4; a plan 1 row still `planned` stops the step with BLOCKED and the row, unless its file's names are all ported, in which case flip it.
- `ts/knip.json`'s `entry` is Task 2's `["tests/**/*.test.ts", "scripts/*.ts"]` again, and knip reports no unused export; an export knip then flags is removed if nothing reads it, or reported if a later plan needs it.
- The new test is shown failing first (one Python name missing from `index.ts`, one extra name added), and the report gives that output.

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-11-close-report.md`: what you changed per file, the failing output, the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
