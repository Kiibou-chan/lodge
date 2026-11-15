# Task 5, fix round 1

Read `CLAUDE.md`, then `task-5-brief.md`, `task-5-report.md`, and `task-5-review.md` in this folder (history: do not edit them).
Worktree: this one (lane C, branch `server-api-c`), on top of the commit that holds this brief.
Test-first: for each item, add the test, run the mutation named in the review (or one you pick) and see the test fail, restore the code; all existing tests keep passing; gate `sh scripts/check-ts.sh`.

Fix (tests only unless a test finds a real defect, in which case fix the code and say so in the report):

1. **I-1** (`ts/src/api/http.ts:25`): the plan allows a `charset` parameter on `Content-Type: application/json`; add a test (`application/json; charset=utf-8` is accepted) that fails when the allowance is dropped.
2. **I-2**: pin the value checks that survive mutation: the `filters.kind`, `filters.scope`, and `filters.status` values (`ts/src/api/operations.ts:46-51`), a non-integer `limit` (`ts/src/api/args.ts:35`), and the `[name, text]` pair shape (`ts/src/api/args.ts:48`).
   Each gets a case in `arguments_are_checked` (or its own test) with the plan's sentence.
3. Minor, cheap: a test for the `Authorization` header with a scheme other than `Bearer` (answers `unauthorised`).

Leave the other minors alone (parked in the ledger).
In the report, state plainly which tests were written after the code and the mutation each was killed by (review I-3).
Do not stage any `*-codex-final.txt`.
Write `task-5-fix-1-report.md` in this folder: per item, the test with `file:line` and the mutation that fails it.
Commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, push `server-api-c`.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, with the commit hash.
