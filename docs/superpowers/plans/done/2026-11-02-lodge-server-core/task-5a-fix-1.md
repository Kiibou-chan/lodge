# Brief: Task 5a, fix round 1

You fix the findings of `docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md` in this repository, on its current branch, and three small items parked from earlier tasks.
Read `CLAUDE.md`, then `task-5a-brief.md` (Task 5a's requirements and the plan's Global Constraints), then the review, in that folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Task 5b (drafts) is built on top of Task 5a and committed; keep its tests passing.

## What to fix

- D-1 (Important): add the review's four tests, each shown failing against the mutants it names (`trimEnd` or `trim` in place of `rstrip` and `strip` at `document.ts:40,44,45,49` and `fields.ts:29`), all five mutants killed.
- C-1 (Important): per ruling d-4m6m35 (`uv run --frozen --quiet lodge show d-4m6m35 --reasoning`): `readRank` refuses a rank that is not a safe integer as a format problem naming the key; tests at `2**53 - 1` (read) and `12345678901234567890` (refused); list it in the report's known differences.
- C-2, C-3, C-4, P-1, P-2, P-3, D-2, and D-3: as each finding's Fix says; for C-3, list both surrogate cases in the report (ruling d-0q54zn defers the decoding to a later plan; nothing to change in code).
- Ruling d-f18pz7: `ts/package.json`'s `check` runs `biome check --error-on-warnings .`; fix every Biome warning in `ts/` (16 at 7c3ab8b, `noNonNullAssertion` and `useTemplate`), by changing the code, not by turning a rule off; if a rule cannot fit, stop with BLOCKED and the rule.
- Parked from Task 3: add a test in `ts/tests/structure/` that pins `PACKAGES` and `CORE_NPM` of `table.ts` to their literal values of ruling d-k5swcq, so a wrong edge in the table fails a test.
- Parked from Task 4 (N-1 of `task-4-recheck-1.md`): `ts/tests/core/fileformat.test.ts:160` feeds an escaped newline where Python's test feeds a literal one; keep the title, and list it in this report among the tests that cannot hold in TypeScript, with ruling d-p48gr1 as the reason.
- Each new or strengthened test is shown failing against the code before your fix (or the mutation the finding names), and the report gives that output.

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-fix-1-report.md`: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
