Read `CLAUDE.md` in this worktree first.

Outcome: a verdict on whether fix round 1 of Task 9 resolves the findings it answers, without a new problem.
Read-only: edit no source or test file, commit nothing; the only file you write is `docs/superpowers/plans/2026-11-02-lodge-server-api/task-9-recheck-1.md` (leave it uncommitted); run mutations only in a scratch worktree removed afterwards.

Range: `git diff 2698ac9 d716ff2`; findings answered: I1 and M1 of `task-9-codex-review.md`; the fix report is `task-9-fix-1-report.md`.
For each finding: resolved or not, proved by running the mutation (I1: revert the 401 branch of `page.js` and run `ts/tests/api/page-session.test.ts`, which must fail for both sign-out and token issuance; also probe a 401 from `token-revoke`, `approve`, and `held`; M1: drop one header from the shared set in `http.ts` and run `page.test.ts`).
Then look for a new problem the diff introduces: the page's JSON error message still shown after the reset, a signed-out `me` response leaving a stale view, the secret surviving in any element after a 401, the CSP header on a JSON response breaking nothing the clients read, the test opening a socket, the 300-line limit, public-repo hygiene.
Report each as Important or Minor with file, line, and a probe or failing test; list per finding "resolved" or "not resolved".
Done when the file is written; ask through the ask tool for anything unsettled.
