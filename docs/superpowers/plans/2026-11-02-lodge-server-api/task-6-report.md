# Task 6 report

Implemented passkey registration and sign-in, person sessions and operations, and the server setup and serve commands.
The work stays on `server-api-c`, and no file under `ts/src/cli` changed.

## Changes per file

| File | Change |
|---|---|
| `ts/src/api/passkeys.ts` | Public ceremony dispatch, stable SHA-256 user handles, required user verification, passkey counters, five-minute single-use challenges, setup-code validation and spending, fixed refusals, and session creation. |
| `ts/src/api/session.ts` | Hashed 32-byte sessions, thirty-day expiry, strict secure cookies, exact Origin checks, and sign-out. |
| `ts/src/api/person.ts` | Token and project operations, confirmation, person-filtered holds, core-parsed draft summaries, approval, and decline. |
| `ts/src/api/setup.ts` | Exported server interfaces, argument validation, fixed setup identity, Crockford setup codes with hashed fifteen-minute expiry, and injected serving. |
| `ts/src/api/auth.ts` | Cookie authentication and bearer precedence, with optional project scoping for person-only dispatch. |
| `ts/src/api/http.ts` | Ceremony and person dispatch, session response cookies, and nested approval check failures as HTTP 422. |
| `ts/src/api/index.ts` | Exported `ServerParts`, `ServerIo`, `serverCommand`, and `issueSetupCode`. |
| `ts/src/api/webcrypto.d.ts` | Node Web Crypto aliases needed by the dependency's X.509 declarations under strict TypeScript without the DOM library. |
| `ts/knip.json` | Removed the WebAuthn dependency exception now that the API imports it. |
| `ts/.dependency-cruiser.cjs` | Enabled package export resolution with runtime conditions so the published WebAuthn helper subpath resolves. |
| `ts/tests/api/authenticator.ts` | Carried the software authenticator, using ArrayBuffer-backed byte buffers, with adjustable user verification, counter, and origin. |
| `ts/tests/api/signed.ts` | Shared in-memory ceremony and seeded session fixtures. |
| `ts/tests/api/person-fixtures.ts` | Shared synthetic decision and document text. |
| `ts/tests/api/passkeys.test.ts` | Registration, authentication, expiry, replay, origin, verification, counter, normalisation, and user-handle tests. |
| `ts/tests/api/session.test.ts` | Cookie attributes, hashing, expiry, sign-out, Origin enforcement, bearer precedence, and identity tests. |
| `ts/tests/api/person.test.ts` | Token lifecycle, project isolation, agent refusals, confirmation, person reads, and held add settlement tests. |
| `ts/tests/api/person-messages.test.ts` | Held message presentation, publication, and decline tests. |
| `ts/tests/api/person-drafts.test.ts` | Core-parsed summaries, edit and invalid drafts, and approval rechecking tests. |
| `ts/tests/api/setup.test.ts` | Setup output, replacement codes, fixed identity, validation, serving, and usage tests. |
| `docs/superpowers/plans/2026-11-02-lodge-server-api/task-6-report.md` | This report. |

## Test-first evidence

Before implementation, `bun test tests/api` reported `94 pass`, `6 fail`, and `6 errors`.
Each new test module failed to load with `SyntaxError: Export named 'issueSetupCode' not found`, or the missing `serverCommand` export for setup.
The shared fixture imports the missing export, so this is the first failure for each test listed as E1 below.
The software authenticator is carried test support, exercised by the ceremony tests rather than an independent test.
No pre-existing test was changed.

The later supplementary tests were checked against named mutations, individually for M1 to M4, and the mutations were reverted.

| Evidence | First failing output or mutation |
|---|---|
| E1 | Missing Task 6 exports, as above. |
| M1 | Changed challenge lifetime from 300,000 ms to 299,000 ms, producing `0 pass`, `1 fail` at the 299-second success boundary. |
| M2 | Removed challenge deletion, producing `0 pass`, `1 fail` when a signed-in registration response was replayed. |
| M3 | Removed setup-code lower-casing and separator stripping, producing `0 pass`, `1 fail`. |
| M4 | Shifted the SHA-256 user-handle slice from bytes 0 to 15 to bytes 1 to 16, producing `0 pass`, `1 fail`. |
| M5 | Authenticated person-only operations against the empty project instead of omitting project scoping, producing a project error rather than the required person-only refusal. |

