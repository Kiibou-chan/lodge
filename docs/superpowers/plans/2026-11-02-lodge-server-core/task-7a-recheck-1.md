# Task 7a recheck of fix round 1

Rechecker: `rechecker`, against commit 5a24b52 (`git diff a54f486 5a24b52 -- ts/`), in a detached scratch worktree, since removed.
`bun test tests/core` at 5a24b52: 548 pass, 1 todo, 0 fail.
Each mutation below was applied alone to `ts/src/core/derive.ts`, run against all of `tests/core`, and reverted.

## Verdict

Closed 6 (C-1, C-2, C-3, P-1, P-2, D-1), open 0, handed over 1 (D-2).
No new Blocking or Important problem.

## Findings

- C-1: closed.
  `ts/tests/core/derive.test.ts:190-203`, `orders_by_instant_across_offsets_then_by_id`, builds the snapshot in memory through `builders.snapshotOf` in reverse ID order.
  Tie-break dropped (`return at - bt;`, `derive.ts:33`): that test fails, 547 pass.
  Date compared as text (`byCodePoint(a.date, b.date) || byCodePoint(ai, bi)`): that test fails, 547 pass.
  Tie-break reversed: `changed_by_newest_first` and the new test fail.
- C-2: closed.
  `ts/tests/core/derive-links.test.ts:3` and `ts/tests/core/doubts.test.ts:12` import `snapshotOf` from `./builders.ts` and pass arrays; `ts/tests/core/derivation.ts:7` is back to `(Record | Area)[]`.
  Supports sort dropped (`derive.ts:130`, `s.entries.keys()`): `supports_is_the_reverse_of_rests_on` fails, 547 pass.
- C-3: closed, no code change was asked; the report's evidence is now mutations inside the logic.
- P-1: closed.
  The `Derived` contract is a comment at `derive.ts:8-11`, with one-line comments on `countsFor` and `flagged` (`derive.ts:159`, `183`).
  The `flagged` comment sits above the function and says what is skipped.
- P-2: closed.
  `doubts.ts:28` asserts `as Decision`, the optional chain is gone, and `derive.test.ts:172` writes `files`.
- D-1: closed (the fix took the first option).
  `derive-review.ts` is deleted, `derive.ts` is 238 lines, and `cleared` and `followsAuthorChange` are their own functions (`derive.ts:216`, `229`).
  `cleared` now compares through `compare(target, later) < 0` rather than an index map; dropping the comparison (`true`) fails `confirm_dated_before_does_not_clear`, so the new form is held by a test.
- D-2: handed over to the other fix round by ruling d-qe513h.
  `compare` is still private (`derive.ts:30`), and C-1's test now pins its ordering for whichever way Task 7b reuses it.

## New problems

None Blocking or Important.
`derive.test.ts:192` declares a local `at` that shadows the imported `at` from `builders.ts` inside that one test; harmless, and the file's other tests use the import, so a Minor at most.
