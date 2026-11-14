# Task 11, fix round 1 report

Implemented Important 1 and Minors 2 and 5 from `task-11-review.md`.

- The shared SQLite setup creates its project with owner `author` and records store writes as `author`, matching `wired(store)`. Updated owner, membership and event expectations and callers in the store tests.
- Added a SQLite regression through `wired(store)` that publishes a message by `author` and confirms an agent decision, checking both published outcomes and the stored identities.
- Moved the message impersonation refusal after reference resolution and the closed-thread refusal. Added unknown-reference checks for questions and replies, and a closed-thread reply check.
- Moved the agent confirmation refusal before the state read, after the words checks. Added a regression whose state reader throws if called.

## Test-first evidence

Before implementation, `bun test tests/store/people.test.ts tests/app/people.test.ts` gave 10 pass and 4 fail:

- The SQLite owner regression failed with `name a person of the project exactly, or use your own role`.
- The unknown-reference regression received `Forbidden` instead of `NotFound`.
- The closed-thread regression received `Forbidden` instead of `is closed`.
- The agent regression reached the state reader instead of refusing immediately.

After implementation, `bun test tests/app/people.test.ts tests/store` gave 77 pass and 0 fail.

## Final verification

`sh scripts/check-ts.sh` passed: Biome, TypeScript, dependency-cruiser, knip and the full suite, with 1238 pass, 2 todo and 0 fail. An initial full check found one formatting issue in the updated project tests; formatted it before the successful full run.

`git diff --check` passed. Changed TypeScript modules remain below 300 lines. No dependency was added.

Minors 1, 3 and 4 remain parked for Task 14 as requested. The pre-existing untracked Codex log is excluded from the commit.
