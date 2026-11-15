# Review brief: Task 2 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Read-only review, correctness angle, of commit range `589e829..2bad60b` on branch `server-import-git` in `/var/tmp/lodge-import-git`; read `CLAUDE.md`, then the plan's Global Constraints and "### Task 2" in full, and the builder's report `task-2-report.md` in the plan's folder.
Check each behaviour of the task text against the code and tests: `attempt`/`runBytes`/`run`/`resolveRev`, `readStore` (UTF-8 escapes, attachments, symlinks, settings revision, refusals with their exact sentences), `resolvePath`, `repoRootOf`, `isolateGit`, `zeroTwoRepository`, the parity rows, and that each carried test could fail (try mutations).
Edit nothing. Write findings to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-2-review.md`-shaped text as your final message instead; each finding Important or Minor with file, line, and a probe or failing test.
