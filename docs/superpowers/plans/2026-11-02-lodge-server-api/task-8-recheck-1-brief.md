Read `CLAUDE.md` in this worktree first.

Outcome: a verdict on whether fix round 1 of Task 8 resolves the findings it answers, without a new problem.
Read-only: edit no source or test file, commit nothing; the only file you write is `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-recheck-1.md` (leave it uncommitted); run mutations only in a scratch worktree removed afterwards.

Range: `git diff 2b63b73 e4c2e5a` (the review files are history).
Findings answered, as `task-8-fix-1-brief.md` in that folder lists them: I-1, M-1, and M-2 of `task-8-review.md`, and M8-1 of `task-8-codex-review.md`; the fix report is `task-8-fix-1-report.md`.
M-3 of `task-8-review.md` is parked by ruling and not part of this check.

For each finding: resolved or not, proved by running the probe the report names (an unread export added to a re-export block must be reported by `cd ts && bun --bun node_modules/knip/bin/knip.js`; knip must report nothing on the head; each removed definition tag must leave knip silent) and, for M-2, by mutating `serve.ts` so the second signal does nothing and running `ts/tests/api/serve.test.ts`.
Then look for a new problem the diff introduces (every `/** @public */` is on a name plan 4 consumes or a front-door test reads, the exported names of `#core` and `#api` unchanged, the test opens no socket, the 300-line limit, public-repo hygiene).
Report each as Important or Minor with file, line, and a probe or failing test; list per finding "resolved" or "not resolved".
Done when the file is written; ask through the ask tool for anything unsettled.
