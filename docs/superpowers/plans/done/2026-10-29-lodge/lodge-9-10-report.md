# Fix round LODGE-9 and LODGE-10: report

## LODGE-10, reasoning of a published decision is immutable

`src/lodge/core/check_immutable.py` compares every field of a published decision except `id`, reasoning included, exactly; an agent decision's reasoning is no longer compared by words.
The shrink note is gone, so `check_immutable` returns only problems and `check_change` no longer collects notes from it.
The message is `reasoning of a published author|agent decision was changed`, and the remedy of every check 5 message is `; a correction or a shorter reasoning is a new decision that replaces it`.
`src/lodge/cli/guide.md` (still 60 lines) and `README.md` say a correction or a shorter reasoning is a new decision.
Neither document said before that reasoning may be shortened; the guide and README now say the opposite.

Tests, each failed first (22 failures in `tests/core` before the code change):
- `tests/core/test_check_immutable.py::test_check_5_agent_reasoning_changed_in_any_way_fails` (grew, shrank, reworded, reflowed); `test_check_5_agent_reasoning_unchanged_passes`.
- The header-key, statement, and author-reasoning tests failed on the new remedy text (`REMEDY_CHECK_5` in `tests/core/checks.py`).
- `tests/core/test_apply.py::test_decision_reasoning_edit_keeps_date_and_fails_check_5` (was `..._and_passes`).
- `tests/app/test_writes.py::test_feedback_skips_edited_decisions_which_the_check_refuses`: its shortened-reasoning edit is now refused (check 5); the feedback assertion is kept.

## LODGE-9, reads run checks 4, 5, and 6

`read_checked(w: Wiring)` in `src/lodge/app/state.py` runs `read_state`, then `core.check_change(load(published), snapshot, settings, clock.now())`, and adds the problems the one-state result lacks to `result`, `failing`, and `read.unrecorded`.
Time comes only through `Clock`.
`src/lodge/app/reads.py` takes a `Wiring` instead of a bare store, and every read except `draft` uses `read_checked`.
`add`, `mint`, and `--gate` still use `read_state` and their own comparison, so they behave as before (an `add` makes no extra clock reading).
Plain `lodge check` prints the folded problems with the exit rule it already had; the viewer and `lodge show` get `fails check` through `failing`.

Branch-mode rewrite: `Store.trees()` already returns the accepted tip as the published tree while a rewrite stands, so reads after a rewrite compare with the accepted tip with no port change.
Nothing in the e2e suite covers a read after a rewrite; the app tests cover the staged fake only.

Tests, each failed first (4 of 6 failed before the code change; the gate and clean-state tests pass by design):
- `tests/app/test_reads_published.py`: `test_show_flags_a_hand_edited_published_decision`, `test_search_and_timeline_flag_it_too`, `test_plain_check_lists_the_problem_and_fails`, `test_a_shrunk_agent_reasoning_fails_on_a_read`, plus `test_gate_still_reports_it_once` and `test_an_unedited_published_state_reads_clean`.
- `tests/e2e/test_check_and_gate.py::test_check_and_gate` (the D1 scenario, a hand edit then `lodge check` exit 1 with check 5 and `lodge show` with `fails check`) failed first at the old `ok` assertion; it keeps the gate assertions.
- `tests/app/test_reads.py::test_check_gate_compares_with_the_published_state` was updated: plain check now reports check 4 as the gate does (it failed first).
- `tests/viewer/test_pages.py::test_hand_edited_published_decision_fails_on_its_page_and_in_problems` was written after the code and passed at once; it was not seen failing.

## Gate

`sh scripts/check.sh` is green, 1071 tests, including `lodge check --gate` (`ok`) on the dogfooded records.
