# Task 11 recheck 1 (fix 2e22a53)

Scratch worktree `/var/tmp/lodge-review-11b` at 2e22a53, removed afterwards.

## Findings

- Important 1: answered.
  `ts/tests/store/support.ts:14-15` creates the project and the store with owner `author`; the `ada` expectations in `ts/tests/store/people.test.ts` and the five other store files follow.
  The new `the_wired_owner_confirms_and_writes_as_author` (`ts/tests/store/people.test.ts:31`) confirms and writes `by: "author"` over SQLite and checks the stored identities.
  With the old `support.ts` restored, `bun test tests/store` fails it and four owner-dependent tests (5 fail); with the fix, 0 fail.
- Minor 2: answered.
  The `Forbidden` check now sits after the reference and closed-thread refusals (`ts/src/app/threads.ts:118-119`).
  With `ts/src` reverted to a77c051, `unknown_reference_is_refused_before_impersonation` and `closed_thread_is_refused_before_impersonation` fail; with the fix they pass.
- Minor 5: answered.
  The `agent` refusal precedes `readState` (`ts/src/app/confirm.ts:52-53`); `an_agent_is_refused_before_reading_state` fails on the old source (reads reached) and passes now.

## Checks

- `sh scripts/check-ts.sh` in the scratch worktree: exit 0, 1238 pass, 2 todo, 0 fail.
- Touched files stay at most 201 lines (`threads.ts`) and 172 (`database.test.ts`); no em-dash and British English in the added lines.
- Source diff is two moved lines; test changes only rename `ada` to `author` and add tests, nothing weakened.
- No new problem found; Minors 1, 3, and 4 remain parked for Task 14 as briefed.

Verdict: 0 Blocking, 0 Important, 0 Minor
