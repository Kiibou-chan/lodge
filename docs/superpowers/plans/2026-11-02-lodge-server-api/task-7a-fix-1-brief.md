Read `CLAUDE.md` in this worktree first, then `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7a-codex-review.md` (findings 1 and 2) and `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7a-review.md` (Important I-1 and the Minor on `client()` and a malformed answer); both are history, do not edit them.

Outcome: three lost or missing pins are in place, each failing against the mutation its review names, and a malformed server answer is one sentence instead of an uncaught error.

Scope: `ts/tests/*` and `ts/src/cli/client.ts`; `#cli` exports stay as they are.

Items, each test-first (write the test, mutate the code the review names so you see it fail, restore):
1. Codex finding 1: `ts/tests/app/thread-fix-paths.test.ts:21` also asserts `about s-zzzzzz, not found` through `run(["waiting"], io)` over the existing synthetic `Lodge` (the Python carry `tests/app/test_thread_fix_paths.py:32`); the mutation `?? "unknown"` at `ts/src/cli/thread-output.ts:22` and `:25` must fail it.
2. Codex finding 2: `ts/tests/e2e/show-levels.test.ts:28`, `ts/tests/e2e/waiting.test.ts:47`, and the analogous `indexOf` comparisons assert that both operands are present before comparing positions, as Python's `str.index` raises; probes A and B of the review must fail.
3. Sonnet I-1 (`ts/src/cli/commands.ts:77`): a test spies on the request body of `init` and requires the settings' `core` table in `project-create` (`[length]` and `[import]` values included); the mutation `{ settings: {} }` must fail it.
4. Minor: `client()` (`ts/src/cli/client.ts`) answers a body that is JSON but has no usable `result` or `error` with `CliError("<url> answered something other than a lodge answer")`; test it in `ts/tests/cli/client.test.ts` (stay at 300 lines or fewer, move cases to a new file if needed).

Done when `sh scripts/check-ts.sh` exits 0; write `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7a-fix-1-report.md` (per item: the test with `file:line`, the mutation that fails it, which tests were written after the code); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
Leave the other minors alone.
Unsettled design goes to the ask tool.
