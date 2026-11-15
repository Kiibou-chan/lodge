# Task 2 report

Implemented the fifteen-command grammar and its typed front door on `server-api-a`.
The TypeScript gate passes, including the existing tests and structure checks.

## Files changed

| File | Change |
|---|---|
| `ts/src/cli/args.ts` | Parse declared positionals and options, conversions, choices, repetition, abbreviations, equals syntax, the end-of-options marker, and usage errors. |
| `ts/src/cli/grammar.ts` | Define `Command` and `ThreadCommand`, produce typed commands, construct core filters, handle top-level exits, and enforce author-message rules. |
| `ts/src/cli/grammar-data.ts` | Hold the top-level help and combine the two declaration tables. |
| `ts/src/cli/grammar-records.ts` | Declare the ten record and utility commands with lodge 0.2's captured usage and help. |
| `ts/src/cli/grammar-threads.ts` | Declare the five thread commands with lodge 0.2's captured usage and help. |
| `ts/src/cli/index.ts` | Export `parse`, `Command`, `ThreadCommand`, and `Exit`. |
| `ts/package.json` | Add the `#cli` front door without changing dependencies. |
| `ts/tests/cli/args.test.ts` | Add the eight specified parser tests and four regression tests. |
| `ts/tests/cli/grammar.test.ts` | Add all specified grammar tests, with cases for every command and its help. |
| `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-2-report.md` | Record implementation, failing evidence, validation, and deviations. |

## Test-first evidence

The initial invocation was `cd ts && bun test tests/cli`, before adding the front door or implementation.
Both test files failed to load with `error: Cannot find package '#cli'`.
That missing-module failure is the first failure for every initial test and every expanded parameter case below.
The final focused run has 55 passing cases and 71 assertions.
No carried tests or parity rows change in this task.

| Test | file:line | First failing output |
|---|---|---|
| `options_before_between_and_after_positionals` | `ts/tests/cli/args.test.ts:4` | Cannot find package `#cli`. |
| `equals_form` | `ts/tests/cli/args.test.ts:16` | Cannot find package `#cli`. |
| `double_dash_ends_options` | `ts/tests/cli/args.test.ts:18` | Cannot find package `#cli`. |
| `unique_prefix_is_the_option` | `ts/tests/cli/args.test.ts:20` | Cannot find package `#cli`. |
| `ambiguous_prefix_is_an_error` | `ts/tests/cli/args.test.ts:22` | Cannot find package `#cli`. |
| `repeatable_option_collects` | `ts/tests/cli/args.test.ts:27` | Cannot find package `#cli`. |
| `missing_value_is_an_error` | `ts/tests/cli/args.test.ts:31` | Cannot find package `#cli`. |
| `extra_words_are_an_error` | `ts/tests/cli/args.test.ts:36` | Cannot find package `#cli`. |
| `every_command_parses`, all fifteen commands | `ts/tests/cli/grammar.test.ts:71` | Cannot find package `#cli`. |
| `help_lists_every_command` | `ts/tests/cli/grammar.test.ts:74` | Cannot find package `#cli`. |
| `every_command_has_help`, all fifteen commands | `ts/tests/cli/grammar.test.ts:83` | Cannot find package `#cli`. |
| `no_command_is_a_usage_error` | `ts/tests/cli/grammar.test.ts:89` | Cannot find package `#cli`. |
| `invalid_choice_is_argparse_s_line`, status and ID cases | `ts/tests/cli/grammar.test.ts:100` | Cannot find package `#cli`. |
| `missing_positional_is_argparse_s_line` | `ts/tests/cli/grammar.test.ts:103` | Cannot find package `#cli`. |
| `limit_must_be_a_positive_whole_number`, `0`, `-1`, `many`, and `٣` | `ts/tests/cli/grammar.test.ts:108` | Cannot find package `#cli`. |
| `author_message_needs_where_and_when` | `ts/tests/cli/grammar.test.ts:114` | Cannot find package `#cli`. |
| `where_with_an_agent_role` | `ts/tests/cli/grammar.test.ts:119` | Cannot find package `#cli`. |
| `version_prints_the_version_given` | `ts/tests/cli/grammar.test.ts:124` | Cannot find package `#cli`. |
| `draft_help_says_decisions_are_immutable` | `ts/tests/cli/grammar.test.ts:131` | Cannot find package `#cli`. |
| `unknown_top_level_option_is_not_discarded` | `ts/tests/cli/args.test.ts:44` | Expected exit 2 for `--unknown show d-aaaaaa`, received a `show` command. |
| `extra_arguments_keep_their_order` | `ts/tests/cli/args.test.ts:50` | Expected `unrecognized arguments: extra --unknown`, received `unrecognized arguments: --unknown extra`. |
| `help_flag_rejects_an_explicit_value` | `ts/tests/cli/args.test.ts:56` | Expected the ignored explicit argument error, received `the following arguments are required: ref`. |
| `double_dash_is_leftover_without_positionals` | `ts/tests/cli/args.test.ts:63` | Expected `unrecognized arguments: -- -x`, received `unrecognized arguments: -x`. |

