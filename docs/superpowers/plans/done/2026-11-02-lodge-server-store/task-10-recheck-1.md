# Task 10 recheck 1

Diff `cc2cf0d..024ec5c`; findings C-I1, C-M1, C-M2 only.

## C-I1: fixed
`ts/tests/core/people-regressions.test.ts` adds the nine tests named in the finding, plus `person_message_writes_a_quoted_minute` for the written minute (`:70-73`).
In a detached scratch worktree each of the ten sites was reverted to author-only in turn, and each made `bun test tests/core` fail:
`derive.ts:105` (1 fail), `:118` (1), `:124` (1), `:203` (1), `:206` (1), `:211` (3), `confirmation.ts:20` (1), `feedback.ts:92` (1), `:96` (1), `threads.ts:127` (1).
The scratch worktree is removed.

## C-M1: fixed
`ts/src/core/confirmation.ts:62` quotes a non-plain `decided_by` and keeps `decided_by: author` plain.
`ts/tests/core/people.test.ts:102-118` covers `a: b` and `#ada`, asserts the quoted bytes, and round-trips through `parseRecord`.

## C-M2: fixed
`ts/tests/core/people.test.ts:96` asserts `the thread would not read back: a message by ada needs where`.

## Other checks
- `sh scripts/check-ts.sh` exits 0 (951 pass, 0 fail, structure tests included).
- Core rules: the only new regex is u-flagged; no new `catch`, `ok` key, or `sort` in the diff.
- Only the fix report was added under docs; no earlier brief, report, or review was edited; the branch is untouched.

## New problems
None Blocking or Important.
Minor: `confirmation.ts:62` repeats `PLAIN` from `fileformat.ts:71` as an inline literal; two copies can drift.

Blocking 0, Important 0.
