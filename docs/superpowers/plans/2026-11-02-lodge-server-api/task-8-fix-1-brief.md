Read `CLAUDE.md` in this worktree first.

Outcome: the findings of `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-review.md` (I-1, M-1, M-2) and `task-8-codex-review.md` (M8-1) are fixed on `server-api-c`, starting from its current head.

Scope: `ts/src/core/*.ts`, `ts/src/app/ports.ts`, `ts/src/api/{index,setup,serve}.ts`, and one new test file `ts/tests/api/serve.test.ts`; nothing else, and no structure check is loosened.
I-1: a `/** @public */` on a re-export statement hides every name in its block; move each such tag onto the single specifier knip reports (own line before that name inside the block), so that a new unread export in the block is reported again; probe as the review does (add an unread export to a tagged block, run knip, see it reported, remove it).
M-1 and M8-1: remove every definition-level `/** @public */` tag that knip does not need; with the tags removed one at a time, only the ones knip reports (`THREADS`, `Files`, `HeldMessage` and whatever the specifier-level change leaves) stay; run `cd ts && bun --bun node_modules/knip/bin/knip.js` for each step.
M-2: `listen` takes a repeated signal as a request to stop at once: the second signal calls `server.stop(true)`; test it in `serve.test.ts` with `Bun.serve` replaced by a fake server and a controlled `stop()` promise, opening no socket, as the review's probe did (first signal calls `stop()` once, the second calls `stop(true)`, handlers are removed when it settles); see the test fail before the change.
M-3 of the review (`listen` throwing synchronously on a bound port) stays as it is, parked.

Done when `sh scripts/check-ts.sh` exits 0 with knip reporting nothing; write `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-fix-1-report.md` (per finding what changed, the failing output before, the knip result after); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
Unsettled design goes to the ask tool.
