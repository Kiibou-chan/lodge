# Task 9 recheck 2: fix round 2 (b57b2e1, f440ed8)

Scope: the diff efde8b6..f440ed8 against N1 to N3 of `task-9-recheck-1.md`, and the umask read the coordinator asked me to judge.
Scratch copy: `git archive f440ed8` in the reviewer's scratch directory; probes in `recheck2-t9/probes/`, with git in a temporary directory as before.

Counts: 0 Blocking, 0 Important, 1 Minor (new); N1, N2, and N3 answered.
Verdict: clean.

## What I ran

- `UV_OFFLINE=1 sh scripts/check.sh`: green, 805 passed.
- The new tests against efde8b6's source: 6 failed (both temporary-name tests, both mode tests, both lost-report tests), 80 passed; the FIFO test was deselected as before.
- `p9_rollback.py`, `p8c_lost_report_decision_only.py`, `p11_newmode.py` (new), and the two-clone race with real processes (`p4_race.py`, 20 rounds): 0 bad rounds.

## Findings

- N1: answered (`src/lodge/gitstore/checkout.py:170-187`).
  `p9` c: with a link at the old fixed name, publishing gives `STAGED`, the outside file still reads `victim`, and the record is not a link.
  `p9` b: her own file at that name is kept.
- N2: answered (`src/lodge/gitstore/plumbing.py:78-79`).
  `p8c`: one `add` over a lost report now leaves one decision on the remote (`d-yyyyyy`), in three commits in all, where recheck 1 found two decisions.
  A failed push still gives `False` only when the tip is neither the parent nor the commit, so the I1 behaviour and the refusal paths from recheck 1 are unchanged; the 20-round race was clean.
- N3: answered (`checkout.py:182`, `checkout.py:190-197`).
  `p9` d: a `0600` record keeps `0600`.
  `p11`: under umask `027` a new record gets `0640`, the umask is `027` again afterwards, and no temporary is left.
- `p9` a (rollback of her staged and working versions) still holds: her working text is on disk, the index blob is her staged one, and status is `MM`.

## M1 (Minor, new): the umask is read by setting it

Handle: `src/lodge/gitstore/checkout.py:194-197`.
`os.umask(0)` is process-wide, so a file another thread creates between the two calls gets mode `0666` (or a folder `0777`).
Today this does no harm: the command line has a single thread, and the builder says the viewer never writes.
It is a trap for a later threaded writer, for example a viewer served by `ThreadingHTTPServer` that one day writes.
Fix, if wanted: create a new record directly with `os.open(target, O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW, 0o666)` so the kernel applies the umask, and keep `mkstemp` and `fchmod` only to replace existing files; or read `Umask:` from `/proc/self/status` where it exists.
Can be parked for the final wave.

## Files read

Read: the "Fix round 2" section of `task-9-report.md`, and the source diff of `checkout.py` and `plumbing.py`.
Run, not read: the new tests in `test_checkout_safety.py` and `test_push_race.py`, and `tests/gitstore/fakessh.py`.
