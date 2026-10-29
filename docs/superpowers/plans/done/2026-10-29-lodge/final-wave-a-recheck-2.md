# Recheck 2: final wave A, fix round 1 (0ad8f28..fc4b4ce)

Rechecker, scoped to G4, N1, and N2 of the first recheck, against the G4 and N1 rulings in the ledger.
Probes in a detached worktree at fc4b4ce under `.claude/worktrees/`, removed afterwards, and probe repositories in the scratch directory.
`sh scripts/check.sh` at fc4b4ce in that worktree: green, 1041 passed, `lodge check --gate` ok.

## G4, a rewritten `lodge` branch: answered

`src/lodge/gitstore/accepted.py`, `src/lodge/gitstore/branch.py:52-60, 97-98, 112`.
Probe `s1` (an add after a rewrite): the read prints the rewrite line; the agent's `lodge add` now prints `check 5: d-crdg45: statement of a published decision was changed`, `not published: the check failed`, exit 1; `check --gate` still fails afterwards, exit 1.
Acknowledgement: after `git update-ref -d refs/lodge/accepted`, the next read has no rewrite line, the same add publishes (exit 0), and the gate prints `ok`.
Probe `s2` (a plain `git fetch origin` before lodge reads): the rewrite line shows and the gate gives check 5, exit 1.

`refs/lodge/accepted` never moved over a rewrite in the probes:
- Rewrite, then a fresh clone adds on top, before the first clone reads (probe `s3`): the first clone's read still reports the rewrite and the gate fails; the accepted tip is not an ancestor of the new tip, so `accept` leaves it (`accepted.py:22-23`).
- A harmless rewrite (only a commit message reworded, probe `s4`): the gate finds no problem, so the add publishes, and `accept` after lodge's own push leaves the ref where it was; the rewrite line stays on reads until acknowledged.
- A refused add publishes nothing, so `publish`'s `accept` is never reached.
- The ref is shared by the worktrees of one clone (`refs/lodge/` is not a per-worktree namespace) and lives only in that clone, since the default refspec and `git push --all` carry neither.

Fresh clones: set on first use means a clone made after the rewrite accepts it (probe `s2`, a new clone: gate `ok`, her decision shown as `current · author` with the rewritten statement).
A fresh clone of a repository whose rewrite was acknowledged elsewhere behaves normally (probe `s1`, new clone: gate `ok`, one `refs/lodge/accepted` set to the tip).
That is acceptable for 0.1 as a stated limit, not a hole in the fix: lodge can only compare with a tip it has seen, and the author's long-lived clone is the witness that keeps the evidence until she acknowledges it, however many fresh clones add on top (probe `s3`).
It matters because cloud sessions are fresh clones, so the witness is only ever her own clone; see Minor M2.

## N1, a signal exit deferred while git runs: answered for commands, new problem in the viewer

`src/lodge/gitstore/git.py:13-51`; `tests/e2e/test_killed_add.py` now also asserts the push landed and no `index.lock` remains.

**Minor M1. A SIGTERM or SIGHUP that reaches `lodge view` while a request thread runs git leaves the viewer running and answering nothing.**
Handle: `src/lodge/gitstore/git.py:17-26, 47-49` (one process-wide `_running` and `_pending`), `src/lodge/viewer/server.py:6, 21` (`ThreadingHTTPServer`, git runs in request threads, `serve_forever` in the main thread).
Scenario (run): a `git` wrapper on `PATH` sleeping 3 s, one request in flight, then SIGTERM to the viewer: six seconds later the process is still alive, and the in-flight and every later request get no response (curl `000`); the control run (no request in flight) exits on SIGTERM, and a request without a signal gets 200.
The handler runs in the main thread, sees `_running > 0` from a request thread, only sets `_pending`; the main thread never raises, and each later git call in any request thread raises `SystemExit`, which ends that thread without a reply.
Closing the terminal while the browser loads a page is enough; the port stays held until SIGKILL.
Fix: count running git calls per thread (`threading.local`) and defer only when the main thread is the one running git; raise the pending exit only in the main thread, so the viewer's main thread leaves `serve_forever` at once (its request threads are daemon threads).

## N2, the left-over lock line on reads: answered

`src/lodge/gitstore/branch.py:79-87`, `src/lodge/gitstore/lock.py:18-21, 62`; `test_read_serves_the_cache_when_the_lock_is_left_over` now asserts the exact "older than ten minutes and may be left over; delete it if no lodge is running" line.

## The builder's concern: a refused add names no rewrite

Rated Minor (M3), with one reason it is worth fixing in the same round.
Handle: `src/lodge/app/writes.py` (`Added` carries no freshness), `src/lodge/cli/output.py` (add output prints check lines only).
Scenario (probe `s1`): the agent's add prints only `check 5: d-crdg45: statement of a published decision was changed`, about a decision its drafts never touched; the cause is on the read path's freshness line, which also names the command that accepts the rewrite.
An agent blocked on its add and looking for why will find that line, and nothing on the add path says the command is the author's; the guide's one sentence (`guide.md:19`) is the only barrier between a stuck agent and accepting a rewrite of her decision itself.
Fix: when the store's published tree differs from the current one because of a rewrite, `add` prints the rewrite line too, ending "tell the author; only the author accepts a rewrite", and the freshness line on reads gets the same ending.

**Minor M2. `rewritten` fails open when git cannot answer.**
Handle: `src/lodge/gitstore/accepted.py:32-33` (`returncode == 1` is a rewrite; 128, as for a missing object or a broken repository, counts as no rewrite, and `accept` then moves the ref forward).
Scenario (reasoned, not run): `merge-base --is-ancestor` exits 128 when it cannot read the history (a damaged object store, or a shallow repository missing the accepted commit); the rewrite is then accepted silently.
Fix: treat any non-zero exit as "not contained", so a read reports it and the author decides.
Also say in the README that rewrite detection lives in a clone that read the branch before the rewrite, normally the author's own, since every fresh clone accepts the tip it first sees.

## Counts

Open: 0 Blocking, 0 Important, 3 Minor (M1 viewer survives SIGTERM during a git call, M2 `rewritten` fails open and the per-clone limit is undocumented, M3 a refused add names no rewrite and nothing on its path says only the author accepts it).
Answered: G4 (both probes, the acknowledgement, the fast-forward over a rewrite, a harmless rewrite, fresh clones), N1 for commands, N2.
Probe worktree removed.
