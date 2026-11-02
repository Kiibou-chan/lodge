# Task 8b report

Implemented the Python change checks and exported `checkChange` through `#core`.
No commit or push was made, no package was installed, and no reviewer file was edited.

## Changes per file

- `ts/src/core/check-entries.ts`: ports check 4, including structural entry equality, link-only edits, create misuse, import exemptions, and configured import sources.
- `ts/src/core/check-immutable.ts`: ports decision field immutability and thread append and closing rules, preserving Python field order and snake_case message names.
- `ts/src/core/check-change.ts`: combines state problems, published notes, missing records, date checks against published and optional current decisions, imports over live entries, checks 4 and 5, links to replaced or retired records, and area notes.
- `ts/src/core/index.ts`: exports `checkChange`.
- `ts/tests/core/checks.ts`: adds `check` and `verdict`, using the existing synthetic settings and time.
- `ts/tests/core/check-change.test.ts`: ports all change tests, with every assertion and date case.
- `ts/tests/core/check-current.test.ts`: ports all optional-current tests.
- `ts/tests/core/check-retired.test.ts`: ports both retirement replacement tests.
- `ts/tests/core/check-immutable.test.ts`: carries all immutable and replaced-record tests, with all fourteen header edits, four reasoning pairs, and both link verbs.
- `ts/tests/parity.json`: marks `checks.py` and the four test files as `ported`.
- `ts/knip.json`: removes `src/core/check-state.ts` from entry exemptions and retains `tests/core/checks.ts` for Task 8c.
- This report records the implementation and validation.

No source or test module required splitting, and every file remains below 300 lines.
The implementation uses structural equality for dataclasses and arrays, code-point ordering for strings, and integer stamp comparisons for dates.
None of the three Python modules uses `!r`, so these ports need no `pyRepr` call.

## Test-first evidence

All four test files and both new test helpers were written before the implementation or front-door export.
The initial mechanical translation exposed a reserved identifier and an unsupported assertion translation, which were corrected before the definitive red run.
`cd ts && bun test tests/core` then reported the following for each of the four files:

```text
SyntaxError: Export named 'checkChange' not found in module '…/ts/src/core/index.ts'.
373 pass
4 todo
5 fail
5 errors
1190 expect() calls
Ran 382 tests across 30 files.
```

The fifth module error came from an existing test file importing `checks.ts`, whose new helper imports `checkChange`.
The same missing-export failure is the first valid pre-implementation failure for every test listed below, including every parameter case.
The immutable tests exercise this task's new implementation, so no mutation of an earlier task's code was needed.
No assertion was weakened.
The missing-record path assertion uses optional indexing because TypeScript checks array bounds, alongside the original exact problem-array assertion.

### `check-change.test.ts`

- `clean_change_passes`.
- `nothing_changed_is_clean`.
- `published_problem_is_note_not_failure`.
- `new_state_problem_fails`.
- `check_2_published_record_missing_from_after`.
- `check_1_new_decision_dated_no_later_than_its_target`: ['replaces', 'narrows', 'confirms'].
- `check_1_dates_compare_as_instants`.
- `check_1_new_decision_sharing_an_entry_with_a_later_one`.
- `check_1_imported_decision_is_exempt_from_the_date_rule`.
- `check_1_published_decisions_are_not_dated_again`.
- `check_1_import_changes_entry_changed_live`.
- `check_1_import_changes_entry_only_imports_changed`.
- `area_title_change_is_note`.
- `area_intro_change_is_note`.
- `area_order_change_is_note`.
- `check_1_new_decision_dated_after_the_time_of_the_change`.
- `check_1_a_decision_dated_exactly_now_passes`.
- `published_future_dated_decision_is_not_dated_again`.
- `area_added_and_removed_are_notes`.
- `area_rank_change_is_note`.

### `check-current.test.ts`

- `new_decision_must_be_after_an_unpublished_one_it_shares_an_entry_with`.
- `new_decision_after_an_unpublished_one_passes`.
- `without_the_current_state_only_published_decisions_count`.
- `an_unpublished_decision_is_not_held_to_a_newer_one`.

