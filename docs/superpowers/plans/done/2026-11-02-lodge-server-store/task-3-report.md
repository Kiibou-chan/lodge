# Task 3 report

Implemented Task 3 on branch `server-store-a`.
The task-specific instruction granting commit and push access takes precedence over the repeated sandbox-only builder constraint.
The coordinator's whole-project gate, merge, and ledger update remain the coordinator's work.

## Files

| File | Change |
|---|---|
| `ts/src/app/state.ts` | One asynchronous store reading, derived state, checks against published state, reference resolution, and unreadable-file diagnostics. |
| `ts/src/app/writes.ts` | Draft parsing, bounded ID draws, clock waits, application, feedback, attachment validation, change checks, publication, and retries. |
| `ts/src/app/lodge.ts` | Constructor wiring and asynchronous `mint` and `add` delegation. |
| `ts/src/app/index.ts` | Export `Lodge`. |
| `ts/tests/app/support.ts` | Synthetic storage project, constants, and wiring typed against `Store`. |
| `ts/tests/app/writes.test.ts` | Thirteen required write and mint tests. |
| `ts/tests/app/writes-attach.test.ts` | All six Python attachment test titles, including all six filename cases. |
| `ts/src/app/errors.ts` | Error options and preservation of the settings error as cause, addressing P3. |
| `ts/tests/app/errors.test.ts` | Full settings error message and cause assertions, addressing P2 and P3. |
| `ts/tests/app/ports.test.ts` | Assert explicitly supplied defaulted fields survive all six builders, addressing P1. |
| `ts/src/app/ports.ts` | Carry method contracts for the store, sleep, and entropy, addressing P6. |
| `ts/src/app/time.ts` | Share one two-digit padding helper, addressing P5. |
| `ts/tests/app/fakes.ts` | Use core's attachment directory, document interleaving controls, and name the ID constructor parameter `first`, addressing P4, P6, and P7. |
| `ts/knip.json` | Add the three future-reader entries and remove the now-consumed fakes entry. |
| `ts/tests/parity.json` | Mark conftest, support, and attachment tests ported by Task 3. |
| This report | Evidence and scope. |

The partially carried `test_writes.py` row stays planned for Task 4 to complete and flip, as the brief requires.
Earlier briefs, reports, and reviews were not edited.
P7's correction to Task 2's report is recorded here instead: Task 2 checked six default builders, not seven.

## Test-first evidence

The first application test run after writing support and both new test files, before implementation, ended with:
`SyntaxError: Export named 'Lodge' not found in module`, `9 pass`, `2 fail`, `2 errors`.
Both new files failed at module loading.
The brief explicitly accepts a missing module or export as red.

| Test title | First failure |
|---|---|
| `add_new_decision_entry_area` | Missing Lodge export. |
| `add_fills_id_and_date_from_ports` | Missing Lodge export. |
| `add_date_and_check_time_from_one_reading` | Missing Lodge export. |
| `add_failing_check_publishes_nothing` | Missing Lodge export. |
| `add_returns_feedback_and_notes` | Missing Lodge export. |
| `add_refuses_unreadable_or_unusable_drafts` | Missing Lodge export. |
| `add_imports_only_when_asked` | Missing Lodge export. |
| `dry_run_publishes_nothing` | Missing Lodge export. |
| `dry_run_reports_feedback_and_check` | Missing Lodge export. |
| `mint_skips_taken` | Missing Lodge export. |
| `mint_gives_up_after_ten_draws` | Missing Lodge export. |
| `add_area_sharing_a_rank_gives_feedback` | Missing Lodge export. |
| `rest_on_entry_retired_in_the_same_add_is_refused` | Missing Lodge export. |
| `attachment_is_written_beside_the_new_decision` | Missing Lodge export. |
| `dry_run_writes_no_attachment` | Missing Lodge export. |
| `attachment_needs_exactly_one_new_decision` | Missing Lodge export. |
| `decision_must_list_exactly_the_attached_names` | Missing Lodge export. |
| `attachment_names_are_plain_file_names` | Missing Lodge export, for all six cases. |
| `two_attachments_with_one_name_are_refused` | Missing Lodge export. |
| `explicit_defaulted_fields_survive` | Mutation moved defaults after the value spread in all six existing builders: 5 pass, 1 fail, at the explicit detail assertion. |
| `settings_error_preserves_the_full_message_and_cause` | Message mutation dropped the parser's reason: 5 pass, 1 fail, at full message equality. |
| Same settings test, cause assertion | Mutation removed the cause option: 5 pass, 1 fail, at SettingsError instance assertion. |

All mutations were reverted immediately after their failing runs.
The cause implementation was initially changed while porting reference error chaining, before adding its test.
Its targeted mutation subsequently demonstrated the required failure, rather than claiming an initial red implementation run.

No Python test in this task cannot hold in TypeScript.
As explicitly required, the Python 999999-microsecond test uses START plus 999 milliseconds and checks the identical second-resolution date.

## Commands and results

Read-only inspection used `cat`, `rg`, `git status --short`, `git diff`, `git branch --show-current`, and `wc -l`.
Read CLAUDE.md, Task 2's review, the Python implementations, tests, ports, and TypeScript helpers.
`uv run --frozen --quiet lodge waiting` ended with `waiting for the author / nothing`; nothing awaited an agent either.

| Command | Result or last lines |
|---|---|
| `cd ts && bun test tests/app`, before implementation | 9 pass, 2 fail, 2 errors; missing Lodge export. |
| Same command, after implementation | 33 pass, 0 fail, 96 expect calls. |
| `python3 /tmp/task3-mutations.py` | Each of defaults, message, and cause returned 1; each run had 5 pass and 1 fail. |
| `cd ts && bunx biome check --write src/app tests/app` | Formatted files; reported non-null assertions and an unused import, subsequently corrected. |
| `sh scripts/check-ts.sh`, first run | Exit 1: formatting and warnings. |
| `cd ts && bunx biome check --write src/app tests/app knip.json` | Formatting corrected. |
| `sh scripts/check-ts.sh`, second run | Exit 2: areaFeedback needed an array rather than an iterator; the error assertion needed narrowing. |
| `sh scripts/check-ts.sh`, third run | Exit 0: 967 pass, 0 fail, 2399 expect calls. |
| `cd ts && bunx biome check --write tests/app/support.ts tests/parity.json` | Formatting complete. |
| `cd ts && bunx biome check --write src/app/state.ts src/app/writes.ts tests/app/fakes.ts` | Formatting complete. |
| Final `sh scripts/check-ts.sh` | Exit 0: 967 pass, 0 fail, 2405 expect calls, across 68 files; dependency checks clean. |

The final gate covers Biome with warnings as errors, TypeScript, dependency-cruiser, knip, structure checks, and every Bun test.
No dependency was added or installed.
No Python source, Python test, dependency lock, real repository fixture, or network test was changed.
All new modules and test files remain below 300 lines.

## Concerns

The brief contains conflicting generic and task-specific git instructions.
I followed its explicit task-specific commit and push instruction and Codex trailer, matching Task 2's review observation.
The coordinator's whole-project check is intentionally not run here.
The pre-existing untracked task execution log is excluded from the commit.
