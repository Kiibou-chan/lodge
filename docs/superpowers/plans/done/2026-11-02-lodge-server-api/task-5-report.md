# Task 5 report

Implemented the API handler, record operations, project creation, bearer authentication, token issuance, and wire encoding on `server-api-c`.

## Changes per file

| File | Change |
|---|---|
| `ts/package.json` | Added the `#api` front door without changing dependencies. |
| `ts/src/api/index.ts` | Exported exactly the specified handler, options, Lodge factory, wire encoder, and token helpers. |
| `ts/src/api/options.ts` | Defined `ApiOptions` and `lodgesOver`, sharing actor-aware Lodge construction between the handler's tests and the future program. |
| `ts/src/api/http.ts` | Added path-first routing, method and JSON checks, response headers, error handling, and complete 422 write results. |
| `ts/src/api/errors.ts` | Mapped application error classes and HTTP statuses, keeping unexpected failures in the supplied log. |
| `ts/src/api/wire.ts` | Encoded nested maps and sets in iteration order, omitted undefined object properties, and rejected unsupported values and reserved keys. |
| `ts/src/api/args.ts` | Added field validation for strings, nullable strings, booleans, positive whole numbers, objects, pairs, choices, and unknown fields. |
| `ts/src/api/operations.ts` | Dispatched all sixteen record operations with their defaults and options, validated filters, and created projects with validated settings and the configured person as owner. |
| `ts/src/api/auth.ts` | Authenticated hashed bearer tokens, rejected revoked credentials, and enforced the token's project. |
| `ts/src/api/tokens.ts` | Issued base64url secrets, spelled token IDs, stored SHA-256 hashes, and stamped token metadata. |
| `ts/tests/api/world.ts` | Added an awaited in-memory database, fixed clock, counting IDs and entropy, setup option, configured person, project, token, request builder, and log collector. |
| `ts/tests/api/operation-cases.ts` | Listed every record operation's default arguments and corresponding Lodge method. |
| `ts/tests/api/handler.test.ts` | Covered routing, JSON validation, headers, and internal-error redaction. |
| `ts/tests/api/wire.test.ts` | Covered primitive, ordered, nested, omitted, and unsupported wire values. |
| `ts/tests/api/bearer.test.ts` | Covered credentials, revocation, project restrictions, token storage, hashing, metadata, and ID spelling. |
| `ts/tests/api/operations.test.ts` | Covered all operation defaults, invalid arguments, application errors, actor roles, and missing projects. |
| `ts/tests/api/project-create.test.ts` | Covered persisted settings, settings refusal, duplicate and invalid names, ownership, and missing setup. |
| `ts/tests/api/write.test.ts` | Covered a real failed add without publication and an agent's relayed message held for approval without a current thread. |
| `ts/tests/api/explicit.test.ts` | Covered explicit options and complete failed-check results for all four writing operations. |

## Test-first evidence

No tests were carried from another task or changed outside the new API directory.
All initial tests were written and run before the API existed.
Their first failing output was `Cannot find package '#api'`, with zero passing tests and one module failure per test file.
The parameterised rows below include every case in their referenced table.

