# Task 2 report

Implemented the link action, dependency checks, derived links, read warnings, feedback, and writing guidance.
No files were staged, committed, or pushed.
No lodge records were written, so no `lodge add` was required.

## Changes per file

- `src/lodge/core/model.py`: adds `Action.LINK`.
- `src/lodge/core/derive.py`: excludes link changes from touches, adds newest-first `linked_by`, and derives `supports` for known entries in ID order.
The diff adds 14 lines and replaces one existing line, within the 15-line allowance.
- `src/lodge/core/check_cycles.py`: adds iterative reachability and one check 8 problem per cycle member, naming the other mutually reachable members in sorted order.
- `src/lodge/core/check_state.py`: checks missing and self dependencies, and runs check 8.
- `src/lodge/core/check_entries.py`: accepts edit or link for dependency-only edits, and rejects link for new entries or changes to other fields.
- `src/lodge/core/check_change.py`: rejects newly added dependencies on entries retired in the resulting snapshot, including retirement in the same add.
- `src/lodge/core/views.py`: adds direct dependency warnings and provenance links, retaining the last substantive change as the entry's author and date.
The diff adds 15 lines, within the 30-line allowance.
- `src/lodge/core/feedback.py`: asks about existing entry IDs named in statements but absent from dependencies, once per ID in appearance order.
- `src/lodge/core/__init__.py`: exports `check_cycles`.
- `src/lodge/cli/guide.md`: adds the two required writing sentences and lists link among the actions.
Removes two blank lines around the fenced example to retain the existing 60-line limit without removing guidance.
- `tests/core/test_check_links.py`: covers dependency-only changes, invalid link actions, missing and self dependencies, cycles, and retired dependencies.
- `tests/core/test_derive_links.py`: covers link exclusion from changes and review flags, plus reverse dependencies.
- `tests/core/test_views_links.py`: covers warnings, unchanged-text edits, link preservation of warnings and authorship, and provenance order.
- `tests/core/test_feedback_links.py`: covers missing dependency feedback, duplicate and unknown mentions, listed dependencies, and self mentions.
- `tests/app/test_writes.py`: adds both refusal tests and asserts no publication.
- `tests/e2e/test_guide.py`: checks the new writing guidance.

## First test run

All 26 named tests were written before implementation.
The required first command was `uv run pytest tests/core tests/app/test_writes.py tests/e2e/test_guide.py -q`.
Its last line was `21 failed, 517 passed in 2.48s`.
The complete first output remains in the ignored `.drafts/task-2-first.txt`.
Five compatibility cases already passed before implementation, so they have no first failing output; this is a deviation from the literal requirement that every new test fail.
No existing test was changed.

