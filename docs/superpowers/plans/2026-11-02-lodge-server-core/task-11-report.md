# Task 11 report

DONE_WITH_CONCERNS.
The final gate, `sh scripts/check-ts.sh`, exited 0.
No files were staged, committed, or pushed, and no packages were installed.

## Changes per file

- `ts/src/core/apply.ts`: ports draft application, ordered decision ID allocation, edits, duplicate detection, stale bases, import restrictions, writer refusals, and `Applied` and `StaleBase` interfaces.
- `ts/src/core/apply-areas.ts`: holds application state, refusal construction, area order updates, and restoration detection through derived statuses.
  This topic split keeps both implementation modules below 300 lines and imports only towards this helper from `apply.ts`.
- `ts/src/core/value-repr.ts`: consolidates P-1's representation helpers, preserving YAML list and map representations and record tuple and dataclass representations.
- `ts/src/core/drafts.ts`: uses the shared representation helper.
- `ts/src/core/fileformat.ts`: uses the same helper with tuple representation for record fields.
- `ts/src/core/index.ts`: exports `Applied`, `StaleBase`, and `applyDrafts`.
- `ts/tests/core/applying.ts`: ports the synthetic draft and snapshot helpers, and adds presence and stale-problem assertions for TypeScript.
- `ts/tests/core/apply.test.ts`: carries the application and area order tests.
- `ts/tests/core/apply-edits.test.ts`: splits the edit tests from `apply.test.ts` to respect the 300-line limit and tests a missing edit file.
- `ts/tests/core/apply-refusals.test.ts`: carries the refusal tests and adds two Python representation regression tests.
- `ts/tests/parity.json`: marks only this task's three Python files as `ported` and lists both files carrying `test_apply.py`.
  These statuses cover the apply assertions; the check integration assertions listed below remain outstanding.
- `ts/knip.json`: removes only `tests/core/builders.ts` from `entry`.
  The missing-file test consumes `snapshotOf`, which otherwise has no reader in this lane.
- This report records the implementation, evidence, and remaining integration concern.

## First failing evidence for every carried test

All 38 carried test bodies and `applying.ts` were written before `apply.ts` or its front-door export.
Both test modules initially failed to load with:

```text
SyntaxError: Export named 'applyDrafts' not found in module '<workspace>/ts/src/core/index.ts'.
```

The focused confirmation before implementation ended:

```text
0 pass
2 fail
2 errors
Ran 2 tests across 2 files.
```

This missing-export failure applies individually to every title below.
The edit titles subsequently moved to `apply-edits.test.ts`, without changing their names.

### `tests/core/test_apply.py`

- `new_decision_and_entry_and_area`: missing `applyDrafts` export, as above.
- `new_entry_appended_to_existing_area_order`: missing `applyDrafts` export, as above.
- `area_draft_already_listing_entry_not_doubled`: missing `applyDrafts` export, as above.
- `new_ids_ascend_in_draft_order`: missing `applyDrafts` export, as above.
- `edit_keeps_path_even_if_title_changes`: missing `applyDrafts` export, as above.
- `retire_removes_from_order`: missing `applyDrafts` export, as above.
- `replacing_retirement_restores_order`: missing `applyDrafts` export, as above.
- `replacing_one_of_two_retirements_leaves_the_order`: missing `applyDrafts` export, as above.
- `untouched_area_not_written`: missing `applyDrafts` export, as above.
- `import_without_date_gets_the_add_date`: missing `applyDrafts` export, as above.
- `edit_of_imported_entry_keeping_its_origin_needs_no_flag`: missing `applyDrafts` export, as above.
- `decision_reasoning_edit_keeps_date_and_fails_check_5`: missing `applyDrafts` export, as above.
- `decision_edit_changing_statement_is_judged_by_the_check`: missing `applyDrafts` export, as above.
- `area_edit_needs_current_base_and_keeps_new_entries`: missing `applyDrafts` export, as above.

### `tests/core/test_apply_refusals.py`

