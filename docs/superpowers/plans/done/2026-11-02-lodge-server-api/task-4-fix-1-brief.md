# Task 4, fix round 1

Read `CLAUDE.md`, then `task-4-brief.md`, `task-4-report.md`, and `task-4-review.md` in this folder (history: do not edit them).
Worktree: this one (lane C, branch `server-api-c`), on top of `2bcf61a`.
Test-first: see each new or changed test fail before its fix; all existing tests keep passing; gate `sh scripts/check-ts.sh`.

Fix, each with a test that fails without it:

1. **I-1** (`ts/src/store/schema.ts:79-84`, `ts/tests/store/database.test.ts:206-215`): a schema-2 database with existing projects reopens at version 3 with `settings(name)` null while `names()` lists the project.
   After the migration every existing project answers `settings(name)` as `{}`, the same as a project created without settings (note N-2 in the brief).
   Change `checkMigration(2)` so it pins the new behaviour, with a project present before the migration.
2. **I-2** (`ts/src/store/account-events.ts:36`): spending the newest setup code deletes all codes; add a test where an older code stops being valid after the newest is spent.
3. **I-3** (`ts/src/store/events.ts:105-114`): add a test that pins every table the `rebuild` clear empties (fill each of the six, rebuild, check each is rebuilt from events only).
4. **M-2**: a duplicate token ID is refused with a named error instead of overwriting.
5. **M-3**: `usePasskey` on an unknown ID answers with the store's own not-found error, not a raw `NoResultError`.
6. **M-4**: make `no_event_holds_a_clear_secret` able to fail (hand the store clear secrets through the call that issues them, then scan every event).

Leave M-1, M-5 to M-9 alone (parked in the ledger).
Do not stage `task-4-codex-final.txt` or any `*-codex-final.txt`.
Write `task-4-fix-1-report.md` in this folder: per finding, the test that pins it and its `file:line`, the mutation that fails it.
Commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, push `server-api-c`.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, with the commit hash.