| file:line | Tests | First failure or mutation |
|---|---|---|
| `ts/tests/api/handler.test.ts:5` | `post_only`, `json_only`, `body_must_be_json`, `body_must_be_an_object`, `unknown_operation_is_not_found`, `other_paths_are_not_found` | Missing `#api`. |
| `ts/tests/api/handler.test.ts:49` | `every_answer_carries_the_version_and_no_store` | Missing `#api`. |
| `ts/tests/api/handler.test.ts:64` | `unexpected_error_is_internal_without_detail` | Missing `#api`. |
| `ts/tests/api/wire.test.ts:4` | `plain_values_pass` | Missing `#api`. |
| `ts/tests/api/wire.test.ts:7` | `maps_and_sets_are_tagged_in_order` | Missing `#api`. |
| `ts/tests/api/wire.test.ts:23` | `nested_values_are_encoded` | Missing `#api`. |
| `ts/tests/api/wire.test.ts:28` | `undefined_properties_are_left_out` | Missing `#api`. |
| `ts/tests/api/wire.test.ts:31` | `unsupported_values_throw`, seven cases | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:5` | `no_credentials_is_unauthorised`, `unknown_token_is_unauthorised` | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:15` | `revoked_token_is_unauthorised` | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:21` | `token_reaches_only_its_project` | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:30` | `token_may_create_its_own_project_only` | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:43` | `issued_token_is_stored_as_its_hash` | Missing `#api`. |
| `ts/tests/api/bearer.test.ts:81` | `token_id_is_spelled_as_an_id` | Missing `#api`. |
| `ts/tests/api/operations.test.ts:7` | `each_operation_reaches_lodge`, sixteen operations | Missing `#api`. |
| `ts/tests/api/operations.test.ts:29` | `arguments_are_checked`, twelve cases | Missing `#api`. |
| `ts/tests/api/operations.test.ts:49` | `app_errors_map_to_kinds`, five classes | Missing `#api`. |
| `ts/tests/api/operations.test.ts:69` | `token_role_is_the_actor` | Missing `#api`. |
| `ts/tests/api/operations.test.ts:86` | `unknown_project_is_no_project` | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:15` | `project_create_records_the_settings` | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:25` | `project_create_checks_the_settings`, three cases | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:37` | `project_create_twice_is_already_initialised` | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:47` | `project_name_is_checked` | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:56` | `project_create_makes_the_person_owner` | Missing `#api`. |
| `ts/tests/api/project-create.test.ts:62` | `project_create_before_setup_is_usage` | Missing `#api`. |
| `ts/tests/api/write.test.ts:16` | `failed_check_answers_422_with_the_result` | Missing `#api` through `world.ts`. |
| `ts/tests/api/write.test.ts:29` | `agents_relay_is_held` | Missing `#api` through `world.ts`. |
| `ts/tests/api/explicit.test.ts:6` | `explicit_arguments_reach_lodge`, ten cases | Inserted `throw new Error("synthetic operation mutation")` immediately before Lodge construction in `operate`; expected 200, received 500. |
| `ts/tests/api/explicit.test.ts:89` | `whole_failed_result_is_preserved`, four writes | Same mutation; expected 422, received 500. |

The mutation run finished with `0 pass`, `14 fail`, and `14 expect() calls`.
The mutation was reverted before validation.
Initial implementation checks also exposed incorrect test cleanup using `destroy` instead of the database's `close`, and a thread-list assertion using `threads` instead of `items`.
Both test mistakes were corrected without changing their behavioural assertions.
TypeScript identified index-signature access and unknown JSON values, which were corrected before the gate passed.

## Commands and results

| Command | Result or last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `git status --short --branch` | Confirmed `server-api-c`; two pre-existing Task 4 output files were left untouched. |
| `cat`, `sed`, and `rg` reads | Read the brief first, then `CLAUDE.md`, the required plan sections, core constraints, existing interfaces, fixtures, and structure rules. |
| `cd ts && bun test tests/api`, before implementation | Missing `#api`; the final initial run reported `0 pass`, `6 fail`, and `6 errors`. |
| `cd ts && bun test tests/api/explicit.test.ts`, with mutation | `0 pass`, `14 fail`, and `14 expect() calls`. |
| `cd ts && bunx biome check --write src/api tests/api package.json` | Formatted the new API source and tests; no warnings or errors. |
| `cd ts && bunx biome check --write tests/api/explicit.test.ts` | `Checked 1 file`, `Fixed 1 file`. |
| `cd ts && bunx tsc --noEmit -p .` | Exit 0 after the type corrections. |
| `cd ts && bun test tests/api` | `85 pass`, `0 fail`, `204 expect() calls`, across seven test files. |
| `sh scripts/check-ts.sh` | Exit 0; `1480 pass`, `2 todo`, `0 fail`, `3796 expect() calls`, across 119 test files. |

The gate includes Biome with warnings fatal, TypeScript, dependency-cruiser, knip, and all Bun tests including structure checks.
Biome's literal-key suggestions are informational and also occur in existing CLI code.
No test opened a socket, no dependency was added, and no CLI file was changed.

## Deviations and uncertainties

Added `options.ts` to keep shared interfaces and Lodge construction independent of HTTP routing.
Split project-creation and write tests into their own files, and put the operation table in a helper, keeping each module comfortably within 300 lines.
Added `explicit.test.ts` after implementation and verified its first failures against the documented temporary mutation.
Used the brief's explicit permission to commit and push this lane, overriding the older sandbox-only coordinator instructions.
The unavailable superpowers sub-skill named by the plan header was not used; the task was implemented directly with test-first verification.
No behaviour or interface deviation is known, and no unresolved implementation uncertainty remains.
The two existing todo tests remain unchanged.