- `id_count_must_match_new_decisions`: missing `applyDrafts` export, as above.
- `stale_base_is_problem_naming_both`: missing `applyDrafts` export, as above.
- `edit_without_base_is_problem`: missing `applyDrafts` export, as above.
- `import_needs_flag`: missing `applyDrafts` export, as above.
- `imported_entry_needs_flag`: missing `applyDrafts` export, as above.
- `date_in_new_draft_refused`: missing `applyDrafts` export, as above.
- `decision_with_unknown_id_refused`: missing `applyDrafts` export, as above.
- `entry_statement_with_reasoning_heading_refused`: missing `applyDrafts` export, as above.
- `entry_without_area_refused`: missing `applyDrafts` export, as above.
- `entry_without_id_refused`: missing `applyDrafts` export, as above.
- `entry_in_unknown_area_refused`: missing `applyDrafts` export, as above.
- `area_change_refused`: missing `applyDrafts` export, as above.
- `two_drafts_for_one_record_refused`: missing `applyDrafts` export, as above.
- `every_problem_names_its_draft`: missing `applyDrafts` export, as above.
- `area_name_not_a_string_is_problem`: missing `applyDrafts` export, as above.
- `entry_created_and_retired_in_one_add_not_in_order`: missing `applyDrafts` export, as above.
- `base_on_new_decision_refused`: missing `applyDrafts` export, as above.
- `base_on_entry_that_does_not_exist_refused`: missing `applyDrafts` export, as above.
- `base_on_new_area_refused`: missing `applyDrafts` export, as above.
- `stale_base_message_says_to_redo_the_change`: missing `applyDrafts` export, as above.
- `edit_changing_imported_from_has_its_own_message`: missing `applyDrafts` export, as above.
- `edit_of_decision_changing_imported_from_has_its_own_message`: missing `applyDrafts` export, as above.
- `id_of_the_wrong_shape_says_so`: missing `applyDrafts` export, as above.
- `area_of_the_wrong_shape_says_so`: missing `applyDrafts` export, as above.

## Additional tests and shared-helper mutation

- `existing_entry_area_problem_uses_python_value_text` first failed with expected `area ['storage'] differs from storage; entries do not move areas` and received `area storage differs from storage; entries do not move areas`.
  Replaced JavaScript string coercion with Python-style value text for non-string values.
- `stale_base_problem_uses_python_value_text` first failed with expected substring `the base {'x': ['a']} differs from` and received `the base [object Map] differs from ...`.
  Applied the same correction to stale base messages.
- `missing_edit_file_is_stale_and_names_the_missing_file` failed against the mutation replacing `(the file is missing)` with `MUTATED` in `apply.ts`.
  Its first run ended `3 pass`, `1 fail`, and `Ran 4 tests across 1 file`.
  Restored the implementation before any subsequent successful check.
- Mutated the shared helper to return `MUTATED` for tuples, maps, and arrays, and ran the existing draft and fileformat edge tests.
  `nested_change_read_back_repr`, `draft_non_string_id_is_reported "[]" "[]"`, and `draft_non_string_id_is_reported "{x: [a]}" "{'x': ['a']}"` all failed.
  The run ended `30 pass`, `3 fail`, `109 expect() calls`, and `Ran 33 tests across 2 files`.
  Restored the helper immediately afterwards.

## Commands and outcomes

Source inspection used `cat`, `rg`, `ls`, and `sed` on `CLAUDE.md`, the brief, Python apply modules and tests, the existing TypeScript core, test helpers, parity checks, configuration, and the gate script.
No other part of the main plan was read.
The cloud runtime skill was read at session start; no environment-status tool was available, and no network work was attempted.
Local Python and Bun scripts wrote the test port, implementation files, representation extraction, and targeted edits.
Formatting used the already installed Biome through `bunx --no-install`; no installation command ran.