| file:line | Test or parameterised cases | First failure |
|---|---|---|
| `ts/tests/api/passkeys.test.ts:5` | `register_with_the_setup_code_then_sign_in` | E1 |
| `ts/tests/api/passkeys.test.ts:16` | `setup_code_is_spent_by_registration` | E1 |
| `ts/tests/api/passkeys.test.ts:17` | `wrong_setup_code_is_refused` | E1 |
| `ts/tests/api/passkeys.test.ts:18` | `setup_code_lasts_15_minutes` | E1 |
| `ts/tests/api/passkeys.test.ts:30` | `setup_code_expires_at_15_minutes` | E1 |
| `ts/tests/api/passkeys.test.ts:37` | `wrong_challenge_is_refused` | E1 |
| `ts/tests/api/passkeys.test.ts:38` | `challenge_is_spent_on_use` | E1 |
| `ts/tests/api/passkeys.test.ts:39` | `challenge_lasts_5_minutes` | E1 |
| `ts/tests/api/passkeys.test.ts:40` | `other_origin_is_refused` | E1 |
| `ts/tests/api/passkeys.test.ts:41` | `user_verification_is_required` | E1 |
| `ts/tests/api/passkeys.test.ts:42` | `refusal_does_not_echo_the_library` | E1 |
| `ts/tests/api/passkeys.test.ts:66` | `register_options_keep_one_user_id` | E1 |
| `ts/tests/api/passkeys.test.ts:81` | `counter_going_back_is_refused` | E1 |
| `ts/tests/api/passkeys.test.ts:82` | `sign_in_requires_user_verification` | E1 |
| `ts/tests/api/passkeys.test.ts:83` | `sign_in_challenge_is_spent` | E1 |
| `ts/tests/api/passkeys.test.ts:84` | `sign_in_challenge_expires` | E1 |
| `ts/tests/api/passkeys.test.ts:100` | `signed_in_person_adds_a_passkey` | E1 |
| `ts/tests/api/passkeys.test.ts:113` | `registration_challenge_expires_between_options_and_response` | M1 |
| `ts/tests/api/passkeys.test.ts:121` | `signed_in_registration_cannot_reuse_a_challenge` | M2 |
| `ts/tests/api/passkeys.test.ts:132` | `setup_code_is_normalised_and_stored_as_a_hash` | M3 |
| `ts/tests/api/passkeys.test.ts:145` | `registration_user_handle_is_the_origin_and_person_hash` | M4 |
| `ts/tests/api/session.test.ts:5` | `cookie_is_http_only_secure_and_strict` | E1 |
| `ts/tests/api/session.test.ts:13` | `session_is_stored_as_its_hash` | E1 |
| `ts/tests/api/session.test.ts:21` | `session_lasts_30_days` | E1 |
| `ts/tests/api/session.test.ts:30` | `sign_out_ends_the_session` | E1 |
| `ts/tests/api/session.test.ts:40` | `cookie_request_needs_this_servers_origin` | E1 |
| `ts/tests/api/session.test.ts:48` | `authorization_makes_an_agent_request` | E1 |
| `ts/tests/api/session.test.ts:56` | `me_says_who_is_signed_in` | E1 |
| `ts/tests/api/person.test.ts:7` | `token_issue_shows_the_secret_once` | E1 |
| `ts/tests/api/person.test.ts:19` | `issued_token_works_for_its_project` | E1 |
| `ts/tests/api/person.test.ts:19` | `revoked_token_stops_working` | E1 |
| `ts/tests/api/person.test.ts:49` | `person_operations_refuse_an_agent_token` | E1 |
| `ts/tests/api/person.test.ts:58` | `person_may_call_record_operations` | E1 |
| `ts/tests/api/person.test.ts:64` | `confirm_writes_the_persons_confirmation` | E1 |
| `ts/tests/api/person.test.ts:90` | `approve_makes_the_held_decision_current` | E1 |
| `ts/tests/api/person.test.ts:91` | `decline_closes_the_hold` | E1 |
| `ts/tests/api/person.test.ts:92` | `held_lists_what_waits_for_the_person` | E1 |
| `ts/tests/api/person.test.ts:137` | `global_person_operations_refuse_tokens_without_a_project` | M5 |
| `ts/tests/api/person-messages.test.ts:6` | `held_lists_a_relayed_message` | E1 |
| `ts/tests/api/person-messages.test.ts:7` | `approve_publishes_the_relayed_message` | E1 |
| `ts/tests/api/person-messages.test.ts:8` | `decline_drops_the_relayed_message` | E1 |
| `ts/tests/api/person-drafts.test.ts:24` | `held_shows_the_drafts_as_core_reads_them` | E1 |
| `ts/tests/api/person-drafts.test.ts:83` | `approval_failing_the_check_answers_422` | E1 |
| `ts/tests/api/setup.test.ts:30` | `setup_prints_a_code` | E1 |
| `ts/tests/api/setup.test.ts:38` | `setup_again_before_a_passkey_gives_a_new_code` | E1 |
| `ts/tests/api/setup.test.ts:46` | `setup_after_a_passkey_is_refused` | E1 |
| `ts/tests/api/setup.test.ts:63` | `setup_fixes_origin_and_person` | E1 |
| `ts/tests/api/setup.test.ts:76` | `setup_refuses_a_bad_origin` | E1 |
| `ts/tests/api/setup.test.ts:82` | `setup_refuses_a_bad_person` | E1 |
| `ts/tests/api/setup.test.ts:90` | `serve_needs_setup` | E1 |
| `ts/tests/api/setup.test.ts:96` | `serve_listens_where_told` | E1 |
| `ts/tests/api/setup.test.ts:113` | `server_usage_errors_exit_2` | E1 |