### `check-retired.test.ts`

- `check_6_replacing_the_retirement_lets_the_decision_edit_the_entry_again`.
- `check_6_a_later_decision_may_edit_an_entry_whose_retirement_was_replaced`.

### `check-immutable.test.ts`

- `check_5_header_key_of_a_published_decision_changed`: title, scope, decided_by, date, code, changes, replaces, narrows, confirms, work_item, quote, numbers, attachments, imported_from.
- `check_5_statement_changed`.
- `author_reasoning_edit_fails`.
- `check_5_agent_reasoning_changed_in_any_way_fails`: [('Two words', 'Now three words'), ('Now three words', 'Two words'), ('one two three four five six', 'six five four three two one'), ('Two\nwords', 'Two   words')].
- `check_5_agent_reasoning_unchanged_passes`.
- `check_5_author_reasoning_reflowed_fails`.
- `check_5_new_decisions_are_not_compared`.
- `check_6_new_decision_links_to_a_replaced_decision`: ['narrows', 'confirms'].
- `replacing_a_decision_passes_check_6`.
- `check_6_new_decision_changes_a_retired_entry`.
- `check_6_retiring_a_retired_entry_passes`.
- `check_6_older_records_keep_their_links`.

## Commands and outcomes

Read-only inspection used `cat`, `rg`, `git status --short`, `git diff`, `nl`, and `wc` on the brief, `CLAUDE.md`, the named Python modules and tests, and the TypeScript dependencies and configuration.
No other part of the implementation plan was opened.
The environment skill was read, but its `environment_status` tool is unavailable in this session.
No network operation was attempted.

- `uv run --frozen --quiet lodge waiting`: exit 0, ending `waiting for the author` and `nothing`, with nothing waiting for an agent either.
- `python /tmp/port8b.py`: temporary test translation helper, corrected after its first unsupported AST assertion; final run exited 0 with no output.
- `cd ts && bunx --no-install biome check --write --unsafe` with only the task's test and source paths: removed unused generated imports and formatted the files, ending `Checked 10 files in 14ms. Fixed 3 files.` on the implementation pass.
- `cd ts && bun test tests/core` before implementation: the missing-export failure above.
- `cd ts && bun test tests/core` after implementation: initially `468 pass`, `4 todo`, and `3 fail` because three header test expectations incorrectly used camelCase names; corrected the cases and expected messages to Python's snake_case names.
- `cd ts && bunx --no-install tsc --noEmit -p .`: initially rejected unchecked array indexing and its possibly missing expected path; optional indexing preserves the path equality assertion and resolves the typing.
- `cd ts && bun test tests/core` after the message corrections: `471 pass`, `4 todo`, `0 fail`, `1318 expect() calls`, and `Ran 475 tests across 30 files.`
- `sh scripts/check-ts.sh`: first failed only on formatting the shortened knip entry array, ending `error: script "check" exited with code 1`.
- `cd ts && bunx --no-install biome format --write knip.json`: exit 0, ending `Formatted 1 file in 935µs. Fixed 1 file.`
- `sh scripts/check-ts.sh` before the parity flip: exit 0, `648 pass`, `4 todo`, `0 fail`, `1796 expect() calls`, and `Ran 652 tests across 37 files.`
- `sh scripts/check-ts.sh` after the parity flip and report: exit 0, ending `648 pass`, `4 todo`, `0 fail`, `1806 expect() calls`, and `Ran 652 tests across 37 files.`
The parity flip accounts for the additional assertions.

The gate includes Biome with warnings treated as errors, TypeScript, dependency-cruiser, knip, and all Bun tests.
Knip reports no unused export and retains its two existing configuration hints for unmatched scripts globs.

## TypeScript differences and concerns

No carried test cannot hold in TypeScript.
`NOW` is a stamp instead of a Python datetime, as required, and tuple assertions compare arrays structurally.
All parameter values and Python test names are retained.
There are no unresolved task concerns.
The four existing TODOs belong to work outside this task.
The coordinator still owns the full Python and TypeScript gate outside the sandbox, staging, committing, and pushing.
