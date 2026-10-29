# Task 4 report: snapshot and derived facts

## Built

- `src/lodge/core/snapshot.py`: `Files`, `Tree` (`attachments` defaults to empty), `Snapshot`, `load`.
  Files are read in sorted path order, so "the first is kept" is the lowest path.
  Files under `lodge/attachments/` are listed (joined with `Tree.attachments`) and never parsed.
  Problem 1 for a stray file under `lodge/`, and for a record in the wrong folder (a decision under `lodge/spec/`, an entry under `lodge/decisions/`); problem 2 for a repeated ID, its message naming both paths.
- `src/lodge/core/derive.py`: `Derived`, `derive`, `is_author`.
  Every list is newest first by (aware date, ID); reverse maps hold known targets only.
  A decision's `confirms` counts only when the confirming decision is an author decision.
  The flag clears when any author decision confirms or replaces the flagged one.
- `tests/core/builders.py`: `decision`, `entry`, `area`, `files_of`, plus `at(minute)` and `next_id`.
- Exports added to `lodge.core`; `Tree.rev` added to `vulture_allow.py` (read first by the store port, unused until then).

## Red, before the code

Before any module existed, both test files failed at collection:
`ImportError: cannot import name 'Tree' from 'lodge.core'` (test_snapshot) and `cannot import name 'Snapshot' from 'lodge.core'` (test_derive).
With signature stubs raising `NotImplementedError`, every test failed on that line:
`FAILED tests/core/test_snapshot.py::<test> - NotImplementedError` for all 5 snapshot tests, and likewise for all 18 derive tests (`test_is_author`, the 17 flag, status, and link tests).
23 failed in 0.25s.

Tests beyond the brief's list: `test_record_in_the_wrong_folder_is_problem_1`, `test_is_author`, `test_author_decisions_are_never_flagged`, `test_author_edit_dated_after_the_agent_does_not_flag_it`, `test_confirm_by_an_agent_does_not_clear`, `test_imported_after_imported_author_edit_not_flagged`.

## Final gate

`sh scripts/check.sh`: ruff format, ruff, mypy strict, vulture clean; `433 passed in 2.01s`.

## Concerns

- The wrong-folder problem 1 is my addition (the brief does not list it); without it a decision file under `lodge/spec/` loads silently as an entry in an area named `decisions`.
- A flag looks only at the single latest change before D on an entry; when that is an imported author decision and D is imported, D is not flagged even if an earlier non-imported author edit exists.
- `derive` ignores dangling targets (IDs not in the snapshot); resolving them is check 2's job.
- Flag clearing does not require the confirming or replacing author decision to be dated after the flagged one.

## Fix round 1

Red before the fix: 7 failed, 18 passed (`ValueError: tuple.index(x): x not in tuple` for the two B1 tests, `assert frozenset() == {'d-bbbbbb'}` for the other five).

- B1: the latest earlier change comes from an index over every changed entry, known or not; `Derived.changed_by` still lists known entries only (`test_agent_change_to_missing_entry_does_not_crash`, `test_agent_after_author_edit_of_unparsable_entry_flagged`).
- B2: only `is_author(d) and d.imported_from is None` skips the flag, so an imported author decision is flagged on decision and entry targets (`test_imported_author_replacing_live_author_decision_flagged`, `test_imported_author_editing_live_author_entry_flagged`).
- I1: the flag clears only on a non-imported author decision ordered after the flagged one (date, then ID) naming it in `confirms` or `replaces` (`test_imported_author_confirm_does_not_clear`, `test_confirm_dated_before_does_not_clear`); `Derived.confirmed_by` is unchanged and still lists every author confirmer.
- I2: an imported decision that changes an entry is flagged when any non-imported author decision changed it, whatever the dates (`test_backdated_import_editing_live_author_entry_flagged`).
- M1: `earlier_target` is `touches_author_decision`, `earlier_change` is `follows_author_change`; no test needed.

`sh scripts/check.sh`: all gates clean, `440 passed`.

## Fix round 2

Red on 4fb80cc: 2 failed, 24 passed (`assert frozenset({'d-aaaaaa'}) == frozenset()` and `assert frozenset({'d..., 'd-cccccc'}) == frozenset()`).

- N1: the I2 clause is removed, so an imported decision follows the same latest-earlier-change rule by date as a live one; B2, B1, and I1 are untouched. `test_backdated_import_editing_live_author_entry_flagged` is replaced by `test_imported_author_creation_not_flagged_by_her_later_live_edit` (R1) and `test_imported_agent_edit_before_her_later_live_edit_not_flagged` (R2). The back-dated import case now belongs to Task 5's check.
- N3: the `_flagged` docstring names agent decisions and imported decisions.

`sh scripts/check.sh`: all gates clean, `441 passed`.

## LODGE round

Red before the code: 8 failed, 416 passed (before the split of two oversize test files, which moved tests only).
Failing lines: `KeyError: 'lodge/spec/storage/_area.md'` (`test_replacing_retirement_restores_order`), `assert [(6, 'd-ddddd... is retired')] == []` (both check 6 tests), `assert frozenset() == {'d-dddddd'}` (P3 and P4 tests), `assert frozenset() == {'d-cccccc'}` (confirmation dated after), `assert ('retired', 'replaced') == ('current', 'replaced')` (replaced retirement), `assert [] == [Feedback(...)]` (edit-back question).
Passing at once, as guards: `test_imported_confirmation_does_not_make_a_decision_hers`, `test_entry_stays_retired_while_another_retirement_stands`, `test_replacing_one_of_two_retirements_leaves_the_order`, and the two negative edit-back tests.

