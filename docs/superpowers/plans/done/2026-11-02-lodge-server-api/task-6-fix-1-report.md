# Task 6 fix 1 report

The four security rules I-1 to I-4 now have regression tests killed by the review's mutations.
Person operations return `{ result, checkFailed }`, and the person's HTTP dispatch uses only `checkFailed` to select 422 or 200.
Missing setup now refuses session authentication with `unauthorised`, and passkey library messages reach `options.log` as JSON strings with escaped line breaks.

## Tests and mutation evidence

Every mutation below was applied individually, run against the named tests, observed failing, and restored.
The final source contains none of the mutations.

| Item | Test and handle | Mutation observed failing |
| --- | --- | --- |
| I-1 | `registration_requires_access`, `ts/tests/api/passkeys.test.ts:169`, both `register-options` and `register` | Delete `await sessionActor(options, request)` from `registrationAccess`: both cases fail with unauthorised access admitted. |
| I-2 | `register_with_the_setup_code_then_sign_in`, `ts/tests/api/passkeys.test.ts:5` | Remove the cookie from sign-in's answer: the cookie assertion fails. The test checks the full planned attributes and uses the cookie with `me`. |
| I-3 | `setup_code_uses_100_bits`, `ts/tests/api/setup-entropy.test.ts:5` | Change `& 31` to `& 15`: all four vectors fail. Swap alphabet characters: the full-alphabet vectors fail. Request 14 bytes instead of 13: the requested-length assertion fails. Limit the code to 19 characters: the exact-output assertion fails. |
| I-4 | `authorization_wins_on_ceremony`, `ts/tests/api/session.test.ts:68` | Delete registration's Authorization guard: register fails its expected 401. Delete sign-out's Authorization guard: sign-out fails its expected 403. Each test also checks that no passkey was added and the person's session remains live. The existing projects case remains at `ts/tests/api/session.test.ts:50`. |
| I-5 | `approval_failing_the_check_answers_422`, `ts/tests/api/person-drafts.test.ts:83`; successful approval assertion at `ts/tests/api/person.test.ts:123`; `person_may_call_record_operations`, `ts/tests/api/person.test.ts:58` | Replace the handler's `if (checkFailed)` with `if (false)`: the failed approval answers 200 and fails. Make approve return `checkFailed: false`: the same test fails. Make approve always return `checkFailed: true`: successful approvals fail their expected 200. |
| M-7 | `stale_cookie_without_setup_requires_sign_in`, `ts/tests/api/session.test.ts:87` | Restore the combined missing-setup/origin guard: projects answers 403 instead of 401. The test also asserts that `me` answers 200 with `{ setUp: false, signedIn: false }`. |
| M-9 | `library_log_escapes_line_breaks`, `ts/tests/api/passkeys.test.ts:184` | Remove `JSON.stringify` from the library-message log: the literal CR/LF assertion fails. Parsing the logged JSON must recover the library message containing the supplied origin; the response still holds only the fixed refusal sentence. |

The setup vectors include bytes 1 through 13, all bytes 255, and two fixed vectors covering every Crockford character.
They pin the 20-character output, four groups of five, full alphabet, 13-byte entropy request, and high-bit use.

## Test order

I-1 to I-4 tests were written against the existing correct implementation, run green, and then made red with the review's mutations before restoring the code.
Their underlying implementation predates these tests; no claim is made that these fixes introduced that implementation test-first.
The two full-alphabet vectors were added later, before their alphabet and mask mutation runs, with no setup implementation change.

The M-7 and M-9 tests were written and observed failing before changing their production code.
For I-5, a stand-in person-operation test and direct approve-result tests were written and observed failing before changing the return contract.
They passed after implementation, including add and message approval flag cases, but the gate rejected their direct internal import under the front-door rule.
Those tests were removed under the coordinator's ruling below.
The additional final assertions on the existing failed and successful approval tests were written after the I-5 implementation.
Their status mutations were then run and observed failing.
The existing approval and person-read tests predate this fix.

## Coordinator rulings

For M-7, the coordinator selected the missing-setup `unauthorised` refusal in `sessionActor`, projects answering 401, and `me` answering 200 through its existing unauthorised catch.
Both responses are tested.

For I-5, the front-door rule disallows the test importing `src/api/person.ts` directly.
The coordinator ruled: "No new seam: handler keeps its one-argument signature (plan 4 consumes it)."
The ruling explicitly directed dropping the stand-in test and pinning the flag through real HTTP approval requests instead, with plan 4 testing its own import operation.
Consequently, the requested stand-in test is absent from the final changes.
No new handler argument, public export, or dependency-rule exception was added.
The handler no longer inspects the person's result shape, and approve explicitly derives its flag from the add or message outcome.
Confirm derives its flag from its outcome; reads and other successful person operations set it false.

## Scope and validation

Implementation and test changes are confined to `ts/src/api/*` and `ts/tests/api/*`.
The named consumed interfaces and person dispatch remain in their original modules.
The review history, CLI, plan 4 files, M-6, M-10, and other minors are unchanged.
M-9 is limited to escaping the library message as requested; challenge caps and truncation were not added.
Unrelated pre-existing transcript files are excluded from the commit.

Final `sh scripts/check-ts.sh`: exit 0, 1569 pass, 2 todo, 0 fail.
Biome reported nine informational suggestions, TypeScript and the dependency checks passed, and `git diff --check` passed.
