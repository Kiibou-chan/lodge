Task 7a is implemented on the current branch, without staging, committing, pushing, installing packages, or using the network.
The reviewer’s `task-6-review.md` was not edited.
The untracked task brief was already present and was not edited.

Changes by file:

- `ts/src/core/derive.ts`: ports `Derived`, derivation, reverse links, retirement revival, and `orderKey`.
  Ordering uses `orderInstant(date)` and code point ID comparison.
  Links and statuses retain known records only.
- `ts/src/core/derive-review.ts`: splits author recognition, confirmation, flag clearing, previous standing changes, and review flags from the main derivation module.
  It imports model and snapshot types only, and the derivation module imports it in one direction.
  Sorted decision positions implement comparisons of unique `(instant, id)` ordering keys in clearing and revival calculations.
- `ts/src/core/doubts.ts`: ports local doubt and question marks, created and last changed entry marks, and dependency propagation with cycle detection.
- `ts/src/core/index.ts`: exports `Derived`, `derive`, and `isAuthor` through `#core`.
- `ts/knip.json`: adds `src/core/derive.ts` to entry points pending Task 7b’s first reader of `orderKey`.
- `ts/tests/core/derivation.ts`: ports `IMPORTED` and the file-backed snapshot helper, asserting that loading produces no problems.
- `ts/tests/core/derive.test.ts`: ports the main status, ordering, flag, confirmation, and missing or unparsable entry tests.
- `ts/tests/core/derive-imported.test.ts`: holds the imported-decision tests split from `derive.test.ts` to keep both below 300 lines.
- `ts/tests/core/derive-links.test.ts`: ports link and reverse dependency tests.
- `ts/tests/core/derive-confirmed-retired.test.ts`: ports confirmed decision and retirement revival tests and their record builders.
- `ts/tests/core/doubts.test.ts`: carries the seven doubt tests and the two required Task 9a TODOs.
- `ts/tests/parity.json`: marks `derivation.py`, `test_derive.py`, `test_derive_links.py`, and `test_derive_confirmed_retired.py` as ported, and lists the imported-test split beside the main file.
  `test_doubts.py` remains planned because its two rendering tests await Task 9a.
- This report records implementation, verification, and concerns.

Failure evidence:

- R1, before implementation: `cd ts && bun test tests/core` ended with `301 pass`, `2 todo`, `4 fail`, `4 errors`, and `Ran 307 tests across 22 files`.
  The new doubt, link, and confirmed-retired files reported `SyntaxError: Export named 'derive' not found`.
  The main derivation file initially reported `error: Expected ";" but found "new"` because the Python local variable `new` had been carried into TypeScript.
- R2, after correcting the test syntax: removing the new front door exports and running all five task test files ended with `0 pass`, `5 fail`, `5 errors`, and `Ran 5 tests across 5 files`.
  Each file reported `SyntaxError: Export named 'derive' not found`.
  The front door was restored immediately.
- M1, per-test verification: temporarily inserting `throw new Error("task7 mutation: derivation disabled")` at the beginning of `derive` made every derivation and doubt test fail with that message.
  Temporarily returning `false` from `isAuthor` made `is_author` fail with `Expected: true` and `Received: false`.
  The combined run ended with `0 pass`, `2 todo`, `49 fail`, and `Ran 51 tests across 5 files`.
  Both mutations were restored immediately.
- The snapshot helper is exercised by these tests, including its empty-problems assertion.
  It has no independent Python test function to carry.

Each implemented test below failed against M1.
The two explicitly deferred tests were registered as TODOs rather than executed.

