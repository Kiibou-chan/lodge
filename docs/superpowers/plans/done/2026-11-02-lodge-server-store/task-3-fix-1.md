# Fix round 1 for Task 3 of `docs/superpowers/plans/2026-11-02-lodge-server-store.md`

Worktree `/var/tmp/lodge-store-a`, branch `server-store-a`. Read `CLAUDE.md`, then `docs/superpowers/plans/2026-11-02-lodge-server-store/task-3-review.md` (the review) and `docs/superpowers/plans/2026-11-02-lodge-server-store/task-3-brief.md` (the task).
Fix finding C1 (Important): every carried `pytest.raises(LodgeError, match=...)` must assert the class as well as the message (`await expect(p).rejects.toThrow(LodgeError)` beside the pattern check, or one `raises(promise, Class, pattern)` helper in `ts/tests/app/support.ts`); confirm by replacing `LodgeError` with a plain `Error` at each site of `ts/src/app/writes.ts` that the review lists (one per run) that a test now fails, then revert, and list that in the report as a table.
Also fix the Minors PR1, PR2, PR3 (not D1; the coordinator places it in Task 4).
Same rules as the brief: test-first where applicable, `sh scripts/check-ts.sh` last and green, never edit earlier briefs/reports/reviews (add `docs/superpowers/plans/2026-11-02-lodge-server-store/task-3-fix-1-report.md`), commit with explicit paths as the brief says (trailer `Co-Authored-By: Codex <noreply@openai.com>`), `git push origin server-store-a`.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line, concerns.
