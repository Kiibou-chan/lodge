# Brief: fix round 1 for Task 10 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-roundtrip`, branch `server-import-roundtrip`; same rules as `task-10-brief.md` in this folder.
The Sonnet review is `~/.cache/lodge-work/codex/plan4/sonnet-task10-review.md`; fix only these, test-first (see each new test fail, by the mutation named).

1. Important I-1: the exit codes of `ts/scripts/round-trip.ts` are untested (`differences.length ? 1 : 0` changed to `? 0 : 0` passes all tests; the import-refused exit and the usage exit are untested too).
   Move the exit decision into an exported function the unit table asserts (0 on no other differences, 1 on any), and add subprocess cases that exit 1 (a wrong argument count, and a repository that holds no `lodge/` folder or a refused import).
   Each must fail against its mutation.
2. Minor: the script prints a line number where the plan says the first line that differs, and "line 1" with no side for a lone missing or extra path.
   Print the first differing line's text, and name the side (missing from the export, extra in the export) for a lone path.
3. Minor: `scripts/round-trip.sh` gets the `command -v bun` guard `scripts/check-ts.sh` has.
4. Left as is: `plan_4_changed_rows_keep_every_python_test_name` stays (the plan names it); the two mapping forms stay.

Run `sh scripts/check-ts.sh` last; commit with explicit paths, trailer `Co-Authored-By: Codex <noreply@openai.com>`, push the branch.
Write `task-10-fix-1-report.md` in this folder (each change, each test with the mutation it failed against, commands run) and commit it.
Final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests.
