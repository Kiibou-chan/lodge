# Task 9 report

Implemented the hook command, its context, carried command tests, and the five parked Task 4 minors on `server-import-hook`.

## Changes by file

| File | Change |
| --- | --- |
| `ts/src/cli/hook-context.ts` | Find the edited file's repository through injected git functions, read settings strictly as UTF-8 bytes, parse hook settings, recognise moved projects and branch mode, and return null on errors |
| `ts/src/cli/commands.ts` | Add optional `Io.hook`, dispatch before settings, ignore unknown events, and return the hook port's result |
| `ts/src/cli/grammar.ts` | Add the hook command and the early event parsing rule |
| `ts/src/cli/grammar-data.ts` | Add the exact hook summary and argparse help, with a typed declaration map |
| `ts/src/cli/settings.ts` | Validate hook settings and translate `LodgeError` into `CliError` |
| `ts/src/cli/index.ts` | Export `hookContextFor`, read by `main.ts`, the repository helper, and context tests |
| `ts/src/main.ts` | Wire stdin, stdout, context, git resolution, and nullable working directory into the command's hook port |
| `ts/src/hook/post-tool-use.ts` | Resolve moved projects' lodge symlinks and remove the redundant end assertion and false comment |
| `ts/tests/hook/repository.ts` | Provide isolated real git repositories, staged initial folders, settings, and command execution without server requests |
| `ts/tests/hook/hand-edits.test.ts` | Carry every Python test and all three malformed settings cases, and add moved advice in checkout and branch modes |
| `ts/tests/hook/outside-repository.test.ts` | Carry every Python test, exercise actual outside-repository and malformed-settings payloads, and check optional port dispatch |
| `ts/tests/hook/entrypoint.test.ts` | Exercise the actual composition root through synchronous Bun subprocesses, including unavailable working directory |
| `ts/tests/cli/hook-context.test.ts` | Cover defaults, record folders, branch and moved contexts, strict bytes, malformed settings, and adapter failures |
| `ts/tests/cli/settings.test.ts` | Rename `hook_is_left_alone` to `hook_is_checked`, cover a float section, and repair the existing core fixture |
| `ts/tests/cli/grammar.test.ts` | Include hook in command and help cases, and pin permissive event parsing and exact help |
| `ts/tests/e2e/help-lists-every-command.test.ts` | Include hook in command listing and help cases |
| `ts/tests/hook/edges.test.ts` | Pin literal glob escaping, question marks excluding slashes, and absolute display outside the repository |
| `ts/tests/hook/moved-advice.test.ts` | Pin disregard of an unrelated data root and resolution of a lodge symlink |
| `ts/tests/parity.json` | Mark outside-repository tests ported and set the two changed reasons specified by Task 9 |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-9-report.md` | Record implementation, red evidence, commands, and deviations |

The helper's git repository sits inside its allocated temporary parent, so outside-repository probes still run git only in temporary folders.
No dependency was added or installed.
No historical brief, report, review, frozen document, Python file, or structure rule was edited.

## Test-first evidence

Each parametrised row below retains every listed case.
The initial carried hook suites failed to load with `SyntaxError: Export named 'hookContextFor' not found`, before the export or implementation existed.
The first focused run ended with `255 pass`, `12 fail`, and `2 errors`.
Context and parked regression tests were then added before implementing context or changing symlink resolution.
Mutations listed below were restored immediately after their checks.

| file:line | Test or cases | First failing output or mutation rejected |
| --- | --- | --- |
| `ts/tests/hook/hand-edits.test.ts:19` | `hook_names_the_write_path_after_a_hand_edit_of_a_record` | Missing `hookContextFor` export |
| `ts/tests/hook/hand-edits.test.ts:27` | `hook_finds_the_repository_of_the_edited_file_not_of_the_session` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:37` | `hook_finds_the_repository_for_a_file_that_does_not_exist_yet` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:44` | `hook_stays_silent_where_lodge_is_not_initialised` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:51` | `hook_stays_silent_for_a_file_that_is_not_lodges` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:55` | `hook_reads_the_frozen_globs_from_the_settings` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:63` | `hook_in_branch_mode_protects_frozen_files_only` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:73` | `unknown_hook_setting_is_one_sentence_for_commands_and_silent_for_the_hook`, unknown key, integer frozen, and integer hook | Missing export |
| `ts/tests/hook/hand-edits.test.ts:87` | `unknown_hook_key_is_named` | Missing export |
| `ts/tests/hook/hand-edits.test.ts:92` | `hook_gives_the_moved_advice_for_a_project_on_the_server`, default checkout and branch | Missing export |
| `ts/tests/hook/outside-repository.test.ts:9` | `hook_outside_repository_exit_0_silent` | Missing export |
| `ts/tests/hook/outside-repository.test.ts:19` | `hook_with_a_malformed_settings_file_stays_silent` | Missing export |
| `ts/tests/hook/outside-repository.test.ts:29` | `hook_with_an_unknown_event_stays_silent` | Missing export |
| `ts/tests/hook/outside-repository.test.ts:32` | `hook_without_a_port_stays_silent`, post-tool-use, whenever, and empty event | Missing export |
| `ts/tests/hook/outside-repository.test.ts:52` | `hook_dispatches_only_post_tool_use_before_settings_and_returns_the_port_code` | Replacing hook dispatch with `return 0` failed the expected return value of 7 |
| `ts/tests/cli/hook-context.test.ts:26` | `hook_context_defaults_and_edited_path` | Missing export |
| `ts/tests/cli/hook-context.test.ts:36` | `checkout_needs_both_record_folders`, decisions and spec | Missing export |
| `ts/tests/cli/hook-context.test.ts:41` | `branch_context_has_no_data_root_and_allows_other_sections` | Missing export |
| `ts/tests/cli/hook-context.test.ts:51` | `moved_context_needs_no_record_folders`, checkout and branch | Missing export |
| `ts/tests/cli/hook-context.test.ts:61` | `malformed_hook_context_is_null`, malformed TOML, invalid store table or mode, invalid server table or URL value, invalid hook table, key, or frozen value, and invalid UTF-8 | Missing export for initial cases; the three added float cases received a context instead of null before replacing nullish defaults with presence checks |
| `ts/tests/cli/hook-context.test.ts:81` | `context_silences_repository_folder_and_read_errors` | Missing export |
| `ts/tests/cli/settings.test.ts:140` | `hook_is_checked` | `Expected constructor: CliError`, `Received function did not throw` |
| `ts/tests/cli/settings.test.ts:144` | `hook_float_is_not_an_absent_table` | `Received function did not throw`, before the presence check |
| `ts/tests/cli/settings.test.ts:145` | `core_table_holds_length_and_import_only`, carried assertion with valid hook fixture | Returning an empty core table instead of the parsed table failed the retained assertion |
| `ts/tests/cli/grammar.test.ts:72` | `every_command_parses`, hook case | Expected hook command, received usage error |
| `ts/tests/cli/grammar.test.ts:75` | `help_lists_every_command` | `Expected: true`, `Received: false` |
| `ts/tests/cli/grammar.test.ts:84` | `every_command_has_help`, hook case | Expected code 0 and hook usage, received invalid choice |
| `ts/tests/cli/grammar.test.ts:137` | `hook_bypasses_other_parsing`, absent event, unknown option with extra argument, and version flag | Expected hook command, received usage error |
| `ts/tests/cli/grammar.test.ts:144` | `hook_help_and_summary_match_argparse` | Expected exact hook help, received invalid choice |
| `ts/tests/e2e/help-lists-every-command.test.ts:24` | `help_lists_every_command` | `Expected: true`, `Received: false` |
| `ts/tests/e2e/help-lists-every-command.test.ts:31` | `every_command_has_help`, hook case | `Expected: 0`, `Received: 2` |
| `ts/tests/hook/entrypoint.test.ts:6` | `main_wires_stdin_context_output_and_resolution`, unmoved and moved | Restoring the original main before running the new tests made both fail with exit code 2 |
| `ts/tests/hook/entrypoint.test.ts:34` | `main_keeps_the_hook_silent_when_the_process_folder_cannot_be_read` | `Expected: 0`, `Received: 1`, before guarding the command Io working directory |
| `ts/tests/hook/moved-advice.test.ts:60` | `moved_project_ignores_a_different_data_root`, M-2 | Using a non-null supplied data root for moved records failed with a null response |
| `ts/tests/hook/moved-advice.test.ts:67` | `moved_project_resolves_the_lodge_symlink`, M-3 | `expect(received).not.toBeNull()`, `Received: null` |
| `ts/tests/hook/edges.test.ts:46` | `glob_escape_set_and_question_mark_do_not_overreach`, M-4 | Individually removing dot, backslash, or pipe escaping, or allowing question marks across slashes, failed; the initial pipe probe passed, so its paths were strengthened and rerun to a failure before code changes |
| `ts/tests/hook/edges.test.ts:58` | `record_path_outside_the_repository_is_shown_absolute`, M-5 | Always showing a relative path failed the absolute-path assertion |

M-1 removes a redundant assertion without changing behaviour.
The existing trailing-newline test at `ts/tests/hook/edges.test.ts:6` remains green.
Slash escaping is behaviourally redundant in the `RegExp` constructor, so no mutation assertion claims otherwise.

## Commands and results

Repository inspection used `cat`, `sed`, `rg`, `git status --short`, `git branch --show-current`, and `git diff`.
Their final observations were the specified branch, a clean starting tree, the merged interfaces, and the changes listed above.
Temporary editing scripts and log files were kept outside the repository.

| Command or check | Last lines or result |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author`, `nothing`; no agent work waiting either |
| Coordinator question | Direct implementation approved; valid hook fixture approved; validate store table and mode, hook, and string server URL only |
| `cd ts && bun test tests/hook tests/cli tests/e2e/help-lists-every-command.test.ts`, first run | `255 pass`, `12 fail`, `2 errors`, `Ran 267 tests across 15 files` |
| `cd ts && bun test tests/cli/hook-context.test.ts tests/hook/edges.test.ts tests/hook/moved-advice.test.ts`, red run | `11 pass`, `2 fail`, `1 error`, `Ran 13 tests across 3 files` |
| Temporary mutation drivers | Six effective regression mutations exited 1; the first pipe probe exited 0, then the strengthened pipe probe exited 1; dispatch and core mutations each exited 1 |
| `cd ts && bun test tests/cli/hook-context.test.ts tests/cli/settings.test.ts`, float regression red run | `79 pass`, `4 fail`, `Ran 83 tests across 2 files` |
| Temporary main restoration and entrypoint test | Exit 1; both actual-main cases failed before restoring the implementation |
| `cd ts && bun test tests/hook/entrypoint.test.ts`, working-directory red run | `2 pass`, `1 fail`, `Ran 3 tests across 1 file` |
| Biome formatting on the explicit changed TypeScript and JSON paths | `Checked 19 files`, `Fixed 11 files`, informational suggestions only |
| `cd ts && bunx tsc --noEmit -p .`, first run | TS7053 for the inferred declaration map; fixed by declaring `Readonly<Record<string, Declaration>>` |
| `cd ts && bunx tsc --noEmit -p .`, final run | Exit 0, no output |
| Focused hook, CLI, and help reruns | Initially `307 pass`, then `314 pass`, then `315 pass`, always `0 fail` after each corresponding implementation |
| `cd ts && bun --bun run check` | `2109 pass`, `0 fail`, `7249 expect() calls`, `Ran 2109 tests across 189 files`; dependency and structure checks passed |
| `git diff --check` | Exit 0, no output |
| `sh scripts/check-ts.sh`, final verification | Exit 0; `2109 pass`, `0 fail`, `7249 expect() calls`, `Ran 2109 tests across 189 files`; Biome reported 43 informational suggestions, no warnings or errors |

