# Final wave, Part A: builder report

Branch `build-0.1`, from bee7114.
Every item test-first; "failed first" below means the test was run before the fix and failed.

## Item 7, author reasoning compared exactly (Task 5 N1)

`check_immutable.py`: an author decision's reasoning is compared exactly, an agent's by words as before.
Test: `test_check_5_author_reasoning_reflowed_fails` (`tests/core/test_check_compare.py`), which replaces the author half of the old reflow test; failed first.

## Item 5, author lookalikes (R1)

`check_state.py`, check 3: a `decided_by` that is not `author` but contains it after strip and casefold is reported with the ruled sentence; one clause added to the guide's "Quoting the author".
Test: `test_check_3_author_lookalike` (five spellings, `tests/core/test_check_state.py`); failed first.

## Item 6, her decision behind an agent's entry edit (D2)

`derive.py`: a flagged decision that changes an entry is also filed against the previous standing change of that entry (not replaced) when that decision counts as hers (author or confirmed by her, with the imported rule of `_counts_for`).
Tests: `test_author_decision_behind_an_agent_entry_edit_awaits_the_author`, `test_agent_decision_behind_an_agent_entry_edit_is_not_flagged` (`tests/core/test_views.py`); the first failed first.

## Item 1, a rewritten `lodge` branch (G4)

New port type `Gate(published, checked, notes)` and `Store.gate(current)`; `reads.check` with `--gate` compares `published` with each checked state.
`BranchStore._fetch` reads the tracking ref before fetching; when `merge-base --is-ancestor old new` fails, `gitstore/rewrite.py` keeps the old tip at `refs/lodge/rewritten/<UTC time>` and records it in `lodge-rewritten` beside the git directory (the old tip, and the new tip that replaced it).
While the branch stands at that new tip, `gate` returns the old tree as the published one and `freshness` adds the ruled line; the next commit on the branch ends it.
`trees()` is unchanged, so `add` still builds on the fetched tip (an `add` is not blocked by the rewrite; the gate and the line are what say it).
Tests: `tests/gitstore/test_branch_rewrite.py` (four), `tests/app/test_reads.py` (three: labels, merged labels, gate notes), `tests/e2e/test_gate_after_rewrite.py`.
Failed first: the gitstore and app tests (no `gate`, no `Gate`); the e2e test was written after the fix and passed on its first run.

## Items 2 and 3, the checkout gate (C1, C2)

`gitstore/published.py` holds the published state and the committed gate (moved out of `checkout.py`, which stays under 300 lines).
`gate(current)` checks `HEAD`'s tree (`committed`) and the working tree (`working tree`) against the published state, labels a problem with the state that has it ("committed and working tree" when both), and adds the note "uncommitted record changes in lodge/; commit them before you push" when they differ; when they are the same it checks one state, unlabelled.
No base: neither `<remote>/<base>` nor `<base>` resolves, or `merge-base` fails, with `HEAD` born: `gate` raises a `LodgeError` (exit 2) naming the refs and the `base` setting, and `freshness` says the same sentence on reads.
Unborn `HEAD` is "no history": empty published state, no message.
Tests: `tests/gitstore/test_checkout_gate.py` (five), `tests/e2e/test_gate_checkout_states.py` (three: partial commit fails as `committed:`, working-tree-only failure, missing base exits 2 and reads say it).
Failed first: the gitstore tests; the e2e tests were written after the fix and passed on their first run.

## Item 4, a killed add (G1)

`main`: when run as the command (`argv is None`), SIGTERM and SIGHUP raise `SystemExit(143)` and `SystemExit(129)`.
`lock.py`: `LockHeld(LodgeError)` carries the lock path, for both the wait running out and a lock older than ten minutes.
`BranchStore.trees()`: on `LockHeld` it serves the cached ref and `freshness` says "not fetched: another lodge holds <path>; data as of <time>"; with no cached ref it raises the lock error; `publish` still waits and reports as before.
`CheckoutStore._write_all` now puts files back and restages on any `BaseException`, so an exit between the temporaries and the replaces leaves no `.lodge-tmp` file (the review's claim that the handler covers checkout mode was not true before this).
Tests: `tests/e2e/test_killed_add.py` (SIGTERM and SIGHUP in a push held by a `pre-push` hook; lock gone, exit 143 and 129; failed first), `tests/gitstore/test_branch.py` (read serves cache, left-over lock, nothing cached, publish still waits; the first two failed first, and they replace `test_fetch_waits_for_the_lock`, whose "reads fail on a held lock" behaviour the ruling reverses), `tests/gitstore/test_checkout_safety.py::test_an_exit_between_the_replaces_leaves_nothing_behind` (failed first).

## Gate

`sh scripts/check.sh`: green, 1035 passed, `lodge check --gate` ok.

## Fix round 1 (recheck of 125231f)

**G4, reworked per the ruling.**
`gitstore/accepted.py` replaces `rewrite.py`: `refs/lodge/accepted` is the last tip lodge accepted, set on first use and moved only forward (when the fetched tip contains it, after lodge's own push and after `init`), with the old value checked in `update-ref`.
Every `trees()` compares it with the remote-tracking tip, so a plain `git fetch` first no longer hides a rewrite; while the tip does not contain it, `trees()` returns the accepted tree as the published one (so `add`'s own check refuses, exit 1, with the check 2 and check 5 problems), `gate` compares the accepted tree with the current one, and the freshness line says the branch was rewritten and names `git update-ref -d refs/lodge/accepted`.
A commit on top of the rewritten tip does not end it; deleting the ref does (the next read sets it anew).
`refs/lodge/rewritten/<time>` and the `lodge-rewritten` marker are removed.
The guide gets one line: the rewrite notice is for the author, who accepts it with the git command.
Tests, all failed first: `tests/gitstore/test_branch_rewrite.py` (first read accepts, rewrite said and compared, plain `git fetch` first, stands for a later process and after a commit on top, acknowledgement clears it, fast-forward and own push move the tip), `tests/e2e/test_gate_after_rewrite.py` (said and gate fails, `git fetch` first, add refused and gate still fails, acknowledgement clears and an add works).

**N1.** `gitstore/git.py`: `request_exit(code)` exits at once when no git command runs, otherwise records the code and `attempt` raises `SystemExit` when the command returns; `main`'s handler calls it.
Test: `tests/e2e/test_killed_add.py` now also asserts the push landed (two commits on the remote branch) and no `index.lock`; failed first.

**N2.** `LockHeld.left_over`; a cache read over a lock older than ten minutes says "<path> is older than ten minutes and may be left over; delete it if no lodge is running".
Test: `test_read_serves_the_cache_when_the_lock_is_left_over` (tightened to the full line); failed first.

`sh scripts/check.sh`: green, 1041 passed, `lodge check --gate` ok.
