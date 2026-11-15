# Brief: Task 6 fix round 1 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-export`, branch `server-import-export`. Read `CLAUDE.md`, Task 6 of the plan, `task-6-report.md`, and the review `~/.cache/lodge-work/codex/plan4/sonnet-task6-review.md`.
Public repository: no personal paths or machine names. British English, no em-dashes, one sentence per line in Markdown.

## Findings to fix (Sonnet review, both Important)

1. `ts/src/app/exporting.ts:38`: `...attachmentTexts` in `exportFiles` is untested; deleting it leaves all 16 tests passing, because `MemoryStore.trees()` puts attachments in `Tree.files` while the SQLite store keeps them in `Tree.attachments`. Add a test with a `tree()` that lacks the attachment plus a separate `attachmentTexts` map; see it fail against the deletion, then restore.
2. `ts/src/app/exporting.ts:62-66`: the approving `publish` forwarding `approves` is untested; dropping the fourth argument leaves all tests passing. Add a test asserting `await inner.held()` is empty after the approving publish (the held item is removed), failing against that mutation.
Use a disposable copy under `mkdtemp` for mutations, never the lane's files left changed.
Out of scope (coordinator parks them): the duplicated branch and remote rule between `app` and `git`, `failed` throwing under `void exporters.written`, `start` and `settled` over a permanently failing target, the two Proxy bodies repeating the bind step.

Test-first. All tests pass; `sh scripts/check-ts.sh` exits 0. Never edit earlier briefs, reports, or reviews. Commit with explicit paths, `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, then `git push origin server-import-export`. Never touch `main`.
Write `task-6-fix-1-report.md` in the plan folder and commit it. Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests.