Commit and push use the brief's explicit identity, paths, branch, and Codex trailer after the final gate succeeds.
The coordinator's whole Python gate and compiled-binary smoke test remain coordinator steps.

## Deviations and uncertainties

The coordinator approved direct implementation because the plan header's required subagent skill is unavailable.
The coordinator approved replacing the old core settings test's invalid hook fixture with `frozen=[]`, preserving its original assertion.
The coordinator confirmed that unrelated top-level settings are accepted by hook context, other legacy store keys and core settings are not validated there, and server URL validation there requires a string only.
This differs from Python's broader legacy settings validation and follows the Task 9 interface as ruled.
The brief supersedes the sandbox restrictions for committing and pushing, and supersedes the historical Claude trailer with Codex.
The command Io's working directory also uses the guarded reader, because guarding only the hook callback still threw before dispatch when `process.cwd()` failed.
Additional context, dispatch, entrypoint, and float regression tests protect those boundary behaviours.
A temporary mutation utility initially used Python `subprocess.run` to start its Bun driver, contrary to the spawning rule.
All repository subprocesses added by this task and subsequent temporary mutation drivers use `Bun.spawnSync`; no Python spawning code is included in the change.
An initial deleted-directory probe passed because Bun retained the working directory, so the final test injects a throwing `process.cwd()` and was observed failing before the fix.
The first pipe escape mutation survived its initial probe, which was corrected and observed failing.
No unresolved implementation question remains.
