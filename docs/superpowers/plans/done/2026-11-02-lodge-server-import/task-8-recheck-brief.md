# Recheck brief: Task 8 fix round 1 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Read-only recheck of fix commit `a0d5ea1` (range `5bcaa46..a0d5ea1`) on `server-import-server` in `/var/tmp/lodge-import-server`; read `CLAUDE.md`, `task-8-fix-1-brief.md`, `task-8-fix-1-report.md`, and the six Minors listed in the fix brief.
Check each is answered, mutating a disposable copy under `mkdtemp`, never the lane: skipping `exportTargetProblem` fails `bad_target_is_usage` by assertion and does not hang; mutating `settingsRev`'s default to `"HEAD"` fails a test; a relative or empty `repository` is refused `import: repository must be an absolute path` before `moving.read`; the two operations are in the agent-token refusal and an unauthenticated and a wrong-`Origin` call to each is refused; the session constant replaces the magic string; the startup line no longer names a project "startup" and the `options.ts` imports are merged.
Report any new defect the round introduced (Important or Minor with file, line, probe). Edit nothing in the lane.
Final message: findings, or "0 Important, 0 Minor".
