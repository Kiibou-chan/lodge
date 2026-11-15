# Task 6 recheck 1

Verdict: fix round 1 resolves I-1 to I-5, M-7, and M-9 within the fix brief's scope.
No new Important or Minor finding was found in `git diff 5635978 f928ce5`.
The uncapped challenge map and message truncation remain parked parts of the original M-9, as ruled by the coordinator during this recheck.

## Evidence and method

Read `CLAUDE.md` first, ran `lodge waiting` (nothing waiting), and read the review, fix brief, fix report, and the plan's Task 6 sentences.
Read every changed source and test file, the HTTP, authentication, session, and person dispatch, the test world and ceremony helpers, and the confirmation implementation.
The worktree's HEAD is `7d292e0`; its source and API tests have no difference from `f928ce5`.
The later commit adds the recheck brief only.

Ran all 13 mutations below individually against the actual worktree implementation.
Each file's original contents were held in memory and restored in a `finally` block immediately after its test run.
A `git diff --quiet -- <file>` check passed after each restoration.
Each mutant's named test invocation exited 1 because its assertion failed, rather than because of a syntax or import error.
The initial harness anchor check stopped before applying any mutation; the corrected harness then completed all 13 runs.

The command pattern was `cd ts && bun test tests/api/<file>.test.ts -t '<test name>'`.
Counts below describe only the selected tests in each mutation run.

| Finding | Verdict | Test read and mutation reproduced | Observed failure |
| --- | --- | --- | --- |
| I-1, Important | resolved | `ts/tests/api/passkeys.test.ts:169`, `registration_requires_access`; remove `sessionActor` from `registrationAccess` at `ts/src/api/passkeys.ts:53`. | Both register-options and register answer 200 instead of 401: 2 failures. |
| I-2, Important | resolved | `ts/tests/api/passkeys.test.ts:5`, `register_with_the_setup_code_then_sign_in`; remove the sign-in cookie at `ts/src/api/passkeys.ts:177`. | The cookie assertion receives null: 1 failure. |
| I-3, Important | resolved | `ts/tests/api/setup-entropy.test.ts:5`, `setup_code_uses_100_bits`; change `& 31` to `& 15` at `ts/src/api/setup.ts:29`. | All 4 exact-output vectors fail. |
| I-3, Important | resolved | Same test; swap alphabet characters 0 and 1 at `ts/src/api/setup.ts:19`. | 3 vectors fail, including both full-alphabet vectors; the all-Z vector passes. |
| I-3, Important | resolved | Same test; request 14 bytes at `ts/src/api/setup.ts:20`. | All 4 requested-length assertions fail. |
| I-3, Important | resolved | Same test; limit output to 19 characters at `ts/src/api/setup.ts:27`. | All 4 exact-output assertions fail. |
| I-4, Important | resolved | `ts/tests/api/session.test.ts:68`, `authorization_wins_on_ceremony`; delete registration's Authorization guard at `ts/src/api/passkeys.ts:52`. | Register answers 200 instead of 401: 1 failure, sign-out passes. |
| I-4, Important | resolved | Same test; delete sign-out's Authorization guard at `ts/src/api/passkeys.ts:179`. | Sign-out answers 200 instead of 403: 1 failure, register passes. |
| I-5, Important | resolved | `ts/tests/api/person-drafts.test.ts:83`, `approval_failing_the_check_answers_422`; replace `if (checkFailed)` with `if (false)` at `ts/src/api/http.ts:49`. | Real failed approval answers 200 instead of 422: 1 failure. |
| I-5, Important | resolved | Same failed-approval test; return `checkFailed: false` from approve at `ts/src/api/person.ts:120`. | Real failed approval answers 200 instead of 422: 1 failure. |
| I-5, Important | resolved | `ts/tests/api/person.test.ts:90`, `approve_makes_the_held_decision_current`; return `checkFailed: true` from approve at `ts/src/api/person.ts:120`. | Real successful approval answers 422 instead of 200: 1 failure. |
| M-7, Minor | resolved | `ts/tests/api/session.test.ts:87`, `stale_cookie_without_setup_requires_sign_in`; restore the combined missing-setup/origin guard at `ts/src/api/session.ts:13`. | Projects answers 403 instead of 401: 1 failure. |
| M-9, Minor | resolved within the brief's scope | `ts/tests/api/passkeys.test.ts:184`, `library_log_escapes_line_breaks`; remove `JSON.stringify` at `ts/src/api/passkeys.ts:66`. | The log contains literal CR/LF and fails the escaped-line assertion: 1 failure. |

