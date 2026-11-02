# Brief: Task 4, fix round 1

You fix the findings of `docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md` in this repository, on its current branch.
Read `CLAUDE.md`, then `task-4-brief.md` (Task 4's requirements and the plan's Global Constraints), then the review, in that folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Task 5a (record files) is built on top of Task 4 and committed; keep its tests passing, and if a fix here changes a message or behaviour its code relies on, update that code and say so in the report.

## What to fix

- C-1 (Blocking): a memo per alias target, set before its children are walked, so each node is walked once, as the finding's Fix says; add a test that a header of nine nested anchors, each used twice in the next, loads in well under a second (a bound of 1 s).
- C-2: per ruling d-p48gr1 (`uv run --frozen --quiet lodge show d-p48gr1 --reasoning`): no new refusals; add one test per listed difference pinning the TypeScript behaviour, and list each difference in the report's known differences.
- C-3: per ruling d-fbhdvf: the message is `unreadable character N`, N the decimal code point; a test pins it.
- C-4 and C-5: as each finding's Fix says.
- C-6: per ruling d-v9mw2d: nothing to change in `core`; add the variables to the report's known differences.
- D-1: per ruling d-g1hrmn: add to `stamps.ts` `export function orderInstant(date: string): number`, the instant of a stamp, and of a bare day the instant of `<day>T00:00:00+00:00`, throwing a `ValueError` on anything else; tests for a day, a stamp, a day against a stamp of the same day (`2026-10-29` before `2026-10-29T00:30:00+00:00`, after `2026-10-28T23:30:00+00:00`), and a non-date. It is first read in Task 7a, so `src/core/stamps.ts`'s names stay exported through `#core` as before (d-hshapm).
- C-7, M-1, M-2, P-1, P-2, P-3, P-4, and D-2: as each finding's Fix says.
- Each new or strengthened test is shown failing against the code before your fix (or the mutation the finding names), and the report gives that output.

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-fix-1-report.md`: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