- LODGE-6, `derive.py`: a decision a non-imported author decision confirms, in any date order, counts as hers for the flag; `_counts_for` still limits an imported decision to non-imported counting decisions (`test_agent_rewrites_an_edit_she_confirmed`, `test_agent_replaces_a_decision_she_confirmed`, `test_confirmation_dated_after_the_later_agent_change_still_counts`, `test_imported_confirmation_does_not_make_a_decision_hers`).
- LODGE-7, `derive.py`: an entry is retired only while a retiring decision is not replaced (`test_replacing_the_retirement_makes_the_entry_current`, `test_entry_stays_retired_while_another_retirement_stands`).
- LODGE-7, `check_change.py` (check 6): an entry counts as retired when it is retired both published and after, so the replacing decision or a later one may edit it (`test_check_6_replacing_the_retirement_lets_the_decision_edit_the_entry_again`, `test_check_6_a_later_decision_may_edit_an_entry_whose_retirement_was_replaced`).
- LODGE-7, `apply.py`: an entry retired before the add and current after it (read from the add's files) is appended to its area's order (`test_replacing_retirement_restores_order`, `test_replacing_one_of_two_retirements_leaves_the_order`).
- LODGE-7, `feedback.py`: an author decision that replaces an agent decision whose edit of an entry is still that entry's latest change, and does not change the entry, is asked whether it edits it back, one note per entry (`test_author_replacing_an_agent_edit_is_asked_whether_it_edits_back`, `test_no_edit_back_question_when_the_decision_edits_the_entry`, `test_no_edit_back_question_when_a_later_change_stands`).
- Test files over 300 lines were split: `tests/core/derivation.py` (shared helpers), `test_derive_confirmed_retired.py`, `test_check_retired.py`.
- Part 2, `derive.py` (concern 2, ruled): the latest change to an entry before a decision skips changes by a decision that a non-imported author decision replaces, in any order (`test_agent_edit_after_she_replaced_an_agent_retirement_flagged`, `test_agent_edit_after_she_replaced_an_agent_edit_flagged` failed first with `assert frozenset() == {'d-dddddd'}`; `test_agent_edit_after_an_agent_replaced_by_an_agent_is_as_before` guards the old behaviour); `sh scripts/check.sh` clean, `767 passed`.
- Part 3, `derive.py`, `views.py`, `feedback.py` (L1 to L4, ruled): L1 the replaced-changes skip applies only to decisions that are neither author decisions nor confirmed by her (`test_agent_edit_after_she_corrected_her_own_decision_flagged`, `test_agent_edit_after_she_corrected_her_own_edit_flagged`); L2 `Derived.revived` (decision to the entries whose last standing retirement it replaces), and a reviving decision counts as changing the entry, so it shows in `changed_by`, the flag, and `touched_by_flagged` (`test_agent_reviving_her_retired_entry_flags_the_entry`; `test_agent_reviving_an_entry_an_agent_retired_is_not_flagged` guards H6); L3 `retired by` skips replaced retirements (`test_retired_by_names_a_standing_retirement`); L4 feedback names each entry a replacing decision revives and the way to keep it retired (`test_replacing_her_retirement_says_which_entry_comes_back`). Red before the code: 5 failed (`assert frozenset() == {'d-dddddd'}` twice, `KeyError: 's-aaaaaa'`, `assert [] == [Feedback(...)]`, `assert 'retired by d-bbbbbb' in (...)`); `sh scripts/check.sh` clean, `773 passed`.
- Part 4, `feedback.py`, `derive.py` (recheck 2, N1 to N3): N1 the revival line skips an ID in `replaces` that is not in the snapshot instead of raising (`test_dangling_replaces_leaves_the_revival_line_and_does_not_raise`, `KeyError: 'd-zzzzzz'` first); N2 the edit-back question fires when the replaced agent edit is the entry's newest create or edit, passing over retirements and revivals, and its text now says "latest edit of that entry" (`test_rejecting_an_agent_edit_and_a_later_agent_retirement_asks_to_edit_back`); N3 `_revived` lists an entry once per decision, and one revival line names every replaced retirement, none when the entry ends retired (`test_one_revival_line_names_every_replaced_retirement`, `test_no_revival_line_when_the_entry_stays_retired`). Red before the code: 4 failed; `sh scripts/check.sh` clean, `795 passed`.
- Part 5, `derive.py`, `feedback.py` (recheck 3, N4 and N5): N4 `Derived.revived` lists known entries only and feedback reads entry status with `.get` (`test_revival_of_an_unparsable_entry_does_not_crash`, `test_revival_of_a_dangling_entry_does_not_crash`, `KeyError: 's-aaaaaa'` and `'s-zzzzzz'` first); N5 the revival line names only retirements whose earliest replacement is this decision (`test_revival_line_names_only_retirements_that_were_standing`); U1 pinned by `test_unparsable_decision_in_replaces_does_not_crash`, which passed already. `sh scripts/check.sh` clean, `799 passed`.

`sh scripts/check.sh` after the first part: all gates clean, `764 passed`.
