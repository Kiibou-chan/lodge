# Task 8 report

Task 8 adds server imports and export targets, with the signed-in person's existing session and Origin checks.
All fixtures are synthetic, and every git repository used by the new tests is temporary and isolated.

## Changes by file

| File | Change |
| --- | --- |
| `ts/src/api/options.ts` | Adds the optional `moving` port and its public `Moving` interface. |
| `ts/src/api/moving.ts` | Implements import and export-target operations, argument validation, project lookup, import check results, target persistence, and notification rejection logging. |
| `ts/src/api/person.ts` | Registers and dispatches both operations after the existing person-only actor check. |
| `ts/src/api/index.ts` | Exports `Moving`, read by the API test world. |
| `ts/src/cli/settings.ts` | Extracts `tomlTable`, converting every top-level value, and retains the existing settings-name validation. |
| `ts/src/cli/zero-two.ts` | Rejects surrogate-escaped UTF-8 bytes and selects only the legacy core tables. |
| `ts/src/cli/index.ts` | Exports both TOML readers, consumed by tests, the legacy reader, and the composition root. |
| `ts/src/main.ts` | Composes git reading, TOML conversion, SQLite targets, exporters, wrapped projects, and lodges over the wrapper, and starts pending exports from `listen` only. |
| `ts/tests/api/world.ts` | Mirrors production composition, exposes the clock and export helpers, creates projects through the wrapper, and signs person requests with a synthetic session. |
| `ts/tests/api/import.test.ts` | Tests both layouts, author mapping, refusal cases, imported flags, settings forwarding, invalid TOML mapping, and absent moving wiring. |
| `ts/tests/api/export-target.test.ts` | Tests person access, validation, target persistence, published-write export, target removal, and rejection logging. |
| `ts/tests/cli/zero-two.test.ts` | Tests the legacy settings reader and conversion of every top-level TOML value. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-8-report.md` | Records implementation, red-test evidence, verification, and deviations. |

`importOperation` and `exportTargetOperation` are read by `person.ts`.
`Moving` is read by `world.ts`, `ApiOptions`, and the operation module.
`zeroTwoCoreTable` is read by `main.ts`, `world.ts`, and its tests.
`tomlTable` is read by `loadSettings`, `zeroTwoCoreTable`, and its direct conversion test.
The existing `ExportTarget` and `ExportOutcome` shapes match the structural argument and result types of `git/export.ts`, including committed, unchanged, and moved results.
No change to either shape was needed.

## Test-first evidence

The first required command ran before implementation and ended with `0 pass`, `19 fail`, and `1 error`.
The five initial CLI tests could not load because their export was absent.
The table uses final file handles, since formatting moved the original lines.

| file:line | Test or cases | First failure or failing mutation |
| --- | --- | --- |
| `ts/tests/api/import.test.ts:27` | `person_imports_the_made_up_store`, checkout and branch | `TypeError: undefined is not an object (evaluating 'w.clock.sleep')`. |
| `ts/tests/api/import.test.ts:52` | `agent_token_is_forbidden` | Missing `w.clock.sleep`, as above. |
| `ts/tests/api/import.test.ts:61` | `second_import_is_a_conflict` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:69` | `failing_store_answers_check_failed` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:70` | `project_without_the_sources_answers_check_failed` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:71` | `branch_layout_without_its_settings_fails_check_4` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:96` | `missing_revision_is_usage` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:97` | `unknown_field_is_usage` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:99` | `unknown_project_is_no_project` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:112` | `imported_records_read_as_imported` | Missing `w.clock.sleep`. |
| `ts/tests/api/import.test.ts:123` | `project_settings_survive_the_wrapper` | Missing `w.clock.sleep`; also failed against a mutation returning null for the proxy's `settings` method, with the expected sources table replaced by null. |
| `ts/tests/api/import.test.ts:129` | `invalid_settings_are_a_usage_error` | Mutating the world's `CliError` translation to throw plain `Error` produced `Expected: 400`, `Received: 500`. |
| `ts/tests/api/import.test.ts:140` | `server_without_moving_refuses`, import and export-target | Mutating the missing-wiring refusal to plain `Error` produced `Expected: 400`, `Received: 500` for both cases. |
| `ts/tests/api/export-target.test.ts:21` | `person_sets_the_target` | `TypeError: w.createProject is not a function`. |
| `ts/tests/api/export-target.test.ts:30` | `agent_token_is_forbidden` | Missing `w.createProject`, as above. |
| `ts/tests/api/export-target.test.ts:39` | `bad_target_is_usage` | Missing `w.createProject`. |
| `ts/tests/api/export-target.test.ts:53` | `unknown_project_is_no_project` | Missing `w.createProject`. |
| `ts/tests/api/export-target.test.ts:62` | `write_after_target_exports` | Missing `w.createProject`. |
| `ts/tests/api/export-target.test.ts:76` | `null_target_stops_the_export` | Missing `w.createProject`. |
| `ts/tests/api/export-target.test.ts:92` | `export_notification_rejection_is_logged` | Mutating the rejection handler to discard the error left the expected failure line absent from the log. |
| `ts/tests/api/export-target.test.ts:102` | `target_fields_are_checked`, absent target, array target, numeric repository, numeric branch, numeric remote, and unknown nested field | Mutating the operation to return success before target validation produced `Expected: 400`, `Received: 200` in all six cases. |
| `ts/tests/cli/zero-two.test.ts:5` | `core_tables_are_kept` | `SyntaxError: Export named 'zeroTwoCoreTable' not found`. |
| `ts/tests/cli/zero-two.test.ts:10` | `store_and_hook_are_ignored` | Missing `zeroTwoCoreTable` export, as above. |
| `ts/tests/cli/zero-two.test.ts:13` | `whole_number_float_is_refused_as_the_command_refuses_it` | Missing `zeroTwoCoreTable` export. |
| `ts/tests/cli/zero-two.test.ts:18` | `not_utf8_is_one_sentence` | Missing `zeroTwoCoreTable` export. |
| `ts/tests/cli/zero-two.test.ts:23` | `not_toml_is_one_sentence` | Missing `zeroTwoCoreTable` export. |
| `ts/tests/cli/zero-two.test.ts:27` | `toml_table_converts_every_top_level_value` | Mutating `tomlTable` to return raw parsed values failed equality for big integers, floats, dates, times, arrays, and nested values. |

