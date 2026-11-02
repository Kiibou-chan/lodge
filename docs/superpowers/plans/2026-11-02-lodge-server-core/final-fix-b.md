# Brief: final fix wave, part B (the parked Minors in the port)

You fix the parked Minors of plan 1's task reviews and the final review's remaining findings, in this repository on its current branch (`server-core`); part A (the structure rules, `final-fix-a.md`) is already done and its tests pass.
Read `CLAUDE.md`, then the plan's Global Constraints in `docs/superpowers/plans/2026-11-02-lodge-server-core.md`, then the ledger's lines starting `Parked` in `docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md`, then each review file they name in this folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0. Also run `sh scripts/differential.sh` if `uv` works in your sandbox, and say if it does not.
Read each ruling with `uv run --frozen --quiet lodge show <id> --reasoning`.

## What to fix, in this order

1. 12-D-1 (`task-10-12-8afix-review.md`): the differential compares thread files: they enter the rewrite on both sides (`ts/scripts/differential.ts:65-73`, `scripts/differential_dump.py:65-76`), and a made-up store holding at least two threads (open and closed, one message by `author` with where and when) is part of the run, so changing `writeThread`'s output makes the run report a difference; show it does.
2. 12-D-2: `bun test` passes with only `bun` on PATH: the differential test runs from `scripts/differential.sh` (and so from `scripts/check.sh`), not from `bun test`'s default set; say how.
3. F-5 (`final-review.md`): a test pinning `isDigit`'s Unicode digit branch.
4. 10-D-1: tests that kill the 21 surviving `feedback.ts` mutations the review lists, as new TS tests (Python has the same gap; give their parity row a `why`).
5. Every other finding on a `Parked` line (Tasks 5b, 6, 8a, 8b, 8c, 9a, 9b, 10, 11, and the 8a fix round): as each finding's Fix says. Some may already have been taken by a later round; check, and list those as already done with the commit.
6. 9b-C-1 in particular: the carried render assertion compares as strictly as Python's.

Each new or changed test is seen failing against the code before your fix, or against the mutation the finding names.

Write your report to `final-fix-b-report.md` in this folder: per finding, what you changed (or why it was already done), the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