| Test | First failing output or baseline result |
| --- | --- |
| `test_link_changing_rests_on_only_passes` | ValueError: 'link' is not a valid Action |
| `test_rests_on_change_without_decision_fails_check_4` | assert [(4, "s-aaaaa...n's changes")] == [(4, "s-aaaaa...n's changes")] |
| `test_edit_may_change_rests_on` | Passed before implementation; existing behaviour already satisfies this case. |
| `test_link_changing_the_statement_fails_check_4` | ValueError: 'link' is not a valid Action |
| `test_link_for_a_new_entry_fails_check_4` | ValueError: 'link' is not a valid Action |
| `test_unknown_rests_on_fails_check_2` | assert False |
| `test_rests_on_itself_fails_check_2` | assert False |
| `test_two_entry_cycle_fails_check_8_on_both` | AssertionError: assert [] == [('lodge/spec...th s-aaaaaa')] |
| `test_three_entry_cycle_names_the_other_two` | AssertionError: assert [] == ['s-aaaaaa: i...aa, s-bbbbbb'] |
| `test_new_rest_on_retired_entry_fails_check_6` | assert False |
| `test_kept_rest_on_retired_entry_passes_check_6` | Passed before implementation; existing behaviour already satisfies this case. |
| `test_link_is_not_a_change` | ValueError: 'link' is not a valid Action |
| `test_link_raises_no_flag` | ValueError: 'link' is not a valid Action |
| `test_supports_is_the_reverse_of_rests_on` | AttributeError: 'Derived' object has no attribute 'supports' |
| `test_rests_on_retired_mark` | AssertionError: assert 'rests on s-bbbbbb, retired' in () |
| `test_rests_on_changed_since_mark` | AssertionError: assert 'rests on s-bbbbbb, changed since' in () |
| `test_edit_with_unchanged_text_clears_changed_since` | Passed before implementation; existing behaviour already satisfies this case. |
| `test_link_after_the_change_keeps_changed_since` | ValueError: 'link' is not a valid Action |
| `test_entry_level1_keeps_the_author_after_a_link` | ValueError: 'link' is not a valid Action |
| `test_level3_lists_rests_on_supports_and_linked_by` | ValueError: 'link' is not a valid Action |
| `test_statement_naming_an_unlisted_entry_asks` | AssertionError: assert [] == ['the stateme... to rests_on'] |
| `test_listed_named_entry_no_feedback` | Passed before implementation; existing behaviour already satisfies this case. |
| `test_own_id_no_feedback` | Passed before implementation; existing behaviour already satisfies this case. |
| `test_cycle_made_in_one_add_is_refused` | lodge.app.errors.LodgeError: d.md:6: changes.action must be one of 'create', 'edit', 'retire', not 'link' |
| `test_rest_on_entry_retired_in_the_same_add_is_refused` | AssertionError: assert <AddOutcome.PUBLISHED: 'published'> is <AddOutcome.CHECK_FAILED: 'check failed'> |
| `test_guide_names_rests_on_and_link` | assert ('rests_on' in "# lodge: the guide for agents\n\nlodge holds a project's decisions and specification entries.\nA decision records a c...-xxxxxx]`.\n\nExit codes: 0 done, 1 check failed or the store changed under you (add again), 2 usage or environment.\n") |

The initial application cycle test failed at action parsing before reaching the check.
After implementation, its attempted header replacement did not add the dependency because an empty `rests_on` is omitted from generated drafts.
Corrected the fixture to insert `rests_on` after the opening header delimiter, then verified both check 8 problems and no publication.

## Commands and final output

- Initial required pytest command: `21 failed, 517 passed in 2.48s`.
- `uv run ruff format`: initially `8 files reformatted, 398 files left unchanged`, then `2 files reformatted, 404 files left unchanged` after annotations and line wrapping.
- Intermediate required pytest reruns: `2 failed, 536 passed in 2.62s`, then `1 failed, 537 passed in 2.47s`.
These exposed the faulty application fixture and the guide length, both corrected.
- Intermediate `uv run ruff check`: initially `Found 3 errors.`, corrected by wrapping test strings; final `All checks passed!`.
- Intermediate `uv run mypy`: initially `Found 35 errors in 4 files (checked 167 source files)`, corrected by annotating the new tests; final `Success: no issues found in 167 source files`.
- `uv run vulture`: successful, no output.
- Full builder gate: `uv run ruff format --check && uv run ruff check && uv run mypy && uv run vulture && uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py && uv run lodge check --gate`.
Formatting: `406 files already formatted`; lint: `All checks passed!`; typing: `Success: no issues found in 167 source files`; pytest: `1111 passed in 31.10s`; lodge: `ok`, followed by area notes ending `note: area writing: added`.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer`: `1 passed, 2 deselected in 0.29s`.
- Final focused run after the guide spacing adjustment: `uv run pytest tests/core/test_check_links.py tests/core/test_derive_links.py tests/core/test_views_links.py tests/core/test_feedback_links.py tests/app/test_writes.py tests/e2e/test_guide.py -q`: `46 passed in 0.31s`.
- `git diff --check`: successful, no output.

## Concerns and coordinator checks

The design's Rests on section says level 3 lists “supported by”, while the brief explicitly asks for “supports”.
Following the stated design precedence, the displayed reverse relation is `supported by`; the derived field remains `supports`, and the test asserts that distinction.
The coordinator should confirm this label interpretation.
Five new tests already passed against Task 1, as documented above.

Socket-bound files `tests/viewer/test_server.py` and `tests/e2e/test_view.py` were excluded from the builder gate as instructed, apart from the separately passing port test.
The coordinator must run `sh scripts/check.sh` outside the sandbox, stage explicit paths, commit, and push.
The untracked task brief was present before work began and was left unchanged.
