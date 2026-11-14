# Task 11, fix round 1

Worktree `/var/tmp/lodge-server-store`, branch `server-store`.
Read `task-11-review.md` in this folder; fix the findings below, test-first, and keep every existing test passing.
Do not dispatch subagents.

1. Important 1: make the plan's sentence true, that every `Lodge` of the store tests acts as `person("author")`, the owner of their project.
   Create the project in `ts/tests/store/support.ts` with owner `author`, move the `ada` expectations in `ts/tests/store/people.test.ts` (and any other store test that relies on `ada` through `setup()`) to match, and add one store test over `wired(store)` showing that `confirm` and a message `by: "author"` are not refused over the SQLite store (see the review's probe); see it fail against the old setup first.
2. Minor 2: move the `Forbidden` check of `ts/src/app/threads.ts:95` beside the closed-thread refusal (`:117`), so that an unknown reference gives `NotFound` and a closed thread `is closed` before `Forbidden`; add one test for each order.
3. Minor 5: in `ts/src/app/confirm.ts`, put the `agent` refusal before the state read, with the other checks that need no state.

Minors 1, 3, and 4 stay parked for Task 14.
Hard rules: modules at most 300 lines, British English, no em-dashes, no new dependency, run `sh scripts/check-ts.sh`.
Write `task-11-fix-1-report.md` in this folder, commit with explicit paths (trailer `Co-Authored-By: Codex <noreply@openai.com>`), and push `server-store`.
