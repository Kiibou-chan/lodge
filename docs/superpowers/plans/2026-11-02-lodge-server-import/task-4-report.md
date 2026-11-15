# Task 4 report

Implemented the hook advice and settings parser on `server-import-hook`.

## Changes by file

| File | Change |
|---|---|
| `ts/src/app/hook-settings.ts` | Validate the hook table and frozen globs, preserving all three Python error messages as `LodgeError`. |
| `ts/src/app/index.ts` | Export `parseHookSettings`. |
| `ts/src/hook/index.ts` | Expose `HookContext`, `Resolve`, `respond`, and `run`. |
| `ts/src/hook/post-tool-use.ts` | Carry payload handling, record and thread selection, frozen globs, context lookup, JSON output, and silent failures, and add moved-project selection. |
| `ts/src/hook/texts.ts` | Preserve the three original templates character for character and add the three exact moved-project templates. |
| `ts/package.json` | Add the `#hook` front door without adding dependencies. |
| `ts/tests/app/front-door.test.ts` | Permit the planned `parseHookSettings` export. |
| `ts/tests/parity.json` | Set the hook row's explanation to the Task 4 parity wording. |
| `ts/tests/hook/post-tool-use.test.ts` | Carry all 24 Python test names, all 11 malformed payload cases, all three invalid settings cases, and every original assertion. |
| `ts/tests/hook/moved-advice.test.ts` | Add the six planned moved-project tests, checking attachments in both store modes. |
| `ts/tests/hook/edges.test.ts` | Check literal glob escaping, Unicode characters, full matching, cross-folder double stars, output failure, and resolution failure. |
| `ts/tests/hook/support.ts` | Supply typed contexts, payloads, output assertions, a driver, reversal assertions, and a test-local resolver that handles missing suffixes and symbolic links. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-4-report.md` | Record implementation, red evidence, commands, and deviations. |

The readers of the new `#hook` exports are the hook tests and their support module.
The carried tests read `parseHookSettings` through `#app`, and `post-tool-use.ts` reads every template export.
`HookOutput` stays private.

## Test-first evidence

E1 is the first failing output for each test below: `error: Cannot find package '#hook'`.
The initial carried and moved suites failed at import before implementation: `0 pass`, `2 fail`, and `2 errors`.
After adding the edge tests, the second red run still preceded implementation: `0 pass`, `3 fail`, and `3 errors`.
The brief explicitly permits a missing module or export as failing evidence.
No mutation was needed because the hook and settings implementation did not exist.
The existing front-door tests retain their assertions, with only the planned allowed addition.

| Test added or carried | file:line | First failing output |
|---|---|---|
| `record_edit_gets_feedback` | `ts/tests/hook/post-tool-use.test.ts:17` | E1 |
| `relative_record_path_is_read_from_the_repository_root` | `ts/tests/hook/post-tool-use.test.ts:28` | E1 |
| `dotted_path_still_counts_as_a_record` | `ts/tests/hook/post-tool-use.test.ts:33` | E1 |
| `attachment_edit_gets_nothing` | `ts/tests/hook/post-tool-use.test.ts:36` | E1 |
| `frozen_edit_gets_feedback` | `ts/tests/hook/post-tool-use.test.ts:41` | E1 |
| `frozen_globs_do_not_overreach` | `ts/tests/hook/post-tool-use.test.ts:51` | E1 |
| `branch_mode_protects_only_frozen_files` | `ts/tests/hook/post-tool-use.test.ts:61` | E1 |
| `other_edit_gets_nothing` | `ts/tests/hook/post-tool-use.test.ts:64` | E1 |
| `symlinked_checkout_still_matches` | `ts/tests/hook/post-tool-use.test.ts:72` | E1 |
| `bad_payload_exit_0_silent` | `ts/tests/hook/post-tool-use.test.ts:91` | E1 |
| `unreadable_input_exit_0_silent` | `ts/tests/hook/post-tool-use.test.ts:94` | E1 |
| `context_failure_exit_0_silent` | `ts/tests/hook/post-tool-use.test.ts:111` | E1 |
| `run_writes_one_json_line_for_a_record_edit` | `ts/tests/hook/post-tool-use.test.ts:120` | E1 |
| `run_stays_silent_for_an_unwatched_file` | `ts/tests/hook/post-tool-use.test.ts:129` | E1 |
| `settings_default_to_no_frozen_files` | `ts/tests/hook/post-tool-use.test.ts:134` | E1 |
| `settings_read_the_frozen_globs` | `ts/tests/hook/post-tool-use.test.ts:137` | E1 |
| `bad_settings_are_one_sentence` | `ts/tests/hook/post-tool-use.test.ts:144` | E1 |
| `a_hook_section_that_is_not_a_table_is_an_error` | `ts/tests/hook/post-tool-use.test.ts:153` | E1 |
| `record_advice_reverses_the_edit_without_git` | `ts/tests/hook/post-tool-use.test.ts:157` | E1 |
| `frozen_advice_names_the_guide` | `ts/tests/hook/post-tool-use.test.ts:170` | E1 |
| `context_is_asked_about_the_edited_file` | `ts/tests/hook/post-tool-use.test.ts:175` | E1 |
| `relative_path_is_read_from_the_payload_working_folder` | `ts/tests/hook/post-tool-use.test.ts:188` | E1 |
| `relative_path_without_a_payload_folder_is_read_from_the_process_folder` | `ts/tests/hook/post-tool-use.test.ts:197` | E1 |
| `thread_file_edit_names_reply_and_close` | `ts/tests/hook/post-tool-use.test.ts:217` | E1 |
| `moved_record_edit_names_the_server` | `ts/tests/hook/moved-advice.test.ts:22` | E1 |
| `moved_thread_edit_names_reply_and_close` | `ts/tests/hook/moved-advice.test.ts:31` | E1 |
| `moved_frozen_edit_names_the_server` | `ts/tests/hook/moved-advice.test.ts:38` | E1 |
| `moved_project_protects_lodge_in_branch_mode` | `ts/tests/hook/moved-advice.test.ts:44` | E1 |
| `moved_attachment_edit_gets_nothing` | `ts/tests/hook/moved-advice.test.ts:47` | E1 |
| `moved_advice_reverses_the_edit_without_git` | `ts/tests/hook/moved-advice.test.ts:51` | E1 |
| `glob_literals_and_unicode_match_the_whole_path` | `ts/tests/hook/edges.test.ts:6` | E1 |
| `run_silences_output_and_resolution_failures` | `ts/tests/hook/edges.test.ts:17` | E1 |

