# Task 10 report

Outcome: DONE_WITH_CONCERNS.
The required Unicode database difference is documented below.
No dependencies were added, no Python source or tests were edited, no commits or pushes were made, and no reviewer files were edited.

## Changes by file

- `ts/src/core/feedback.ts`: ported the complete Python feedback behaviour, including length guidance, named specification dependencies, related decisions, number handles, already replaced decisions, edit-back questions, revival notes, author waiting notes, and shared area ranks.
  Message order, deduplication, code-point sorting, code-point title lengths, and Python whitespace splitting follow the source.
  Regular expressions use Unicode mode, explicit word lookarounds, Unicode decimal digits, and `PY_SPACE_CLASS`.
- `ts/src/core/index.ts`: exported `Feedback`, `feedback`, and `areaFeedback` through `#core`.
- `ts/tests/core/feedback.test.ts`: ported 19 guidance, related-decision, number, author-waiting, and ordering tests.
- `ts/tests/core/feedback-edit-back.test.ts`: ported the remaining four tests from `test_feedback.py`, covering edit-back questions and the retirement message.
  This split keeps both files below 300 lines, and each file has its own small local helper without a dependency between test files.
- `ts/tests/core/feedback-links.test.ts`: ported all three named-entry tests.
- `ts/tests/core/feedback-revival.test.ts`: ported all ten revival and already-replaced tests, including malformed and dangling records.
- `ts/tests/core/area-feedback.test.ts`: carried all three Python area feedback tests, including every shared-rank case.
  No TypeScript area feedback implementation existed before this task.
- `ts/tests/core/thread-files.test.ts`: replaced the deferred `thread_id_is_not_number_feedback` with its Python assertion and added its imports.
  Existing thread tests were preserved.
- `ts/tests/parity.json`: marked the four feedback Python test files and `test_thread_files.py` as `ported`, and registered the split feedback test file.
- `docs/superpowers/plans/2026-11-02-lodge-server-core/task-10-report.md`: this report.

## Test-first evidence

All 39 tests from the four Python feedback files and the deferred thread test were written before `feedback.ts` or its exports existed.
The initial `cd ts && bun test tests/core` failed at import time in all five test files.
The exact shared first error was `SyntaxError: Export named 'feedback' not found in module` for the feedback, feedback-links, feedback-revival, and thread-files tests.
For area-feedback it was `SyntaxError: Export named 'areaFeedback' not found in module`.
The missing-export failure applies to every test listed below, including the four subsequently moved from feedback.test.ts into feedback-edit-back.test.ts.
The brief explicitly accepts missing modules or exports as the first failure.
These are newly ported tests against a new module, so no mutation of earlier-task code was needed.

### feedback.test.ts

- `clean_decision_no_feedback`.
- `title_over_guidance`.
- `decision_statement_over_guidance`.
- `spec_statement_over_guidance`.
- `statement_at_the_limit_is_clean`.
- `words_split_on_whitespace`.
- `reasoning_over_guidance`.
- `related_decision_asks_replace_or_narrow`.
- `related_lists_each_with_its_title`.
- `related_silent_when_it_replaces_or_narrows`.
- `number_without_handle`.
- `number_in_reasoning_counts`.
- `numbers_in_backticks_ignored`.
- `numbers_ignore_ids_codes_and_dates`.
- `number_in_a_word_that_is_not_a_code_is_flagged`.
- `numbers_with_handle_are_clean`.
- `decision_derive_flags_waits_for_author`.
- `feedback_on_decision_with_changes_and_related`.
- `one_call_covers_every_added_record`.

### feedback-edit-back.test.ts

- `author_replacing_an_agent_edit_is_asked_whether_it_edits_back`.
- `no_edit_back_question_when_the_decision_edits_the_entry`.
- `no_edit_back_question_when_a_later_change_stands`.
- `replacing_her_retirement_says_which_entry_comes_back`.

### feedback-links.test.ts

- `statement_naming_an_unlisted_entry_asks`.
- `listed_named_entry_no_feedback`.
- `own_id_no_feedback`.

### feedback-revival.test.ts

- `dangling_replaces_leaves_the_revival_line_and_does_not_raise`.
- `rejecting_an_agent_edit_and_a_later_agent_retirement_asks_to_edit_back`.
- `one_revival_line_names_every_replaced_retirement`.
- `no_revival_line_when_the_entry_stays_retired`.
- `unparsable_decision_in_replaces_does_not_crash`.
- `revival_of_an_unparsable_entry_does_not_crash`.
- `revival_of_a_dangling_entry_does_not_crash`.
- `revival_line_names_only_retirements_that_were_standing`.
- `replacing_a_decision_another_decision_already_replaced_says_so`.
- `replacing_a_decision_only_this_decision_replaces_is_silent`.

### area-feedback.test.ts

- `shared_rank_feedback`.
- `unshared_rank_no_feedback`.
- `unwritten_area_no_feedback`.

### thread-files.test.ts

- `thread_id_is_not_number_feedback`.

## Commands and results

