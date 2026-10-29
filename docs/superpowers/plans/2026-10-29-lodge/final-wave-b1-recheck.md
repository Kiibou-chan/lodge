# Final wave, Part B1: recheck

Checked at 2c6b62b in a scratch copy (the scratch directory); the build worktree was not touched.
`sh scripts/check.sh` in the copy: format, ruff, mypy, vulture and 1050 tests pass; only the last step (`lodge check --gate`) stops, because the copy is not a git repository.

## Answered

Each fix was reverted in the copy and its test run; the test failed every time.
- G2 (`branch.py:114`, `update-ref` with the old value): `test_a_landed_push_that_another_clone_built_on_is_published_and_the_newer_ref_stays` fails without the old value.
- G3 (`plumbing.py:78-92`): the same test fails with `_landed_below` replaced by `False`.
- C3 (`branch.py:17,100`): `test_gate_says_it_runs_inside_add` fails without the note; guide and README say it.
- A1 and D3 (`writes.py:107`, `output.py:66`): `test_unchanged_draft_publishes_nothing` and `test_add_nothing_changed` fail with `PUBLISHED`.
- H1 (`post_tool_use.py:19-35`): text as ruled; the assertion in `test_frozen_edit_gets_feedback` covers it.
- D4 (`reads.py:59-60`, `pages.py:44-46`): `test_timeline_newest_first_and_limited` fails with `more=0`.
- D5 (`check_immutable.py:12`, `check_state.py:105,122`, `check_entries.py:34`): all four remedies as the review words them; 18 tests in `test_check_immutable.py` fail without the check 5 remedy.
- D6 (`commands.py:65`, `parser.py:119`): `test_draft_of_a_decision_says_decisions_are_immutable` fails without the note.
- D7 (`output.py:57`): `test_dry_run_marks_new_decision_ids_provisional` fails without the mark.
- D8 (`commands.py:57,76`, `server.py:80`): tests changed first; run by hand, `lodge spec` prints "Nothing is recorded yet." and `init` ends with "next: lodge guide".
- M1 (`git.py:14,25,36,50`): `test_git_in_another_thread_does_not_defer_the_exit` fails with the process-wide counter.
- M2 (`accepted.py:33`): `test_a_git_that_cannot_answer_is_not_taken_for_no_rewrite` fails with `== 1`; README line present.
- M3 (`results.py:46`, `output.py:71`, `branch.py:68-72`): `test_add_refuses_after_a_rewrite_and_the_gate_still_fails` fails without the printed freshness; wording ends as ruled.

Moved tests: every `def` and `parametrize` in the old `test_check_compare.py` exists in the union of it and `test_check_immutable.py`; the only removed lines are the old message strings.
New text: no em-dashes, British English, each says what to do next.

## Minor 1. A SIGTERM during a viewer request that holds the lock leaves `lodge.lock`

Handle: `src/lodge/viewer/server.py:21` (`ThreadingHTTPServer`, daemon request threads), `src/lodge/gitstore/lock.py:46-48` (the lock is a file removed in a `finally`), `src/lodge/gitstore/branch.py:49` (a branch-mode read fetches under the lock), `git.py:36,50` (M1's fix lets the main thread exit at once).
Scenario (reasoned, not run): `lodge view` in branch mode, a request is fetching under the lock, SIGTERM or SIGHUP arrives; the main thread raises `SystemExit`, the daemon thread is dropped at interpreter exit, its `finally` never runs, and `lodge.lock` stays; the next write waits, then after ten minutes every lock user is told the lock may be left over, which is the G1 symptom the signal handling was meant to remove.
Fix: let the viewer wait for its request threads on exit (`daemon_threads = False` with `block_on_close`, closing in the existing `finally`), since their git calls are short.

## Minor 2. `(provisional)` marks the feedback lines only

Handle: `src/lodge/cli/output.py:62-63` (the check lines print `p.message` with the record ID, unmarked).
Scenario (run): a dry run of an author decision without a quote prints `check 3: d-9wdgev: decided_by is author, but there is no quote; ...` and no `(provisional)`; the real add mints another ID, so an agent that copies the ID from the check line names a record that never exists.
Fix: mark the minted IDs in the check lines the same way, or have the guide say that every decision ID a dry run prints is provisional.

## Not findings

A refused add prints the freshness line whole; in checkout mode there is none (run), in branch mode it is one age line before "not published", which is harmless.