## What the tests and implementation establish

I-1 covers both registration endpoints with no cookie and an unknown cookie, then a live cookie without Origin, and finally an expired cookie.
It asserts the fixed unauthorised response and checks that a missing Origin is forbidden.
I-2 checks every planned cookie attribute and sends the issued cookie to `me`, requiring the signed-in person in the result.
I-3 checks the independent bytes-1-to-13 vector, all ones, and vectors covering the full Crockford alphabet, as well as the 13-byte entropy request.
I-4 uses the world's real issued agent token alongside the person's cookie and valid registration data, then checks that the passkey count and live session survive both refused operations.
The existing projects precedence case remains at `ts/tests/api/session.test.ts:50`.

I-5 meets the coordinator's real-HTTP ruling.
`personOperation` returns `{ result, checkFailed }`, approve derives the flag from either the added or written outcome, and confirm derives it from its written outcome (`ts/src/api/person.ts:61`, `:104`, `:117`).
All other person operations return the same pair with a false flag.
The person branch of HTTP selects status from the flag alone (`ts/src/api/http.ts:48`); its result-shape inspection is gone.
The failed-approval test also pins the fixed error, the original Approved result without a leaked flag, the check-6 problem, and retention of the hold.
The successful approval test explicitly checks 200 at `ts/tests/api/person.test.ts:124`.
The existing person read test at `ts/tests/api/person.test.ts:58` checks that wrapping does not change the projects wire result.
`handler` still takes one argument, with no new test seam, front-door exception, or public export.
The report's superseded direct internal tests are absent, consistently with the ruling.

M-7 follows option A: missing setup is unauthorised before the Origin check (`ts/src/api/session.ts:13`).
The unmutated test checks both projects' 401 sentence and `me`'s 200 `{ setUp: false, signedIn: false }` response.
The mutation fails at its first projects assertion, so the later me assertions were assessed by reading and the passing unmutated gate.

M-9's test sends a real signed authentication response whose supplied origin contains CR/LF.
It verifies the fixed client refusal, exactly one log entry, no literal CR/LF, and JSON decoding back to the library message containing that origin.
The coordinator answered the scope question through `coord.ask_coordinator`: “A. Resolved within the fix brief's scope (line-break escaping); carry the uncapped challenge map and message truncation forward as a parked Minor, not a new finding.”
Those residuals remain at `ts/src/api/passkeys.ts:44` and `:65`; this verdict does not claim that the original resource-growth concern was fixed.

## New-problem scan and validation

No new Important or Minor problem found.
Read the complete diff against Task 6's ceremony, session, person-operation, and setup contracts and the hard rules in `CLAUDE.md`.
The new tests use synthetic fixtures, in-memory accounts and projects, software passkeys, and direct handler requests; they introduce no Git subprocess, real repository access, socket, or network call.
Production changes remain in API modules and use the existing options and ports.
No dependency, structure rule, limit, or consumed interface was loosened.
All source modules remain at most 300 lines; changed production files have 81, 184, 124, and 33 lines, and the largest changed test has 199 lines.
The changed report and fixtures contain no personal paths, machine names, credentials, or another project's records; the added Markdown uses British English, no em-dashes, and one sentence per line.

The fix report honestly records test order, including the retrospective assertions for already-correct I-1 to I-4 code and the final I-5 HTTP assertions.
This retains the previously recorded M-10 process limitation, which the brief explicitly leaves alone; mutation evidence does not establish historical test-first development.
No new test-order claim is inferred from a green gate.

After all restorations, `sh scripts/check-ts.sh` exited 0: 1569 pass, 2 todo, 0 fail, and 4043 assertions across 126 files.
Biome reported nine informational suggestions, TypeScript passed, dependency-cruiser found no violations, and knip passed.
`git diff --check 5635978 f928ce5` passed.
Before writing this report, `git status --short` showed only the five pre-existing untracked transcript files and no tracked-file changes.
After writing it, the only additional path is this uncommitted report; no source or test changes remain, and nothing was committed.

This is a recheck of the specified fix range, not a rerun of browser, socket, or whole-application acceptance checks.