Read-only inspection used `cat`, `rg`, `sed`, `wc -l`, `git status --short`, and `git diff` on the brief, `CLAUDE.md`, the named Python source and tests, relevant TypeScript modules, package metadata, and probes 23 and 27.
The cloud runtime guidance was read; this session exposes no `environment_status` tool, and the task required no network or container work.

| Command | Result or last lines |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | Both agent and author queues: `nothing`. |
| `python /tmp/port-feedback-tests.py` | Created the initial TypeScript test translations, then manually corrected TypeScript names, collection shapes, and typing; exit 0 with no output. |
| `cd ts && bun test tests/core` before implementation | `598 pass`, `5 fail`, `5 errors`, `1514 expect() calls`, `Ran 603 tests across 46 files.` |
| `cd ts && bun test tests/core` after implementation | `668 pass`, `0 fail`, `1630 expect() calls`, `Ran 668 tests across 46 files.` |
| `cd ts && bunx --no-install biome check --write --unsafe src/core/feedback.ts src/core/index.ts tests/core/*feedback*.test.ts tests/core/thread-files.test.ts` | `Checked 7 files`, `Fixed 7 files`; removed unused imports and formatted the new code. |
| `cd ts && bunx --no-install tsc --noEmit -p .` | Initially reported optional indexed values in tests; these were corrected using optional chaining, plus an explicit missing-fixture check. |
| Subsequent scoped `biome check --write` commands | Final result: `Checked 1 file`, `No fixes applied`. |
| First `sh scripts/check-ts.sh` | Failed at the remaining optional indexed message in `number_in_reasoning_counts`; fixed before the successful gates. |
| Second `sh scripts/check-ts.sh`, before parity changes | Exit 0; `845 pass`, `0 fail`, `2146 expect() calls`, `Ran 845 tests across 54 files.` |
| `cd ts && bunx --no-install biome format --write tests/parity.json` | `Formatted 1 file`, `Fixed 1 file`. |
| Third `sh scripts/check-ts.sh`, after parity changes | Exit 0; `845 pass`, `0 fail`, `2158 expect() calls`, `Ran 845 tests across 54 files.` |
| Python `isdecimal()` enumeration with `uv run --frozen python`, compared with Bun `\p{Nd}` enumeration | Exactly 90 additional code points, listed below. |
| `git diff --check` | Exit 0; no output. |
| Final `sh scripts/check-ts.sh` | Exit 0; `845 pass`, `0 fail`, `2158 expect() calls`, `Ran 845 tests across 54 files.` |

The successful gate includes Biome with warnings treated as errors, TypeScript, dependency-cruiser, knip, parity checks, structure checks, and all Bun tests.
Dependency-cruiser reported `no dependency violations found (111 modules, 363 dependencies cruised)`.
Knip printed two non-failing configuration hints for unmatched scripts patterns already present in its configuration.
No network or package installation commands were used.
The temporary translation, logs, Unicode enumeration, and report-writing scripts are outside the repository.

## TypeScript differences and concerns

Every required Python test holds in TypeScript with its original title and assertions.
There are no skipped or weakened parity tests and no remaining deferred thread test.

As required by the brief, `_CODE`, `_DATE`, and `_NUMBER` use `\p{Nd}`.
Bun recognises 90 decimal digits absent from Python 3.13's Unicode 15.1 database, so those patterns accept these additional code points:

- U+10D40, U+10D41, U+10D42, U+10D43, U+10D44, U+10D45, U+10D46, U+10D47, U+10D48, U+10D49.
- U+116D0, U+116D1, U+116D2, U+116D3, U+116D4, U+116D5, U+116D6, U+116D7, U+116D8, U+116D9.
- U+116DA, U+116DB, U+116DC, U+116DD, U+116DE, U+116DF, U+116E0, U+116E1, U+116E2, U+116E3.
- U+11BF0, U+11BF1, U+11BF2, U+11BF3, U+11BF4, U+11BF5, U+11BF6, U+11BF7, U+11BF8, U+11BF9.
- U+11DE0, U+11DE1, U+11DE2, U+11DE3, U+11DE4, U+11DE5, U+11DE6, U+11DE7, U+11DE8, U+11DE9.
- U+16130, U+16131, U+16132, U+16133, U+16134, U+16135, U+16136, U+16137, U+16138, U+16139.
- U+16D70, U+16D71, U+16D72, U+16D73, U+16D74, U+16D75, U+16D76, U+16D77, U+16D78, U+16D79.
- U+1CCF0, U+1CCF1, U+1CCF2, U+1CCF3, U+1CCF4, U+1CCF5, U+1CCF6, U+1CCF7, U+1CCF8, U+1CCF9.
- U+1E5F1, U+1E5F2, U+1E5F3, U+1E5F4, U+1E5F5, U+1E5F6, U+1E5F7, U+1E5F8, U+1E5F9, U+1E5FA.

For `_CODE`, this can also make a code with those digits eligible for known-code suppression.
For `_DATE`, it can suppress a date-shaped token containing those digits.
For `_NUMBER`, it can emit a numeric warning for those digits.
This is the known difference explicitly required by probes 23 and 27, and no additional Python test needed a changed expectation.
No other unresolved implementation uncertainty was identified.