Every mutation was reverted before validation.
The first logging and settings-translation mutation runs overlapped the proxy mutation and failed earlier on project lookup.
They were rerun individually to demonstrate the intended failures reported above.
Existing tests were retained unchanged, including `settings.test.ts`.

## Commands and outcomes

Commands below ran from the repository root unless prefixed with `cd ts`.
Read-only inspection used `cat`, `sed`, `rg`, `nl`, `wc`, and `git diff` to locate the required plan sections, inspect the implementation and fixtures, and review the changes.

| Command | Last lines or result |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author`, `nothing`; nothing awaited an agent either. |
| `git status --short --branch` | Confirmed `server-import-server` and an initially clean tree. |
| `cd ts && bun test tests/api/import.test.ts tests/api/export-target.test.ts tests/cli/zero-two.test.ts` before code | `0 pass`, `19 fail`, `1 error`, `Ran 19 tests across 3 files`. |
| The same focused command after implementation | Initially `18 pass`, `5 fail`, then `22 pass`, `1 fail`, while correcting assertions to the existing API shape and exact settings sentence. |
| `cd ts && bun test tests/cli/zero-two.test.ts -t toml_table_converts_every_top_level_value` against the conversion mutation | `0 pass`, `5 filtered out`, `1 fail`. |
| `cd ts && bun test tests/api/import.test.ts -t project_settings_survive_the_wrapper` against the proxy mutation | `0 pass`, `12 filtered out`, `1 fail`. |
| `cd ts && bun test tests/api/import.test.ts -t invalid_settings_are_a_usage_error` against the isolated translation mutation | `0 pass`, `12 filtered out`, `1 fail`. |
| `cd ts && bun test tests/api/export-target.test.ts -t export_notification_rejection_is_logged` against the isolated logging mutation | `0 pass`, `6 filtered out`, `1 fail`. |
| `cd ts && bun test tests/api/import.test.ts -t server_without_moving_refuses` against the refusal mutation | `0 pass`, `13 filtered out`, `2 fail`. |
| `cd ts && bun test tests/api/export-target.test.ts -t target_fields_are_checked` against the validation mutation | `0 pass`, `7 filtered out`, `6 fail`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings` with explicit changed TypeScript paths | Formatted the changes; remaining diagnostics were informational `useLiteralKeys` suggestions, which conflict with index-signature access required by TypeScript. |
| `cd ts && bunx --no-install tsc --noEmit -p .` | Final standalone run exited 0 with no output, after correcting test JSON decoding, index-signature access, and control-flow narrowing. |
| `cd ts && bun test tests/api tests/cli/zero-two.test.ts tests/cli/settings.test.ts` | `324 pass`, `0 fail`, `1873 expect() calls`, `Ran 324 tests across 26 files`. |
| `git diff --check` | Exited 0 with no output. |
| First `sh scripts/check-ts.sh` | Failed with `no-circular: src/api/moving.ts` through `options.ts`; resolved with the coordinator's ruling below. |
| Successful `sh scripts/check-ts.sh`, repeated last after completing this report | Exit 0; `2045 pass`, `0 fail`, `7089 expect() calls`, `Ran 2045 tests across 185 files`. |
| Commit with the supplied identity, explicit paths, and the Codex co-author trailer | Commits the implementation, tests, and this report on `server-import-server`. |
| `git push origin server-import-server` | Pushes the task branch to origin after the green gate. |

