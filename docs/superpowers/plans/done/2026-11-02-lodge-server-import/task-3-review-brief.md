# Review brief: Task 3 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Read-only review, correctness angle, of commit range `7818d89..40a6cb0` on `server-import-git` in `/var/tmp/lodge-import-git`; read `CLAUDE.md`, then the plan's Global Constraints and "### Task 3" in full, and the builder's report `task-3-report.md` in the plan's folder.
Check each numbered step of `exportStore` (refusals with exact sentences, tip finding with and without a remote, checked-out-branch refusal, foreign-files refusal, temporary index tree, `unchanged`, commit identity and message, push without force and `moved`, `update-ref` with old value), the test helpers `bareRemote`, `clone`, `seeded`, `worktree`, `riggedRemote`, and that each of the 13 named tests could fail (try mutations).
Also check the three Task 2 Minors the builder took (listed in `task-3-brief.md`): `read-store.test.ts` primary-revision case, `resolvePath` dangling symlinks, `repos.ts` `git` helper using `strip`.
Edit nothing. Final message: findings, each Important or Minor with file, line, and a probe or failing test; or "0 Important, 0 Minor".
