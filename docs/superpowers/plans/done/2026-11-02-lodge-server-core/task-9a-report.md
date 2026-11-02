# Task 9a report

Implemented the levels API and all view tests in the brief.
The final TypeScript gate passes.
No commit, staging, push, package installation, or network access was performed.

## Changes per file

- `ts/src/core/views.ts`: ported `views.py`, including readonly `Level1` and `Level3`, path-to-failure mapping, unrecorded problems, all three levels, ordered flags, provenance, headers, and exact text formatting.
  Changes are deduplicated by entry and action, matching Python value equality.
  Dependency freshness compares instants alone, so an ID tie-break cannot create a same-second warning.
- `ts/src/core/index.ts`: exported the eleven interfaces and functions named by the brief.
- `ts/tests/core/views.test.ts`: carried all sixteen Python view tests with their original names and assertions.
- `ts/tests/core/views-links.test.ts`: carried all seven dependency-link view tests.
- `ts/tests/core/views-trust.test.ts`: carried all seven trust view tests.
- `ts/tests/core/snapshot.test.ts`: replaced the duplicate-ID todo with its full test.
- `ts/tests/core/doubts.test.ts`: replaced the confirmation and flag-order todos with their full tests.
- `ts/tests/core/check-threads.test.ts`: created the view-specific thread-problem visibility test, with both Python parameter cases.
- `ts/tests/parity.json`: marked the three view files, snapshot, and doubts as `ported`.
  The thread-check row remains `planned` for the missing Task 8c tests described below.
- This report records implementation, validation, and the integration concern.

No source or test file needed splitting; `views.ts` has 216 lines and the largest new test file has 289 lines.
No knip entry exemption was needed because the public API is exported through the front door.

## Test-first evidence

All tests below were written before `views.ts` or its front-door exports existed.
The initial run caught a reserved-word transcription error in the main view suite; that syntax error was corrected before the recorded missing-export run and before implementation.
The second `cd ts && bun test tests/core` run failed at module loading, which the brief explicitly accepts as test-first evidence.
Its last lines were:

```text
402 pass
1 todo
6 fail
6 errors
1208 expect() calls
Ran 409 tests across 30 files.
```

Each group below shares its stated first failing output.
The tests could not load their required new views exports; no mutation of earlier-task code was needed for these new consumers.
Existing tests outside the explicitly authorised todos were preserved.

### `views.test.ts`

First failure: `SyntaxError: Export named 'level2' not found in module ts/src/core/index.ts`.

- `level1_status_who_flags`.
- `author_decision_behind_an_agent_entry_edit_awaits_the_author`.
- `agent_decision_behind_an_agent_entry_edit_is_not_flagged`.
- `narrowed_decision_flagged_at_level1`.
- `replaced_decision_names_successor_at_level1`.
- `entry_level1_takes_who_from_latest_decision`.
- `unquoted_import_flags`.
- `awaiting_flag_on_touched_entry`.
- `failing_ids_maps_paths`.
- `unrecorded_problem_for_unparsable_file`.
- `level2_of_entry`.
- `level2_views_of_entry_are_level1_views_newest_first`.
- `level3_reverse_links_with_status`.
- `level3_unknown_target_and_provenance`.
- `format_level1_exact_text`.
- `format_level3_exact_text`.

### `views-links.test.ts`

First failure: `SyntaxError: Export named 'level3' not found in module ts/src/core/index.ts`.

- `rests_on_retired_mark`.
- `rests_on_changed_since_mark`.
- `same_second_change_does_not_mark_changed_since`.
- `edit_with_unchanged_text_clears_changed_since`.
- `link_after_the_change_keeps_changed_since`.
- `entry_level1_keeps_the_author_after_a_link`.
- `level3_lists_rests_on_supports_and_linked_by`.

### `views-trust.test.ts`

First failure: `SyntaxError: Export named 'level2' not found in module ts/src/core/index.ts`.

- `level1_quote_on_decision_and_entry_when_author`.
- `level2_heads_and_entry_name_a_failing_decision`.
- `entry_whose_decision_is_replaced_or_narrowed`.
- `flag_order_in_full`.
- `entry_without_decision_says_so`.
- `level3_changes_carry_the_action`.
- `retired_by_names_a_standing_retirement`.

### Completed deferred tests

- `snapshot.test.ts`: `duplicate_id_marks_kept_record_failing`.
  First failure: `SyntaxError: Export named 'level1' not found in module ts/src/core/index.ts`.
  Asserts the kept ID fails, the dropped path remains unrecorded, and level 1 carries the warning.