The complete gate includes Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip, and all Bun tests, including the structure tests.
No dependency was added or installed.
No Python source, Python tests, frozen documents, historical briefs, historical reports, or historical reviews were edited.

## Deviations and coordinator rulings

The plan header requested an unavailable `superpowers:subagent-driven-development` skill.
The coordinator answered: "A. Implement directly, test-first, no delegation."
No sub-agent was used.

The initial placement of `Moving` in `moving.ts` created a type-only import cycle with `options.ts`.
The coordinator ruled: "Define and export Moving in ts/src/api/options.ts beside ApiOptions (the plan names that file for the ApiOptions change), exported through #api; moving.ts holds only the operations. Public shape unchanged."
The implementation follows that ruling.

The brief's merged names and synthetic-session approach replace the plan's older names and passkey ceremony, as instructed.
The brief also authorises committing and pushing from this worktree, overriding the plan's sandbox prohibition.
Coordinator-only whole-project checks and integration steps were not performed.

The parked Task 6 notification rejection issue is handled by catches on the operation, wrapped-store notifications, and startup notification promise.
The operation's logging path has a regression test with a rejecting notification stub, without creating a failing git target or an endless fixed-clock retry.
The production startup and wrapper catches were reviewed directly, as the plan requires for `main.ts`.

Additional tests cover all top-level TOML conversion, nested target field types, unknown nested fields, absent moving wiring, and invalid settings error mapping.
The initial assertions guessed the search response to be an array, expected provenance in the default show response, and used "integer" instead of the existing "whole number" settings sentence.
Those assertions were corrected to the existing `result.items` envelope, the imported and unquoted flags, and the existing exact sentence, respectively.
The checkout success case omits `settingsRev` to exercise its default, while the branch success case supplies it explicitly.

## Uncertainty and review limits

No unresolved implementation question remains.
The production `main.ts` startup path is reviewed rather than imported by tests, as required by the plan.
It constructs exporters during open, starts them only in listen, uses the inner store for exporter reads, and gives the same wrapped projects to `ApiOptions` and `lodgesOver`.
The Git and application export shapes were checked against each other, and TypeScript accepts `exportStore` as the exporters' write port.
The parked sign-in-options challenge-cap issue and Bun's oversized-body response remain assigned to the final fix wave, with their implementation files untouched by this task.
