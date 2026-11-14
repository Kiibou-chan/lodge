# Brief: Task 3, fix round 1

You fix the findings of `docs/superpowers/plans/2026-11-02-lodge-server-core/task-3-review.md` in this repository, on its current branch.
Read `CLAUDE.md`, then `task-3-brief.md` (Task 3's requirements and the plan's Global Constraints), then the review, in that folder.
Do not commit and do not push; you have no network, so never run `bun install` or `bun add`.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.

## What to fix

- B1, I1, I2, I3, m2, m3, m6, m7, and m8: as each finding's "Fix" says.
- I4 and I5: as each finding's "Fix" says; the coordinator's ruling d-mfskz3 (`uv run --frozen --quiet lodge show d-mfskz3 --reasoning`) settles that the rules win over the brief's lists.
- m1: per ruling d-s5s2c3: `fetch` and `new WebSocket` are reported as `sockets outside api` in `store` and `git`; `api`, `cli`, and `hook` may call them; `core` and `app` keep their own ban.
- m4: remove the `test:structure` script from `ts/package.json`.
- m5 and m9: build the `allowed-imports` and `front-door` rules of `.dependency-cruiser.cjs` from `PACKAGES` and `CORE_NPM` of `ts/tests/structure/table.ts` if dependency-cruiser's CommonJS config can read them without a build step; if it cannot, keep the rules written out, add a test that checks them against `PACKAGES` and `CORE_NPM`, and say which in the report. Keep lines to 100 characters.
- Each new or strengthened test is shown failing against the mutation the finding names (or the code before your fix), and the report gives that output.
- Task 4's code (`ts/src/core/*.ts`) is committed; if a strengthened rule flags it, fix the rule if the flag is false, and otherwise stop with BLOCKED and the flag.

Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-3-fix-1-report.md`: per finding, what you changed, the test, and its failing output; the commands you ran and their last lines.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
