Read `CLAUDE.md` in this worktree first, then `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-6-review.md` (findings I-1 to I-5, M-7, M-9; history, do not edit it) and the "### Task 6" section of `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md`.

Outcome: the four unpinned security rules are pinned by tests that fail when the rule is removed, and the 422 for a failed check no longer depends on duck-typing.

Scope: `ts/src/api/*` and `ts/tests/api/*` only; `ts/src/cli` and plan 4's files are out of scope.
The names `ApiOptions`, `lodgesOver`, `handler`, `issueSetupCode`, and `person.ts`'s `approve`, `decline`, `held` dispatch stay where they are.

Items, each test-first (write the test, run it, mutate the code the review names so you see it fail, restore):
1. I-1: `register-options` and `register` with neither a setup code nor a session are `unauthorised` (`ts/src/api/passkeys.ts:53`).
2. I-2: sign-in's answer sets the session cookie with the attributes the plan lists (`passkeys.ts:175`).
3. I-3: setup-code length, alphabet, and use of all 100 bits pinned (`ts/src/api/setup.ts:128-146`; the mutation `& 15` must fail).
4. I-4: a request with `Authorization` and a cookie is the agent's on `register` and `sign-out` as well as `projects`.
5. I-5 (`ts/src/api/http.ts:49-57`): `personOperation` returns `{ result, checkFailed }`; the handler answers 422 from `checkFailed` and 200 otherwise, with no inspection of the result's shape; `approve`'s `CHECK_FAILED` sets it.
   Plan 4's `importOperation` returns the same pair, so a failed import check will answer 422; add a test with a stand-in person operation returning `{ result, checkFailed: true }`.
6. M-7: a stale cookie on a server not set up answers `unauthorised` (`sign in again`), not 403.
7. M-9: the library's message reaches `options.log` with line breaks escaped, so a log line cannot be forged.

Leave M-6, M-10, and the other minors alone.
Unsettled design goes to the ask tool.

Done when `sh scripts/check-ts.sh` exits 0; write `task-6-fix-1-report.md` in the plan's folder (per item: the test with `file:line` and the mutation that fails it, and which tests were written after the code); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
