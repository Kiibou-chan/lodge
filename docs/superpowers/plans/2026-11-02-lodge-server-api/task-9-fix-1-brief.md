Read `CLAUDE.md` in this worktree first.

Outcome: I1 and M1 of `docs/superpowers/plans/2026-11-02-lodge-server-api/task-9-codex-review.md` are fixed on `server-api-d`, starting from its current head.

Scope: `ts/src/api/page.js`, `ts/src/api/page.html` only if a view needs a hook, `ts/src/api/http.ts`, and `ts/tests/api/page.test.ts` (or a new file beside it); no dependency, no structure check loosened, modules 300 lines or fewer, no socket in any test.
I1: a 401 from any call of the page, including the one made by sign-out, clears the issued secret and every signed-in view and shows the signed-out controls, through one central place in `page.js` (the review's probe P1 is the failing case: a deleted session, then the sign-out listener; also a token issuance that gets 401).
Test it first and see it fail: a test that runs the served script in a `node:vm` context with a minimal DOM and a `fetch` bound to the in-process `handler`, as the review's P1 did, using the existing software authenticator helpers in `ts/tests/api/`; if that harness is out of proportion for one case, a smaller one that drives the script against a stub `fetch` answering 401 is enough, provided it fails against the unfixed script.
M1: the JSON responses of `http.ts` (not found, `use POST`, the 500) carry `Referrer-Policy: no-referrer` and the same `Content-Security-Policy` as the assets; a test through the handler for `GET /missing`, `GET /api/v1/me`, and the unexpected-error path; see it fail first.

Done when `sh scripts/check-ts.sh` exits 0; write `docs/superpowers/plans/2026-11-02-lodge-server-api/task-9-fix-1-report.md` (per finding what changed, the failing output before, the result after); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-d`.
Unsettled design goes to the ask tool.
