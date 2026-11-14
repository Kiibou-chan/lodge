# Task 4 report

Implemented event-backed accounts and project settings.
No coordinator checks were run, and no test opened a socket.

## Files

| File | Change |
|---|---|
| `ts/src/app/accounts.ts` | Added the four account interfaces, with readonly fields and the specified methods. |
| `ts/src/app/index.ts` | Exported the account interfaces. |
| `ts/src/app/ports.ts` | Extended Projects with optional settings, settings lookup, and names. |
| `ts/src/store/accounts.ts` | Implemented accounts with clock stamps, server events, ordered lists, and write-first transactions for conditional operations. |
| `ts/src/store/account-events.ts` | Added account event projections in a separate module to keep concerns and module sizes small. |
| `ts/src/store/events.ts` | Routed account events, projected project settings, and cleared all derived tables during rebuild. |
| `ts/src/store/schema.ts` | Added migration 2 and six derived tables, raising the schema to version 3. |
| `ts/src/store/projects.ts` | Stored settings atomically with project creation, returned settings, and sorted names by code point. |
| `ts/src/store/index.ts` | Exported SqliteAccounts. |
| `ts/tests/app/front-door.test.ts` | Allowed the four specified account exports. |
| `ts/tests/store/accounts.test.ts` | Added the twelve account tests below. |
| `ts/tests/store/project-settings.test.ts` | Added the five settings tests below. |
| `ts/tests/store/database.test.ts` | Updated version assertions, preserved the version-1 test name, and added the version-2 migration test with explicit historical SQL. |
| `ts/tests/store/projects.test.ts` | Updated the carried event assertion to include default settings. |
| This report | Recorded implementation, validation, and deviations. |

## Test-first evidence

All new account tests were written before the account module existed.
Their first run failed at module loading with `SyntaxError: Export named 'SqliteAccounts' not found`.
All settings tests failed with missing methods before implementation.
The migration tests failed with expected schema 3 and received schema 2.
The initial store run ended with 85 pass, 10 fail, and 1 error.

| file:line | Test | First failure or mutation |
|---|---|---|
| `ts/tests/store/accounts.test.ts:43` | `server_is_set_up_once` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:50` | `setup_code_is_spent_once` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:60` | `checking_a_setup_code_spends_nothing` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:67` | `setup_code_expires` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:76` | `newer_setup_code_replaces_older` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:84` | `passkeys_keep_their_counter` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:94` | `sessions_start_and_end` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:102` | `tokens_issue_list_and_revoke` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:113` | `revoked_token_keeps_its_revocation` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:122` | `no_event_holds_a_clear_secret` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:138` | `server_events_belong_to_no_project` | Missing SqliteAccounts export. |
| `ts/tests/store/accounts.test.ts:154` | `accounts_survive_reopening_and_rebuild` | Missing SqliteAccounts export. |
| `ts/tests/store/project-settings.test.ts:5` | `create_keeps_the_settings` | TypeError: projects.settings or projects.names is not a function. |
| `ts/tests/store/project-settings.test.ts:10` | `create_without_settings_keeps_none` | TypeError: projects.settings or projects.names is not a function. |
| `ts/tests/store/project-settings.test.ts:13` | `unknown_project_has_no_settings` | TypeError: projects.settings or projects.names is not a function. |
| `ts/tests/store/project-settings.test.ts:16` | `names_lists_the_projects` | TypeError: projects.settings or projects.names is not a function. |
| `ts/tests/store/project-settings.test.ts:21` | `settings_survive_rebuild` | TypeError: projects.settings or projects.names is not a function. |
| `ts/tests/store/database.test.ts:35` | `schema_is_created_once` | Expected schema 3, received schema 2; the newer-schema diagnostic likewise still named version 2. |
| `ts/tests/store/database.test.ts:49` | `newer_schema_is_refused` | Expected schema 3, received schema 2; the newer-schema diagnostic likewise still named version 2. |
| `ts/tests/store/database.test.ts:219` | `schema_1_is_migrated_to_2` | Expected schema 3, received schema 2; the newer-schema diagnostic likewise still named version 2. |
| `ts/tests/store/database.test.ts:220` | `schema_2_is_migrated_to_3` | Expected schema 3, received schema 2; the newer-schema diagnostic likewise still named version 2. |
| `ts/tests/store/projects.test.ts:12` | `create_writes_the_project_and_its_owner` | Removed settings from the project event body temporarily: 12 pass, 1 fail, at this assertion; restored immediately. |

The unchanged front-door tests and remaining store tests were carried through the full gate.
No parity rows belong to this task.

## Commands and results

| Command | Last lines or result |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| Repository and plan reads with `cat`, `sed`, and `rg` | Read the brief, CLAUDE.md, global constraints, interfaces, and Task 4. |
| `cd ts && bun test tests/store`, before implementation | 85 pass, 10 fail, 1 error. |
| `cd ts && bun test tests/store`, after implementation | 106 pass, 0 fail, 342 expect() calls. |
| `cd ts && bun x biome check --write .` | Formatting applied; three non-null assertion warnings subsequently removed. |
| `cd ts && bun x tsc --noEmit -p .` | Index-signature access errors corrected with an explicit event-body type. |
| `cd ts && bun test tests/store/projects.test.ts`, against the mutation | 12 pass, 1 fail. |
| Targeted `bun x biome check --write` | No remaining formatting issues. |
| `sh scripts/check-ts.sh`, final gate | Exit 0; 1320 pass, 2 existing todo, 0 fail, 3454 expect() calls. |

Temporary scripts generated the initial tests and implementation, and were kept outside the repository.
The final gate runs after the report is written.
The report and implementation are committed with explicit paths and pushed to the lane branch.

## Deviations and uncertainties

The account event projection lives in the additional module `account-events.ts`, called from `events.ts`, to keep projection details separate from the event log.
The derived account tables use an ID, an encoded JSON body, and the issue sequence, rather than separate columns for every interface field.
The plan specifies table names and observable behaviour, but no column layout.
Spending the newest setup code clears the derived code rows so that an older code cannot become valid again.
All original events remain append-only.
The newer-schema diagnostic test also changes from 2 to 3, as required by the new schema version.

No dependencies were added.
No unresolved concerns.
