# Final wave, Part B1: builder report

Branch `build-0.1`, from 1d67117.
Items 1 to 10 and 21 to 23 of Part B.
"Failed first" means the test was run before the fix and failed.
`sh scripts/check.sh`: green, 1050 passed, `lodge check --gate` ok.

## Part B items 1 to 10

1. G2, `update-ref` with the old value: `BranchStore.publish` runs `update-ref <ref> <commit> <tip>` through `attempt`, so a failure is ignored.
   Test: `test_a_landed_push_that_another_clone_built_on_is_published_and_the_newer_ref_stays` (`tests/gitstore/test_push_race.py`); failed first with the old `update-ref` (the ref was rewound).
   `tests/gitstore/fakessh.py` gained `FAKESSH_AFTER`, a shell command run once the dropped push has landed.
2. G3, a landed push that another clone built on: `plumbing.push` fetches the branch and counts the push as landed when `merge-base --is-ancestor <commit> FETCH_HEAD` holds.
   Same test; failed first (REJECTED).
3. C3, branch-mode gate note: `BranchStore.gate` carries the note "in branch mode the gate runs inside lodge add; a push to the branch by hand skips it"; the guide and README say it too.
   Test: `test_gate_says_it_runs_inside_add` (`tests/gitstore/test_branch.py`); `test_agent_edit_in_the_same_second_publishes_in_branch_mode` updated.
4. A1 and D3, `UNCHANGED`: `AddOutcome.UNCHANGED`, printed `nothing changed`, the note dropped.
   Tests: `test_unchanged_draft_publishes_nothing` (`tests/app/test_writes.py`), `test_add_nothing_changed` (`tests/e2e/test_add_new_decision_entry_area.py`), both changed to expect it.
5. H1, `FROZEN_TEXT` adds "If the author asked for this edit, tell her the file is frozen and ask before reversing it." and then "Otherwise reverse your own edit now"; text only, with one assertion in `test_frozen_edit_gets_feedback`.
6. D4, timeline `more`: `reads.timeline` returns `more`; the page says "50 of N shown."
   Tests: `test_timeline_newest_first_and_limited` (`tests/app/test_reads.py`), `test_timeline_page_says_how_many_are_shown` (`tests/viewer/test_pages.py`); failed first.
7. D5, remedies on check messages: check 5 (all four wordings) "write a new decision that replaces or narrows it", check 3 "add quote: {text, where, when} with the author's words, or record it under your own role", check 4 "list it in the decision's changes", check 2 attachment "pass the file with --attach".
   Tests: the existing exact-message tests in `tests/core/test_check_*.py`, changed first and failed; check 5 and 6 tests moved to `tests/core/test_check_immutable.py` to keep the file under 300 lines.
8. D6, `draft` of a decision: stderr note "note: decisions are immutable; to change one, write a new decision with replaces or narrows"; the `draft` help says so.
   Test: `test_draft_of_a_decision_says_decisions_are_immutable` (`tests/e2e/test_draft_then_add_edit.py`); failed first.
9. D7 and Task 13 M1, provisional IDs: a dry run prints `feedback: d-xxxxxx (provisional): ...` for newly minted decision IDs (`Added.minted`); the guide says the real add mints new IDs.
   Test: `test_dry_run_marks_new_decision_ids_provisional` (`tests/e2e/test_add_dry_run.py`); failed first.
10. D8: `lodge spec` on an empty store prints "Nothing is recorded yet."; `lodge init` ends with "next: lodge guide"; a busy port says "give another with --port".
    Tests: `test_spec_of_an_empty_store`, `test_init`, `test_init_branch_mode` (`tests/e2e/test_init_branch_mode.py`), `test_serve_reports_a_port_in_use_as_one_sentence`; changed or added first and failed.

## Part B items 21 to 23

21. M1, the deferred exit per thread: `gitstore/git.py` counts running git calls in a `threading.local`; `request_exit` defers only when the calling (main) thread runs git, and only the main thread raises the pending exit.
    Tests: `tests/gitstore/test_exit_request.py` (two); the first failed first (the exit was deferred by a request thread's git).
22. M2, `rewritten` fails closed: any non-zero exit of `merge-base --is-ancestor` counts as a rewrite, so `accept` does not move the ref.
    Test: `test_a_git_that_cannot_answer_is_not_taken_for_no_rewrite` (`tests/gitstore/test_branch_rewrite.py`); failed first.
    README: rewrite detection lives in a clone that read the branch before the rewrite.
23. M3, a refused add prints the rewrite line: `Added.freshness` carries the store's freshness on `CHECK_FAILED`, and the CLI prints it before "not published"; the freshness rewrite line now ends "tell the author; only the author accepts a rewrite, with git update-ref -d refs/lodge/accepted".
    Tests: `test_add_refuses_after_a_rewrite_and_the_gate_still_fails`, `test_rewritten_branch_is_said_and_the_gate_fails` (`tests/e2e/test_gate_after_rewrite.py`), `test_rewritten_branch_is_said_and_compared`; failed first.