- `doubts.test.ts`: `confirmed_decision_shows_confirmation_and_keeps_decided_by` and `flag_order`.
  Both first failed with the same missing `level1` export.
  The tests preserve the Python confirmation, attribution, and complete ordered flag assertions.
- `check-threads.test.ts`: `thread_problems_are_visible_in_reads %p`, with `false` and `true`.
  First failure: `SyntaxError: Export named 'unrecordedProblems' not found in module ts/src/core/index.ts`.
  Asserts a nonempty problem list and exact equality with all unrecorded problems.

## Commands and outcomes

Read-only inspection used `cat`, `rg`, `wc -l`, `git status --short`, and `git diff` to inspect the brief, repository instructions, Python source and tests, existing TypeScript interfaces and tests, line counts, and scoped changes.
Temporary transcription and editing scripts ran with `python` and produced no output on success.
No temporary scripts or logs were added to the repository.

| Command | Result and last output |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | Exit 0; `waiting for the author` followed by `nothing`; nothing waited for an agent either. |
| `cd ts && bun test tests/core` before implementation | Failed, with six missing-export module errors; `Ran 409 tests across 30 files.` |
| `cd ts && bun test tests/core` after implementation | Exit 0; `449 pass`, `1 todo`, `0 fail`, `1316 expect() calls`; `Ran 450 tests across 30 files.` |
| `cd ts && bunx --no-install biome check --write` on changed files | Formatted files and reported unused imports and a template suggestion, all subsequently fixed. |
| `cd ts && bunx --no-install tsc --noEmit -p .` | First failed on unused imports, an optional path explicitly set to undefined, and an unchecked first line; corrected all three; subsequent run exited 0 without output. |
| `cd ts && bunx --no-install biome check --write --unsafe` on three changed files | Applied import removal and the template rewrite; `Checked 3 files in 17ms. Fixed 3 files.` |
| `sh scripts/check-ts.sh` before parity changes | Exit 0; `626 pass`, `1 todo`, `0 fail`, `1794 expect() calls`; `Ran 627 tests across 37 files.` |
| `cd ts && bun test tests/parity.test.ts` with all six requested rows temporarily ported | Failed: `ported_files_keep_every_python_test_name` identified fifteen missing Task 8c tests; `9 pass`, `1 fail`; `Ran 10 tests across 1 file.` |
| `cd ts && bunx --no-install biome check --write` after cleanup | Exit 0; `Checked 3 files in 12ms. No fixes applied.` |
| `sh scripts/check-ts.sh` with truthful final parity | Exit 0; `626 pass`, `1 todo`, `0 fail`, `1804 expect() calls`; `Ran 627 tests across 37 files.` |

The gate checks Biome with warnings as errors, TypeScript, dependency-cruiser, knip, and Bun tests.
Dependency-cruiser reports no violations.
Knip prints two existing configuration hints for unmatched script patterns, and exits successfully.
The final command is another run of `sh scripts/check-ts.sh` after writing this report.

## TypeScript differences

No carried assertion is impossible in TypeScript, and no test was weakened or omitted for language reasons.
Python frozen dataclasses and tuples use readonly interfaces and arrays as required.
Python sets use JavaScript sets with structural test equality.
The parameterised thread test wraps each boolean case in a one-element array, as the brief requires.

## Concerns and integration work

The brief says Task 9a consumes Task 8c, but this worktree has no `ts/tests/core/check-threads.test.ts` and no Task 8c append-only thread checker.
Only Task 9a's view-specific test was added to that file, respecting the task lane.
Temporarily marking its parity row `ported` failed because these fifteen Python test names have no existing TypeScript implementation:

- `open_thread_passes_every_check`.
- `unresolved_about_fails_check_2`.
- `duplicate_thread_id_fails_check_2`.
- `file_name_must_start_with_the_id`.
- `appending_a_message_passes`.
- `closing_passes`.
- `editing_a_published_message_fails_check_5`.
- `removing_a_message_fails_check_5`.
- `changing_about_fails_check_5`.
- `changing_raises_fails_check_5`.
- `reopening_fails_check_5`.
- `message_after_closing_fails_check_5`.
- `closing_without_a_message_fails_check_5`.
- `missing_published_thread_fails_check_2`.
- `changing_opened_fails_check_5`.

Therefore its parity row remains `planned`, an explicit deviation from the requested six-row flip.
The coordinator should combine the new visibility test with Task 8c's thread suite and mark that row `ported` once all names exist.
This is missing prerequisite work, not a TypeScript limitation.

The remaining existing todo is `thread_id_is_not_number_feedback` in `thread-files.test.ts`, whose parity row names Task 10.
It was left untouched because the task-specific file list authorises the four deferred tests above and does not authorise completing the Task 10 number-feedback work.
No other uncertainty remains.