The malformed payload and invalid settings rows retain every Python parametrised case.
The shared reversal assertion also requires the warning to exist before checking command positions.
The record command ordering assertion explicitly requires `lodge draft` to exist, preserving Python's raising `str.index` behaviour.

## Commands and outcomes

Inspection commands included `cat CLAUDE.md`, `sed` for the required plan sections, `rg` and `rg --files` for source and structure discovery, and `cat` for the Python hook, its tests, the front doors, configuration, and gate script.
These completed successfully and supplied the requirements and existing implementation boundaries.

| Command | Outcome or last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Both agent and author queues: `nothing`. |
| `git status --short --branch` | Started clean on `server-import-hook`. |
| `cd ts && bun test tests/hook` before implementation | `Ran 2 tests across 2 files.`, with `0 pass`, `2 fail`, and `2 errors`. |
| `cd ts && bun test tests/hook` after adding edge tests, before implementation | `Ran 3 tests across 3 files.`, with `0 pass`, `3 fail`, and `3 errors`. |
| `cd ts && bun test tests/hook` after implementation | `44 pass`, `0 fail`, and `212 expect() calls`. |
| `bunx biome check --write --error-on-warnings` on changed TypeScript and JSON files | Initial formatting fixed eight files; subsequent focused formatting completed with no fixes. |
| `cd ts && bunx tsc --noEmit -p .` | First run reported TS4111 on index-signature property access; corrected access, and the next run exited 0 with no output. |
| `cd ts && bunx depcruise src tests scripts --config .dependency-cruiser.cjs` | `no dependency violations found (337 modules, 1241 dependencies cruised)`. |
| `cd ts && bunx knip` | Exit 0, with no unused exports. |
| `cd ts && bun test` | `1928 pass`, `0 fail`, and `6695 expect() calls` across 175 files, including structure tests. |
| `wc -l` on the new hook modules and tests | Every file is below 300 lines. |
| `git diff --check` | Exit 0, with no output. |
| `sh scripts/check-ts.sh` as the final validation | Exit 0: `1928 pass`, `0 fail`, and `6698 expect() calls` across 175 files. |

Temporary Python scripts and shell heredocs created the new files and updated the planned existing files.
The final gate passed Biome with `--error-on-warnings`, TypeScript, dependency-cruiser, knip, and all Bun tests.
Biome reported 30 informational diagnostics, with no warnings or errors.
No dependency installation was needed.
No test spawned a process or used a real repository.

## Deviations and uncertainties

The plan header names an unavailable `superpowers:subagent-driven-development` skill.
The coordinator ruled: “Option A: implement Task 4 directly, test-first, no delegation.”
Implementation followed that ruling.
The brief supersedes the sandbox-only prohibition on committing and pushing, and supplies the Codex co-author trailer.
The whole Python gate and other coordinator steps remain with the coordinator.

Added `edges.test.ts` and `support.ts` to keep extra regression coverage and reusable test helpers separate from the carried tests.
The glob uses the required Unicode regular expression and anchored non-capturing group, with a final end-of-input assertion because JavaScript's `$` also accepts the position before a trailing newline, while Python's `fullmatch` does not.
The extra regression test covers this difference.
No other requirement deviations or unresolved uncertainties remain.