All parameterised cases in the named declarations are included, covering eight person-only operations, both missing and foreign origins, five invalid setup origins, two invalid person names, and six malformed argument lists.

## Commands and outcomes

| Command | Last lines or result |
|---|---|
| `uv run --frozen --quiet lodge waiting` | `waiting for the author`, `nothing`, with nothing waiting for an agent either. |
| `bun test tests/api`, before implementation | `94 pass`, `6 fail`, `6 errors`, `Ran 100 tests across 13 files`. |
| `bun test tests/api`, first implementation | `130 pass`, `29 fail`, revealing timestamp format and fixture issues. |
| `bun test tests/api`, after timestamp corrections | `158 pass`, `1 fail`, isolating the approval fixture. |
| `bun test tests/api`, after the approval fixture correction | `159 pass`, `0 fail`, `394 expect() calls`. |
| `bun test tests/api/passkeys.test.ts -t <mutation test>` | Each of M1 to M4 individually ended `0 pass`, `1 fail`. |
| `bun test tests/api/passkeys.test.ts tests/api/person.test.ts`, combined mutation run | Included the M5 refusal failure, with mutations subsequently reverted. |
| `bunx biome check --write src/api tests/api knip.json` | Formatting applied, with informational literal-key suggestions only. |
| `bunx tsc --noEmit -p .` | Exit 0 after adding the Web Crypto declaration aliases. |
| `bunx knip` | Exit 0. |
| `bun test tests/api`, supplementary tests included | `164 pass`, `0 fail`, `408 expect() calls`. |
| `git diff --check` | Exit 0. |
| `sh scripts/check-ts.sh`, initial gate | Unresolvable WebAuthn helper subpath in dependency-cruiser. |
| `sh scripts/check-ts.sh`, first resolver fix | `1558 pass`, `2 todo`, `1 fail`, because the `types` condition changed an existing YAML resolution expectation. |
| `sh scripts/check-ts.sh`, runtime resolver conditions | `1559 pass`, `2 todo`, `0 fail`, `4000 expect() calls`, `Ran 1561 tests across 125 files`, exit 0. |

The final gate was rerun after this report was written and exited 0 with the same totals.
All tests run in process without sockets.
No dependency was added, and neither the lockfile nor the CLI was changed.

## Deviations and uncertainties

- Added `webcrypto.d.ts` because importing the required library exposes X.509 declarations that name Web Crypto globals absent from the ES-only TypeScript configuration.
  These aliases preserve strict checking and do not enable `skipLibCheck` or add DOM globals unrelated to cryptography.
- Enabled dependency-cruiser's package export resolution because the required helper import exists only through the dependency's `exports` map.
  No forbidden edge, limit, or severity changed.
  Runtime conditions omit `types`, preserving the existing YAML dependency expectation.
- Split person tests into message and draft modules and added shared fixtures for clarity and the 300-line limit.
  Approval dispatch remains in `person.ts` for plan 4.
- `operations.ts` needed no modification because person operations dispatch before the unchanged record operations.
- The approval recheck fixture edits the entry through the store and publishes a retirement decision through that store in the same write.
  Editing an entry alone cannot trigger check 6, which specifically rejects a new dependency on a retired entry.
  The test asserts check 6, HTTP 422, and that the hold stays open.
- The plan header names the unavailable `superpowers:subagent-driven-development` skill.
  Implementation was performed directly, retaining the prescribed test-first sequence.
- The existing two todo tests remain unchanged, and Biome reports informational literal-key suggestions without warnings or errors.
  No blocking uncertainty remains.
