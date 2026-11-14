# Task 4 recheck, fix round 1

Commit under recheck: 77993a1 against 1d57ad1 (`git diff 1d57ad1 77993a1`), probes in a scratch worktree at 77993a1, removed.
Test run there: 379 pass, 0 fail.

## Findings

- C-1 closed: `ts/src/core/yamlio.ts:96-98` and `:124-137` (a `built` memo set before the children).
  Run: the 510-byte header of nine anchors, ten aliases each, loads in 12 ms, `a8[0]` is `a7`; `a: &x [*x]` gives a list holding itself, as Python does.
  The test is `ts/tests/core/yamlio-fixes.test.ts:14-24` (two aliases per level, 1 s bound, identity assertion); it also failed on sharing before the fix, which is the stronger check.
- C-2 closed (ruling d-p48gr1): no new refusals; 13 tests pin each listed difference (`yamlio-fixes.test.ts:48-80`), and the report lists them.
  One correction to the review is recorded: `a: \x85b` keeps the U+0085 in TypeScript.
- C-3 closed: `yamlio.ts:55`; run, `a: b\nc: \x01\n` gives `unreadable character 1` at line 2 in both languages; test `yamlio-fixes.test.ts:25-27`.
- C-4 closed: `yamlio.ts:83`; run, `a: b\n  c: d` gives the bare message, line 1 (Python line 2 with a different message; the line comes from `error.pos` as the finding asked).
  The one changed line of `ts/tests/core/fileformat.test.ts:160` is a consequence of C-4 (see N-1).
- C-5 closed: `yamlio.ts:94-95` and `:83`; run, the three texts give lines 3, 4, 3, equal to Python's (messages differ, as before).
- C-6 closed by ruling d-v9mw2d; the report records the variables and Plan 3's obligation.
- C-7 closed: `yamlio.ts:110-114` and `:133-137`; run, `*x: y` and `a: *x` both give `found undefined alias 'x'` at line 1, as Python.
- M-1 closed: `stamps.test.ts:28` adds the negative.
- M-2 closed: `stamps.test.ts:36-37` adds 1900-02-29 and 2000-02-29.
- P-1 closed: `text.ts:4-8` module constants; `isPySpace` tests the first code point as before; the exhaustive whitespace test still passes.
- P-2 closed: `ids.ts:4`.
- P-3 closed: `model.ts:1` `WithDefaults`, used by all five functions.
- P-4 closed: the report lists the differences and says the Unicode counts were not remeasured.
- D-1 closed (ruling d-g1hrmn): `stamps.ts:49-51` `orderInstant`; run, a day sorts before `T00:30+00:00` of the same day and after `2026-10-28T23:30+00:00`; a non-date, an impossible day, an empty string, and a stamp without an offset throw `ValueError` (Python accepts the offset-less stamp, as before, since `isStamp` always required an offset; the ruling names neither).
  Tests: `order-instant.test.ts`, in one test function.
- D-2 closed as the review permits: listed as a known difference in the report.

## New problems

- N-1 · Minor · `ts/tests/core/fileformat.test.ts:160`: the case `a\n` of `bad_code_is_problem_1` now feeds an escaped newline, where Python's test feeds a literal one inside the quotes (`tests/core/test_fileformat.py:144`).
  The old input passed only because the package's excerpt contained the word `code`; with C-4 it fails with `Missing closing "quote` (the column-0 continuation difference of C-2), so the substitution is a consequence of C-4 and C-2 together and tests the same validation.
  No fix needed; Task 5a's differential dump (Task 12) covers the literal form.

## Counts

Closed 15 of 15, open 0; new Blocking 0, Important 0, Minor 1 (N-1).
