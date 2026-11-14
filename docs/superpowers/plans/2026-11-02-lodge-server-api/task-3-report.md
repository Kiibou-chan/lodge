# Task 3 report

Implemented the command’s settings and file readers.

## Files changed

| File | Change |
|---|---|
| `ts/src/cli/errors.ts` | Added `CliError` with exit codes 1 and 2, defaulting to 2. |
| `ts/src/cli/files.ts` | Added strict UTF-8 reads preserving the byte order mark, exact reads, draft newline translation, and readable file errors. |
| `ts/src/cli/settings.ts` | Added repository discovery, TOML conversion and validation, server validation, core settings, the missing-server refusal, and environment token lookup. |
| `ts/src/cli/index.ts` | Exported every interface specified by Task 3 through the front door. |
| `ts/package.json` | Added the `#cli` import alias because lane A is not present. |
| `ts/knip.json` | Removed `smol-toml` from ignored dependencies. |
| `ts/tests/cli/settings.test.ts` | Added settings and repository tests, including normalisation and one-line error cases. |
| `ts/tests/cli/files.test.ts` | Added file-reading tests and explicit exit-code coverage. |
| `docs/superpowers/plans/2026-11-02-lodge-server-api/task-3-report.md` | Added this report. |

## Test-first evidence

All original tests were written before the implementation.
The first `bun test tests/cli` run reported `0 pass`, `2 fail`, and `2 errors`, with `Cannot find package '#cli'` in each file.
Every case in the rows marked A was present in that run, which failed at module import before running the assertions.
The additional tests marked B were written after the first green gate and failed against the initial implementation before their fixes.
No carried Python tests or parity rows belong to this task.

| Test, including all parameter cases | file:line | First failure |
|---|---|---|
| `root_is_the_nearest_folder_with_git %s` | `ts/tests/cli/settings.test.ts:27` | A: `Cannot find package '#cli'`. |
| `outside_a_repository_is_one_sentence` | `ts/tests/cli/settings.test.ts:38` | A: `Cannot find package '#cli'`. |
| `no_settings_file_has_no_server` | `ts/tests/cli/settings.test.ts:42` | A: `Cannot find package '#cli'`. |
| `whole_number_float_is_refused %s` | `ts/tests/cli/settings.test.ts:50` | A: `Cannot find package '#cli'`. |
| `integer_forms_are_read %s` | `ts/tests/cli/settings.test.ts:59` | A: `Cannot find package '#cli'`. |
| `inf_and_a_date_are_refused %s` | `ts/tests/cli/settings.test.ts:62` | A: `Cannot find package '#cli'`. |
| `float_in_sources_is_refused` | `ts/tests/cli/settings.test.ts:65` | A: `Cannot find package '#cli'`. |
| `unclosed_table_header_is_one_sentence` | `ts/tests/cli/settings.test.ts:67` | A: `Cannot find package '#cli'`. |
| `store_is_an_unknown_section` | `ts/tests/cli/settings.test.ts:76` | A: `Cannot find package '#cli'`. |
| `first_unknown_name_in_file_order_is_named %s` | `ts/tests/cli/settings.test.ts:81` | A: `Cannot find package '#cli'`. |
| `server_is_read` | `ts/tests/cli/settings.test.ts:82` | A: `Cannot find package '#cli'`. |
| `server_is_needed` | `ts/tests/cli/settings.test.ts:86` | A: `Cannot find package '#cli'`. |
| `server_url_must_be_https_or_this_machine refused %s` | `ts/tests/cli/settings.test.ts:110` | A: `Cannot find package '#cli'`. |
| `server_url_must_be_https_or_this_machine accepted %s` | `ts/tests/cli/settings.test.ts:121` | A: `Cannot find package '#cli'`. |
| `server_project_is_a_name %s` | `ts/tests/cli/settings.test.ts:125` | A: `Cannot find package '#cli'`. |
| `server_needs_url_and_project %s` | `ts/tests/cli/settings.test.ts:133` | A: `Cannot find package '#cli'`. |
| `server_table_and_keys_are_checked` | `ts/tests/cli/settings.test.ts:136` | A: `Cannot find package '#cli'`. |
| `hook_is_left_alone` | `ts/tests/cli/settings.test.ts:140` | A: `Cannot find package '#cli'`. |
| `core_table_holds_length_and_import_only` | `ts/tests/cli/settings.test.ts:143` | A: `Cannot find package '#cli'`. |
| `token_comes_from_the_environment` | `ts/tests/cli/settings.test.ts:148` | A: `Cannot find package '#cli'`. |
| `settings_not_utf8_is_one_sentence` | `ts/tests/cli/settings.test.ts:153` | A: `Cannot find package '#cli'`. |
| `server_url_rejects_normalised_disallowed_parts %s` | `ts/tests/cli/settings.test.ts:165` | B: all six cases were accepted rather than throwing. |
| `unreadable_settings_is_one_sentence` | `ts/tests/cli/settings.test.ts:171` | B: received `Illegal operation on a directory` instead of `Is a directory`. |
| `unknown_names_remain_one_sentence` | `ts/tests/cli/settings.test.ts:176` | B: received an unknown-key message with a literal newline. |
| `draft_line_ends_are_translated` | `ts/tests/cli/files.test.ts:18` | A: `Cannot find package '#cli'`. |
| `draft_keeps_a_byte_order_mark` | `ts/tests/cli/files.test.ts:20` | A: `Cannot find package '#cli'`. |
| `exact_text_keeps_its_line_ends` | `ts/tests/cli/files.test.ts:22` | A: `Cannot find package '#cli'`. |
| `not_utf8_is_one_sentence` | `ts/tests/cli/files.test.ts:24` | A: `Cannot find package '#cli'`. |
| `missing_file_is_one_sentence` | `ts/tests/cli/files.test.ts:32` | A: `Cannot find package '#cli'`. |
| `cli_error_can_exit_one` | `ts/tests/cli/files.test.ts:37` | A: `Cannot find package '#cli'`. |

