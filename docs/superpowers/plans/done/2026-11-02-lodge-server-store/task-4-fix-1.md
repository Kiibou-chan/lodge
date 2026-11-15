# Fix round 1 for Task 4 of `docs/superpowers/plans/2026-11-02-lodge-server-store.md`

Worktree `/var/tmp/lodge-store-a`, branch `server-store-a`. Read `CLAUDE.md`, then `docs/superpowers/plans/2026-11-02-lodge-server-store/task-4-review.md` (the review) and `docs/superpowers/plans/2026-11-02-lodge-server-store/task-4-brief.md` (the task).
Fix C1 and C2 (Important), and the Minors C3, P1, P2, P3, P4, D1; P5 needs no fix beyond a `file:line` column in this round's report.
C1: each fix is seen failing first against the review's mutation (removing the `no ${what}; ` prefix at `ts/src/app/state.ts:101`).
C2: one test row per input the review lists, seen failing before `strip` replaces `String.trim`.
Same rules as the brief: test-first, `sh scripts/check-ts.sh` last and green, modules ≤ 300 lines, never edit earlier briefs/reports/reviews (add `docs/superpowers/plans/2026-11-02-lodge-server-store/task-4-fix-1-report.md`, with each mutation run as a table), commit with explicit paths as the brief says (trailer `Co-Authored-By: Codex <noreply@openai.com>`), `git push origin server-store-a`.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line, concerns.
