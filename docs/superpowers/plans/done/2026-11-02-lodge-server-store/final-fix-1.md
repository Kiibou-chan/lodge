# Final review, fix wave 1

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `final-review.md` in this folder; fix the findings below, test-first (each new test seen failing against the mutation the review names), and keep every existing test passing.
Do not dispatch subagents.

1. I-1 and I-2: one staged-drift fixture over `MemoryStore` (`files` lacking decision files while `published` still holds them, as the review's probe built it): `ask` and `reply` drive to `CHECK_FAILED` with nothing published (`threads.ts:167`), and an `add` rewriting a published decision is refused when `current` already holds the rewrite (`writes.ts:124`, `threads.ts:166`).
2. I-3: one store test with two projects (`storage` and `other`): publish a file, a decision, and an attachment to `other`, and assert that `trees()`, `members("storage")`, and `attachmentTexts()` of `storage` show none of it (`read-tree.ts:20-34`, `projects.ts:46-58`, `sqlite-store.ts:65-72`).
3. M-5: `lodge/a\b` in the refusals test (`sqlite-store.ts:99`).
4. M-6: delete the untested `base.rev` guard or assert its message, whichever keeps `tests/store/sqlite-store.test.ts:55` meaningful.
5. M-7: one assertion each for `held()` order in the store (`orderBy("seq", "asc")`), `SqliteProjects.members` sorting, `touchHead` keeping `rev`, and above all `storeFor(project, actor)` attributing events to the actor (`projects.ts:90`).
6. M-1: keep `close` in an internal options type and pass it only from `Lodge.close`.

I-4 is done (the logs are scrubbed by the coordinator); M-2, M-3, M-4, M-8 to M-13 are not this round's.
Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `final-fix-1-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