| Command | Last output or outcome |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author` / `nothing`; the agent queue was also empty |
| `cd ts && bun test tests/core` before implementation | `350 pass`, `4 todo`, `2 fail`, `2 errors`, `Ran 356 tests across 25 files` |
| Focused two-file apply tests before implementation | `0 pass`, `2 fail`, `2 errors`, `Ran 2 tests across 2 files` |
| `bunx --no-install biome check --write --unsafe` on this task's files | Initially exposed non-null assertion warnings; replaced them with checked helper calls; final formatting runs said `No fixes applied` |
| `bunx --no-install tsc --noEmit -p .` | Initially reported missing helper imports and stale property narrowing errors; final runs exited 0 with no output |
| Focused apply tests after the initial port | `38 pass`, `0 fail`, `57 expect() calls` |
| Draft and fileformat tests with the representation mutation | `30 pass`, `3 fail`, `109 expect() calls`, `Ran 33 tests across 2 files` |
| Refusal tests with the new area text regression | `24 pass`, `1 fail`, `34 expect() calls`, `Ran 25 tests across 1 file` |
| Refusal tests with both new text regressions | `24 pass`, `2 fail`, `35 expect() calls`, `Ran 26 tests across 1 file` |
| Three-file apply tests after fixing value text | `40 pass`, `0 fail`, `59 expect() calls` |
| `wc -l` on the apply modules and tests | Confirmed the need to split the original 303-line test file; every final file is under 300 lines |
| `git diff --check` | Exited 0 with no output |
| `bunx --no-install knip` after entry removal | Initially `Unused exports (1): snapshotOf`; final run exited 0 with only the existing unmatched script-pattern hints |
| Edit tests against the missing-file mutation | `3 pass`, `1 fail`, `7 expect() calls`, `Ran 4 tests across 1 file` |
| Final focused three-file apply tests | `41 pass`, `0 fail`, `61 expect() calls`, `Ran 41 tests across 3 files` |
| `sh scripts/check-ts.sh`, the final verification command | Exit 0; `568 pass`, `4 todo`, `0 fail`, `1683 expect() calls`, `Ran 572 tests across 33 files` |

The final gate also reported `Checked 68 files`, no dependency violations across 76 modules and 213 dependencies, and no unused exports.
Knip's two configuration hints concern the pre-existing unmatched `scripts/*.ts` and `scripts/**/*.ts` patterns.
The four todos predate this task.

## TypeScript differences and outstanding assertions

There is no inherent TypeScript limitation preventing the carried behavioural assertions.
Python dataclass identity tests use discriminated interfaces, `StaleBase` uses `stale: true`, tuple comparisons use value equality, and dates remain offset-bearing strings.

There is a lane dependency problem: `checkChange` and its checking modules are absent in this checkout.
The coordinator explicitly authorises this early lane because `apply.py` imports only modules already ported, but five Python tests import `check_change` as well.
Porting those checking modules here would violate the lane's file scope.
The following check assertions are deferred, with explicit comments in the corresponding tests:

- `new_decision_and_entry_and_area`: restore the assertion that the merged written tree passes `checkChange`.
- `retire_removes_from_order`: restore the assertion that the merged written tree passes `checkChange`.
- `replacing_retirement_restores_order`: restore the assertion that the merged written tree passes `checkChange`.
- `decision_reasoning_edit_keeps_date_and_fails_check_5`: restore the assertion that the merged written tree reports exactly check 5.
- `decision_edit_changing_statement_is_judged_by_the_check`: restore the assertion that the merged written tree fails `checkChange`.

All their apply assertions run now.
The statement edit test additionally verifies the changed statement in the emitted record.
These five tests are not complete integration equivalents of the Python tests until the missing assertions are restored.
This is a missing lane dependency, not an inability to express the assertions in TypeScript.
The coordinator must reconcile this concern at lane merge rather than treating the `ported` labels as proof of complete assertion parity.

As expressly directed by ruling d-442r2f, no `front-door.test.ts` was written, no assertion checks that all plan 1 rows are ported, and the unrelated `src/core/derive.ts` entry remains in knip.
No uncertainty remains about the implemented apply behaviour or gate outcome; the outstanding uncertainty is when the checking lane will be available for restoring those five integration assertions.
