# Brief: Task 5 fix round 1 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-import`, branch `server-import-import`. Read `CLAUDE.md`, Task 5 and its Review Focus 2 of the plan, and the review at `~/.cache/lodge-work/codex/plan4/run-task5-review/codex.log.final.md`.
Public repository: no personal paths or machine names in code, tests, docs. British English, no em-dashes, one sentence per line in Markdown.

## Findings and the coordinator's rulings

1. Important, `ts/src/app/importing.ts:90`: mapping rewrites a non-author message's bytes (`when` gets quoted) when an owner name or agent role collides with a `by` value on a mixed thread. Ruling: byte preservation governs (design line 289, Review Focus 2, "nothing else changes"). Only the lines that carry `by: author` change; every other byte of a thread stays as the source writer wrote it. Fix so no message but the author's is touched, by whatever means keeps the structure rules (modules at most 300 lines, no new dependency).
2. Minor, `ts/src/app/importing.ts:102`: a failure of the mapped server writer is reported at stage `lodge 0.2` with the source writer's sentence. Ruling: separate the two catches; a mapped-writer failure carries stage `server` and its own sentence. If your fix to 1 removes the mapped writer, keep the refusal for any remaining server-stage failure at stage `server`.

Test-first: add `role_collision_preserves_every_non_author_line` and `mapped_thread_failure_is_at_the_server_stage` as the review describes them (probes in the review), see each fail, then fix. All existing tests keep passing; `sh scripts/check-ts.sh` exits 0.
Never edit earlier briefs, reports, or reviews. Commit with explicit paths, `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, then `git push origin server-import-import`. Never touch `main`.
Write `task-5-fix-1-report.md` in the plan folder (per file changes, each test with its first failing output, commands with last lines, deviations) and commit it.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests.
