# Brief: Task 5 fix round 2 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-import`, branch `server-import-import`. Read `CLAUDE.md`, Task 5 of the plan, `task-5-fix-1-report.md`, and the checkpoint review `~/.cache/lodge-work/codex/plan4/sonnet-task5-checkpoint.md`.
Public repository: no personal paths or machine names. British English, no em-dashes, one sentence per line in Markdown.

## Findings to fix (checkpoint review)

1. Important: fix 1's mapped-writer catch (`ts/src/app/importing.ts` about lines 123 to 130) has no regression test; `mapped_thread_failure_is_at_the_server_stage` reaches the server stage through `checkChange`, not through that catch. Probe: changing `mappedProblems.push(` to `writerProblems.push(` leaves all tests passing. Add a test that reaches the catch, for example `prepareImport(copy, "a\nb", new Set(["a\nb"]), …)` (an owner name that the server writer cannot write as an author), expecting stage `server` and its sentence; see it fail against that mutation, then restore.
2. Minor: the source-writer `ValueError` catch (about lines 111 to 113) is uncovered; add a test that reaches it with stage `lodge 0.2`, or, if it is unreachable once the source check has passed, say so in the report with the reasoning and leave the code.
3. Minor: add a one-line comment stating the fact at `.find(...) as string` (about lines 56 to 57), or remove the cast.
4. Minor: tests build the same `ZeroTwoCopy` three times; extract one helper in `ts/tests/app/` used by both test files.
Not yours: the plan wording and the ledger (coordinator's).

Test-first where a test is new. All tests pass; `sh scripts/check-ts.sh` exits 0. Never edit earlier briefs, reports, or reviews. Commit with explicit paths, `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, then `git push origin server-import-import`. Never touch `main`.
Write `task-5-fix-2-report.md` in the plan folder and commit it. Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests.
