# Task 9 recheck 1: fix round 1 (a7e666f)

Scope: the fix diff 2bde23a..a7e666f against `task-9-review.md` (B1, I1, I2, M1 to M7) and the two Task 9 rulings on B1 and I1.
Scratch copy: `git archive a7e666f` in the reviewer's scratch directory; probes in `recheck-t9/probes/` beside it (the review's `p1` to `p7`, plus `p8`, `p8b`, `p8c`, `p9`, `p10`, and `fakessh.py`), git 2.56.0 in a temporary directory with an empty `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, local bare remotes, no network.

Counts: 1 Blocking (new), 1 Important (new), 1 Minor (new); all ten review findings answered.
Verdict: not clean; fix round 2 needs N1 and N2.

## What I ran

- `UV_OFFLINE=1 sh scripts/check.sh` in the scratch copy: green, 791 passed.
- `tests/gitstore` 20 times: 0 failures.
- The new and changed tests against 2bde23a (its source, a7e666f's `tests/gitstore`): 15 failed, 65 passed; `test_a_fifo_does_not_hang_the_read` deselected because it hangs on the old code, which is its failure.
  The two new tests passing on the old code (`test_publish_through_a_file_in_the_way_is_a_lodge_error`, `test_publish_still_stages_after_a_replace`) are guards, not answers to a finding.
- The test diff hides nothing: the edits to `test_checkout.py` and `repos.py` move the `project` helper into `repos.py` and change no assertion.
- `p4_race.py` with real processes: two clones, 20 rounds, 0 bad (before: 20 of 20 bad); four worktrees and three clones, 8 rounds, 0 bad (before: 8 of 8); four worktrees of one clone, 10 rounds, 0 bad.
  Every round: all files on the remote, linear history, no lock left.
- `p6_checkout_race.py`, 15 rounds: 0 bad.

## The review's findings

- B1: answered for the paths the review named (`checkout.py:112-128` `_refuse_links` under the lock, `checkout.py:69-79` for `lodge` itself, `checkout.py:82-109` reads links as their text).
  `p1`: (a) reads the link text, (b) and (c) refuse with a `LodgeError` and leave the outside folder unchanged, (d) refuses `lodge` as a link.
  The temporary file the fix introduces reopens the same hole (N1).
- I1: answered (`plumbing.py:62-79`, `branch.py:71`).
  `p7` returns `REJECTED`; the races above are clean.
  The dispatch's question: a push failing for another reason stays a `LodgeError`.
  A local pre-push hook refusal gives `refused by hook` (`p5` d), a missing remote gives git's line (`p3` b, c), a refusing `pre-receive` gives `remote: no` (the existing test), and `p10` (another clone moved the branch, then the remote refuses everything) gives one `REJECTED` and then `LodgeError: remote: closed`, so the store cannot loop.
  It does return `REJECTED` for a push that landed (N2).
- I2: answered (`checkout.py:141-229`).
  `p2` (a) and (b) give `LodgeError`s and leave no file and no staged entry.
  The dispatch's question on the index: `p9` a, with her own staged version and a different working copy of the record, a failed stage puts back both (her working text on disk, the index blob identical to her staged one, status `MM` as before).
- M1: answered (`branch.py:84-92`, `branch.py:105-110`); `p5` a: a wrong remote within the window now says "cannot fetch nope/lodge".
- M2: answered (`plumbing.py:51-59`, `branch.py:123`); `p3` e: init succeeds beside `feature/lodge`.
- M3: answered (`checkout.py:107`); `p2` e: the read returns.
- M4: answered (`trees.py:36-43`); `p5` e lists `lodge/spec/sub`.
- M5: answered (`checkout.py:77-78`, `setup.py:46`); `p2` d: "lodge is a file, not a folder" for reads and init.
- M6: answered (`trees.py:12`).
- M7: answered differently but adequately: both modes now refuse a write to an existing attachment (`plumbing.py:24-25`), and the coordinator's ruling no longer claims otherwise.

## New findings

### N1 (Blocking): a link planted at the temporary's name writes outside `lodge/` and turns the record into a link

Handle: `src/lodge/gitstore/checkout.py:152-156`.
The temporary is a fixed name, `.<record name>.lodge-tmp`, beside the target, opened with `Path.write_bytes`, which follows a link and reuses an existing file; `_refuse_links` checks only the target's own path.
`p9_rollback.py` c: with `lodge/decisions/.d-aaaaaa-keep.md.lodge-tmp -> <outside>/victim`, an edit of `d-aaaaaa` returns `STAGED`, the outside file now reads `lodge`, and `os.replace` has moved the link onto the record, so the record itself is now a staged link.
The name is predictable for every existing record, so one committed link is enough, which is B1's scenario again.
`p9_rollback.py` b, the benign form: her own untracked file of that name is overwritten and then renamed away, so its text is lost.
Fix: create each temporary with `tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".lodge-tmp")` and write through the descriptor it returns; `O_CREAT | O_EXCL` never follows or reuses an existing name; keep the names in `temporaries` as now.
Test: a link at the old fixed name, and a regular file there, both left untouched by a publish that succeeds.

### N2 (Important): a push that reached the remote but lost its report is `REJECTED`, and `add` then publishes the decision a second time

Handle: `src/lodge/gitstore/plumbing.py:73-78`.
When the connection drops after the remote has updated the branch, `push` fails, `ls-remote` finds the branch at the new commit, which differs from the parent, so `push` returns False.
`p8_lost_report.py`: an `ssh://` remote through `fakessh.py` (a stand-in for ssh that runs the command locally and drops the first receive-pack's status report) gives `REJECTED` while the remote holds the commit.
`p8c_lost_report_decision_only.py`: one `add` of a single decision draft leaves two decisions on the remote, `d-yyyyyy` and `d-zzzzzz`, identical but for the ID, in two commits.
Before the fix this case was a `LodgeError` with nothing re-applied, so the duplicate is new; records are never deleted, so it stays in her history.
(`p8b`: a draft that creates an entry is refused on the retry instead, with the misleading "an edit draft needs a base key".)
Fix: in `push`, when `remote_tip` equals `commit`, return True (published); only a tip that is neither the parent nor the commit means the branch moved.
Test: the `fakessh.py` arrangement, or any remote whose push reports failure after the update, asserting `PUBLISHED` and one decision.

### N3 (Minor): a replaced record loses its file mode

Handle: `src/lodge/gitstore/checkout.py:154-156`.
`p9_rollback.py` d: a record at `0600` comes back as `0644` after an edit, since `os.replace` swaps in a new file; an executable record would show as a mode change in `git status`.
Fix: `os.fchmod` the temporary to the old file's mode when there is one (falls out of N1's descriptor).
Seen while reading, not run: `_put_back` (`checkout.py:200-204`) removes created folders in the order the writes made them, so with `lodge/spec` itself missing, two writes into two new areas leave `lodge/spec` behind empty; harmless, since git ignores empty folders.

## Files read

Read: `.claude/agents/rechecker.md`; the ledger's last Task 9 lines and the builder's "Fix round 1"; the full diff of `src/lodge/gitstore/` (checkout, plumbing, branch, setup, trees in full where changed); `tests/gitstore/test_checkout_safety.py` lines 104 to 165, `tests/gitstore/test_push_race.py`, and the test diffs of `test_branch.py`, `test_checkout.py`, and `repos.py`.
Not read: `test_checkout_safety.py` lines 1 to 103 (run, not read), the review package file itself (I read the same diff with `git diff 2bde23a a7e666f`).