The draft-help assertion initially looked for an uninterrupted phrase, but lodge 0.2 wraps between `a` and `decision`.
It now allows whitespace between those words, preserving the exact captured help.
The three first regression tests were run together before their fixes and produced 8 passes and 3 failures.
The end-of-options regression was run before its fix and produced 11 passes and 1 failure.

## Commands and outcomes

Read-only inspection used `cat`, `sed`, `rg`, `wc -l`, `nl -ba`, `git status --short`, `git diff --stat`, and `git branch --show-current`.
The branch check returned `server-api-a`.
The initial working tree was clean.
No test opened a socket or accessed the network.

| Command or check | Last lines or outcome |
|---|---|
| `uv run --frozen --quiet lodge waiting` | `waiting for the author`, then `nothing`; neither an agent nor the author had waiting items. |
| Initial `cd ts && bun test tests/cli` | `0 pass`, `2 fail`, `2 errors`, missing `#cli`. |
| First implementation's focused tests | `50 pass`, `1 fail`; draft-help assertion crossed an argparse line break. |
| `COLUMNS=80 uv run --frozen --quiet lodge draft -h` | Confirmed the wrapped immutable-decision sentence and the help section ending `show this help message and exit`. |
| `cd ts && bunx biome check --write --error-on-warnings src/cli tests/cli package.json` | Formatted the new files; later focused formatting ended `Checked 8 files`, with no warnings. |
| `cd ts && bunx tsc --noEmit -p .` | Initially reported un-narrowed parser-result access; after adding a discriminated result, exited 0 with no output. |
| Initial `sh scripts/check-ts.sh` | Knip reported unused `TOP_USAGE`; removed its unnecessary export. |
| Python reference capture using `_parser()` under `COLUMNS=80` | `122 reference exits`. |
| Bun comparison of those exits with `parse` | Initially six end-of-options differences for commands without positionals; after the regression fix, `differences: 0`. |
| Final `cd ts && bun test tests/cli` | `55 pass`, `0 fail`, `71 expect() calls`, across two files. |
| Final `sh scripts/check-ts.sh` | `1357 pass`, `2 todo`, `0 fail`, `3454 expect() calls`, across 110 files; exit 0. |

The reference comparison covered every command's complete help, missing arguments, unknown options, invalid choices, converters, and author-message errors.
Its temporary data stayed outside the repository.
All fifteen command help bodies match lodge 0.2 byte for byte at `COLUMNS=80`.
Top-level help intentionally omits `view` and `hook`, as required by this plan.

## Deviations and uncertainties

The declaration and help data are split into three additional modules to keep every source module below 300 lines.
`grammar-records.ts` holds 236 lines, `grammar-threads.ts` holds 192 lines, and `grammar-data.ts` combines them without a cycle.
Static usage and help strings were captured from the existing Python parser, with `view` and `hook` removed, to preserve argparse's wrapping without implementing a second help formatter.
There is no Python dependency at runtime.
Four additional regression tests cover differences found during implementation and comparison.
The required ASCII-only `--limit` conversion rejects other Unicode decimal digits that Python accepts.
The parser accepts options between file positionals as the task requires, including continuing a multi-file list after an option.
The plan header names a superpowers workflow that is not in the available skills catalogue; implementation followed the brief's test-first steps directly.
No package, import edge, structure rule, historical document, or coordinator-only check was changed.
No unresolved implementation uncertainty remains within Task 2's scope.