| TypeScript file | Test | Evidence |
| --- | --- | --- |
| `derive.test.ts` | `is_author` | M1 |
| `derive.test.ts` | `replaced_and_successor` | M1 |
| `derive.test.ts` | `narrowed_stays_current` | M1 |
| `derive.test.ts` | `retired_entry` | M1 |
| `derive.test.ts` | `changed_by_newest_first` | M1 |
| `derive.test.ts` | `agent_replacing_author_flagged` | M1 |
| `derive.test.ts` | `agent_narrowing_author_flagged` | M1 |
| `derive.test.ts` | `author_decisions_are_never_flagged` | M1 |
| `derive.test.ts` | `agent_after_author_edit_flagged` | M1 |
| `derive.test.ts` | `agent_after_agent_edit_not_flagged` | M1 |
| `derive.test.ts` | `author_edit_dated_after_the_agent_does_not_flag_it` | M1 |
| `derive.test.ts` | `flag_clears_on_confirm` | M1 |
| `derive.test.ts` | `confirm_by_an_agent_does_not_clear` | M1 |
| `derive.test.ts` | `flag_clears_on_author_replace` | M1 |
| `derive.test.ts` | `flag_shows_on_targets` | M1 |
| `derive.test.ts` | `agent_change_to_missing_entry_does_not_crash` | M1 |
| `derive.test.ts` | `agent_after_author_edit_of_unparsable_entry_flagged` | M1 |
| `derive.test.ts` | `confirm_dated_before_does_not_clear` | M1 |
| `derive-imported.test.ts` | `imported_touching_only_imported_not_flagged` | M1 |
| `derive-imported.test.ts` | `imported_after_imported_author_edit_not_flagged` | M1 |
| `derive-imported.test.ts` | `imported_replacing_live_author_decision_flagged` | M1 |
| `derive-imported.test.ts` | `imported_author_replacing_live_author_decision_flagged` | M1 |
| `derive-imported.test.ts` | `imported_author_editing_live_author_entry_flagged` | M1 |
| `derive-imported.test.ts` | `imported_author_confirm_does_not_clear` | M1 |
| `derive-imported.test.ts` | `imported_author_creation_not_flagged_by_her_later_live_edit` | M1 |
| `derive-imported.test.ts` | `imported_agent_edit_before_her_later_live_edit_not_flagged` | M1 |
| `derive-links.test.ts` | `link_is_not_a_change` | M1 |
| `derive-links.test.ts` | `link_raises_no_flag` | M1 |
| `derive-links.test.ts` | `supports_is_the_reverse_of_rests_on` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_rewrites_an_edit_she_confirmed` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_replaces_a_decision_she_confirmed` | M1 |
| `derive-confirmed-retired.test.ts` | `confirmation_dated_after_the_later_agent_change_still_counts` | M1 |
| `derive-confirmed-retired.test.ts` | `imported_confirmation_does_not_make_a_decision_hers` | M1 |
| `derive-confirmed-retired.test.ts` | `replacing_the_retirement_makes_the_entry_current` | M1 |
| `derive-confirmed-retired.test.ts` | `entry_stays_retired_while_another_retirement_stands` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_edit_after_she_replaced_an_agent_retirement_flagged` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_edit_after_she_replaced_an_agent_edit_flagged` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_edit_after_an_agent_replaced_by_an_agent_is_as_before` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_edit_after_she_corrected_her_own_decision_flagged` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_edit_after_she_corrected_her_own_edit_flagged` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_reviving_her_retired_entry_flags_the_entry` | M1 |
| `derive-confirmed-retired.test.ts` | `agent_reviving_an_entry_an_agent_retired_is_not_flagged` | M1 |
| `doubts.test.ts` | `open_doubt_marks_its_record` | M1 |
| `doubts.test.ts` | `closed_doubt_marks_nothing` | M1 |
| `doubts.test.ts` | `question_open_mark_and_no_propagation` | M1 |
| `doubts.test.ts` | `doubt_reaches_entries_resting_on_it_further_down` | M1 |
| `doubts.test.ts` | `doubt_on_decision_marks_entries_it_created_and_last_changed` | M1 |
| `doubts.test.ts` | `doubt_on_decision_reaches_what_rests_on_its_entries` | M1 |
| `doubts.test.ts` | `cycle_of_rests_on_does_not_hang` | M1 |
| `doubts.test.ts` | `confirmed_decision_shows_confirmation_and_keeps_decided_by` | Task 9a TODO |
| `doubts.test.ts` | `flag_order` | Task 9a TODO |

Commands and results:

- Read-only inspection used `cat`, `sed`, `rg`, `head`, `tail`, `wc -l`, and `git diff` to read the brief, `CLAUDE.md`, runtime skill, Python sources and tests, TypeScript modules, configuration, and outputs.
  No record files were opened directly.
- `uv run --frozen --quiet lodge waiting` exited 0, ending with `waiting for the author` and `nothing`.
- Temporary Python scripts under `/tmp` generated the initial test translation, corrected local TypeScript syntax and types, split imported tests, updated parity, and generated this report.
  They produced no application runtime changes outside the listed files.
- Initial `cd ts && bun test tests/core`: R1 above.
- Targeted `bunx --no-install biome check --write --unsafe ...`: initially reported parse errors and non-null assertion warnings; the final targeted run ended `Checked 8 files in 16ms. Fixed 4 files.`
  Fixes removed unused imports and unnecessary mutable bindings, and formatted the new files.
  No lint rule was disabled.
- `bunx --no-install tsc --noEmit -p .`: initially reported an incorrect `Change[]` annotation on the retirement decision; after correction, exited 0 with no output.
- Intermediate `bun test tests/core`: ended `350 pass`, `4 todo`, `0 fail`, and `Ran 354 tests across 22 files`.
- Targeted missing-export and mutation runs: R2 and M1 above, both intentionally exited 1.
- First `sh scripts/check-ts.sh`: exited 1 on parity JSON formatting, ending `error: script "check" exited with code 1`.
- `cd ts && bunx --no-install biome format --write tests/parity.json`: exited 0, ending `Formatted 1 file in 2ms. Fixed 1 file.`
- Second `sh scripts/check-ts.sh`: exited 1 with `526 pass`, `4 todo`, and `1 fail` because the structure checker interpreted calls to a local helper named `open` as file writing outside git.
  Renaming the helper to `openThreads` resolved it without changing any rule.
- Third `sh scripts/check-ts.sh`, before marking parity ported: exited 0, ending `527 pass`, `4 todo`, `0 fail`, and `Ran 531 tests across 30 files`.
- `git diff --check`: exited 0 with no output.
- Final `sh scripts/check-ts.sh`, after marking parity ported and writing this report: exited 0, with `527 pass`, `4 todo`, `0 fail`, and `Ran 531 tests across 30 files`.
  This gate runs Biome with warnings fatal, TypeScript, dependency-cruiser, knip, and the whole Bun test suite.
  The two knip configuration hints about empty `scripts` globs are pre-existing and do not fail the gate.

No Python assertion in this task is impossible in TypeScript.
`confirmed_decision_shows_confirmation_and_keeps_decided_by` and `flag_order` remain TODOs because their `level1` dependency is assigned to Task 9a, as the brief explicitly requires.
The other two TODOs in the complete suite predate this task.

Concern: the main derivation file’s initial red run was a syntax failure rather than a missing-export failure.
Its corrected tests were verified against removed exports and the per-test M1 mutations after implementation, so that file does not have a clean pre-implementation behavioural red run.
All tests were written before implementation, but the correction and mutation chronology is reported here for review.
There are no known remaining implementation uncertainties.
The coordinator still owns the external whole-project gate, staging, commit, and push.
