# Recheck: final wave, Part A (bee7114..125231f)

Rechecker, scoped to G4, C1, C2, G1, R1, D2, and Task 5 N1, plus the `BaseException` restore in `CheckoutStore._write_all`, the `Store.gate` port, and the replaced `test_fetch_waits_for_the_lock`.
Probes in a detached worktree at 125231f under `.claude/worktrees/`, removed afterwards, and probe repositories in the scratch directory.

`sh scripts/check.sh` at 125231f in the probe worktree: green, 1035 passed, `lodge check --gate` ok.

## G4, a rewritten `lodge` branch: still open (Important), in two ways

The fix detects a rewrite only inside lodge's own fetch, and forgets it at the next commit on the branch.

**Open 1, the builder's concern holds: one more add lets the rewrite through.**
Handle: `src/lodge/gitstore/rewrite.py:28-36` (`standing` ends when `tip != new`), `src/lodge/gitstore/branch.py:85-89` (`gate` falls back to the branch against itself), `src/lodge/app/writes.py` (`add` builds on the fetched tip and never asks the store about a rewrite).
Run (probe `r1`): a second clone amends the author decision's statement and force-pushes; the first clone's next read prints the rewrite line and `check --gate` gives `check 5: d-8a60bf: statement of a published decision was changed`, exit 1.
Then one routine agent `lodge add` (a new entry and decision) prints only `note: area core: order changed` and `published`, exit 0, with no word about the rewrite; afterwards reads print no rewrite line and `check --gate` prints `ok`, exit 0, while `show` still has her decision with the rewritten statement under her quote.
So the evidence lasts until the next add, which in a busy project is minutes, and the add that ends it says nothing.