The first implementation run additionally failed `missing_file_is_one_sentence` because Bun supplied lower-case `no such file or directory`.
The corrected implementation passes all 66 task cases with 116 assertions.

## Commands and results

| Command | Result or last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `cat`, `sed`, `rg`, and `wc` inspections | Read the brief, repository instructions, plan requirements, core settings, structure rules, package configuration, and final sources. |
| `cd ts && bun test tests/cli`, before implementation | `0 pass`, `2 fail`, `2 errors`; missing `#cli`. |
| `cd ts && bun test tests/cli`, initial implementation | `57 pass`, `1 fail`; missing-file error capitalisation. |
| `cd ts && bunx --no-install biome check --write src/cli tests/cli package.json knip.json` | Formatting applied; two informational literal-key suggestions remain because TypeScript requires bracket access to index signatures. |
| `cd ts && bun test tests/cli`, after the first correction | `58 pass`, `0 fail`, `101 expect() calls`. |
| `sh scripts/check-ts.sh`, first gate | `1360 pass`, `2 todo`, `0 fail`; 3484 assertions, no dependency violations. |
| `cd ts && bun test tests/cli`, added edge cases | `58 pass`, `8 fail`; six URL cases, directory reading, and a multiline key. |
| `cd ts && bun -e`, system-error API probe | Bun does not export `getSystemErrorMap` from `node:util`. |
| Python `os.strerror` comparison | `No such file or directory`, `Permission denied`, and `Is a directory`. |
| `cd ts && bunx --no-install biome check --write src/cli tests/cli` | Formatted the additions. |
| `cd ts && bun test tests/cli`, final targeted run | `66 pass`, `0 fail`, `116 expect() calls`. |
| `sh scripts/check-ts.sh`, final gate | `1368 pass`, `2 todo`, `0 fail`; 3499 assertions, no dependency violations. |

## Deviations and concerns

The task brief overrides the sandbox and coordinator-only commit instructions, so this task commits and pushes `server-api-b` with the requested Codex trailer.
The Python coordinator gate and socket checks are outside this task and were not run.
Added edge-case tests to enforce the existing URL and one-line error requirements.
Bun normalises dot paths, short IPv4 addresses, empty credentials, and missing URL slashes, so validation checks the original URL as well as the parsed one.
File errors use Python-compatible descriptions for ENOENT, EISDIR, EACCES, and EPERM, since Bun’s descriptions differ in capitalisation and directory wording.
Other error codes retain Bun’s description with initial capitalisation and without the operation or path suffix; exact wording for unusual system errors remains uncertain.
Permission denial is not tested with file modes because the execution account can bypass them; directory and missing-file errors are tested without privileged assumptions.
Two existing todos remain in the suite.
No dependencies were added, no sockets were opened, and no historical documents were edited.