**Open 2, a plain `git fetch` before lodge's own fetch hides the rewrite completely.**
Handle: `src/lodge/gitstore/branch.py:122-130` (`old` is read from `refs/remotes/<remote>/<branch>`, which git's default refspec `+refs/heads/*:refs/remotes/origin/*` also moves, forced).
Run (probe `r2`): rewrite as above, then `git fetch origin` in the first clone (what `git pull`, an IDE, or an agent does routinely), then a lodge read: no rewrite line, `check --gate` prints `ok`, exit 0, and no `refs/lodge/rewritten/*` ref exists; the same with `git fetch --all` (probe `r3`).
lodge's record of what it last saw is a ref that git rewrites on its own, so the detection depends on lodge winning a race it usually loses.

**Smallest fix covering both.**
1. Keep lodge's own record of the last tip it accepted, a ref only lodge moves, for example `refs/lodge/seen/<remote>/<branch>`: set it after a read that finds no rewrite and after lodge's own successful publish.
2. In `trees()` (every read, not only inside `_fetch`), compare that ref with the tracking tip: when it is not an ancestor, keep it under `refs/lodge/rewritten/<UTC time>` as now and record the marker; do not move `seen` while a rewrite stands.
3. A rewrite stands until acknowledged, not until the next commit: `standing` checks that the kept ref still exists and that `seen` has not moved past the marker, whatever the tip; `gate` compares the kept tree with the current one (check 5 and `_missing` are what matter; new records since then are ordinary adds and pass).
4. `add` refuses (a `LodgeError`, exit 2) while a rewrite stands whose comparison has problems of check 2 or check 5, naming the kept ref and the command that acknowledges it; the acknowledgement is deleting the kept ref (`git update-ref -d <ref>`) or a `lodge check --gate --accept-rewrite` that does so, a step the author takes, and the guide says so.
Tests: probe `r1` as an e2e test (an add after a rewrite with a changed author statement exits 2 and the gate still fails), and probe `r2` (a `git fetch` before the lodge read still reports the rewrite).

The G4 tests that exist are sound for what they cover: making `BranchStore.gate` always compare the branch with itself fails three tests (`tests/gitstore/test_branch_rewrite.py`, `tests/e2e/test_gate_after_rewrite.py`); no test covers an add after the rewrite or a `git fetch` before lodge's.

## C1, the checkout gate: answered

`src/lodge/gitstore/published.py:38-45` and `src/lodge/app/reads.py:78-101`.
Probe `k1` re-run: the partial commit now gives `check 4: committed: s-rh2haa: created, but no new decision in this change lists it with action create`, exit 1, with the note "uncommitted record changes in lodge/; commit them before you push"; staged but uncommitted records give `ok` with the same note, as the ruling intends.
Mutation: making `committed_gate` always check the working tree alone fails `tests/gitstore/test_checkout_gate.py`.

## C2, a missing base: answered

`src/lodge/gitstore/published.py:27-35`, `src/lodge/gitstore/checkout.py:39-47`.
Probe `k1` re-run: with `origin/main` and `main` removed, the tampered title now exits 2 with "the published state cannot be found: origin/main and main were tried, …"; a read prints the same sentence above its output and still answers; an unborn `HEAD` gives `ok`, as "no history" should.
Mutation: dropping the `missing` sentence fails one test in `tests/gitstore/test_checkout_gate.py` and `tests/e2e/test_gate_checkout_states.py`.

## G1, a killed add: answered

`src/lodge/main.py:84-97`, `src/lodge/gitstore/branch.py:39-58`, `src/lodge/gitstore/lock.py:15-21`.
Mutations: removing `_exit_on_signals` fails both tests of `tests/e2e/test_killed_add.py`; turning off the `LockHeld` fallback in `trees()` fails the two new read tests in `tests/gitstore/test_branch.py`.
The replaced `test_fetch_waits_for_the_lock` is answered adequately: its behaviour for writes moves to `test_publish_still_waits_for_the_lock_and_reports_it`, for a read with nothing cached to `test_read_with_nothing_cached_and_a_held_lock_is_an_error`, and only the read-with-a-cache case is reversed, as the G1 ruling says.

## The `BaseException` restore in `CheckoutStore._write_all`: answered, one Minor below

`src/lodge/gitstore/checkout.py:164-168`; mutation back to `except LodgeError` fails `test_an_exit_between_the_replaces_leaves_nothing_behind`; the bare `raise` keeps the exit code.

## The `Store.gate` port: answered

`src/lodge/app/ports.py:18-42`; both stores, `MemoryStore`, and the concurrency wrapper implement it; `reads.check` reuses the snapshot already loaded when the checked tree is the current one.
The checkout store's `gate` uses the published state its own `trees()` just read, so the gate and the read agree.

## R1, author lookalikes: answered

`src/lodge/core/check_state.py:110-115`; mutation (`if False and …`) fails 5 tests (`test_check_3_author_lookalike` and others in `tests/core`).

## D2, her decision behind an agent's entry edit: answered

`src/lodge/core/derive.py:57-71, 134-147`; mutation (dropping `*behind`) fails `test_author_decision_behind_an_agent_entry_edit_awaits_the_author`.

## Task 5 N1, author reasoning compared exactly: answered

`src/lodge/core/check_immutable.py:24-28`; mutation back to the word comparison fails `test_check_5_author_reasoning_reflowed_fails`; the test diff only splits the old author case into its own test with the new expectation, it hides nothing.

## New problems the fix introduced

**Minor N1. The SIGTERM handler makes `subprocess.run` kill a running `git` with SIGKILL, which can leave git's own lock file behind.**
Handle: `src/lodge/main.py:84-93` with `src/lodge/gitstore/git.py:21-28`; CPython's `subprocess.run` calls `process.kill()` on any exception from `communicate`, `SystemExit` included.
Scenario (reasoned from CPython's `subprocess.run`, not run): `kill <lodge pid>` (the signal to lodge alone, not its process group) while checkout mode's `git add` runs; before the fix the orphaned `git add` finished and removed `.git/index.lock`, now it is killed with SIGKILL and cannot, so the author's next `git commit` fails with "Another git process seems to be running"; the window is milliseconds, and a signal to the whole group reaches git first, which cleans up.
Fix: in `attempt`, catch `BaseException` around `subprocess.run` by using `Popen` directly, send the child SIGTERM and wait up to a second before re-raising, so git removes its own locks.

**Minor N2. A read that serves the cache because the lock is older than ten minutes no longer says the lock may be left over.**
Handle: `src/lodge/gitstore/branch.py:46-58` (both `LockHeld` messages become "not fetched: another lodge holds <path>").
Scenario (test `test_read_serves_the_cache_when_the_lock_is_left_over`): an hour-old lock gives the same line as a live one, so reads never tell anyone to delete it; only the next `add` does.
Fix: keep the lock error's message in the freshness line when it is the left-over case ("…; it is older than ten minutes, delete it if no lodge is running").

## Counts

Open: 1 Important (G4, in two ways: one add ends the notice and the gate comparison; a plain `git fetch` before lodge's hides the rewrite entirely), 2 new Minor (N1, N2).
Answered: C1, C2, G1, R1, D2, Task 5 N1, the `BaseException` restore, the `Store.gate` port, and the replaced lock test.
Probe worktree removed.
