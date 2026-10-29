# Task 9 review: the git store

Commit under review: db48cc7 (BASE 8b1580a), read from a scratch copy made with `git archive db48cc7`.
Probes: the reviewer's scratch directory (`h.py` the isolated-git helper, `p1` to `p7` and `worker.py` the probes, `run.sh` the runner).
Every probe ran real git 2.56.0 in a temporary directory under that folder, with `GIT_CONFIG_GLOBAL` an empty file, `GIT_CONFIG_NOSYSTEM=1`, bare remotes on local paths, and no network.

## Verdicts

- Spec compliance: no.
  Gaps: the store writes and reads outside `lodge/` through symlinks in checkout mode (B1), against the spec's Structure ("the only package that touches git or the record files") and the report's claim that both modes refuse writes outside `lodge/`; a push that loses a true race is an error, not `REJECTED`, so Review Focus 1 fails under real concurrency (I1).
- Task quality: not approved (1 Blocking, 2 Important, 7 Minor).

## What I ran

- The whole gate in the scratch copy (ruff format, ruff, mypy, vulture, pytest with the build worktree's environment and `PYTHONPATH` on the scratch `src`): green, 751 passed.
- `tests/gitstore/test_concurrent.py` 40 times and `tests/gitstore` 10 times: 0 failures, so no flakiness in the tests as written.
  They are deterministic interleavings (a wrapper runs A's add between B's read and B's publish), not concurrent processes.
- `p4_race.py` with `worker.py`: real processes started together, each publishing its own file in branch mode and retrying on `REJECTED`.
  Four worktrees of one clone, 10 rounds: all clean (every file on the remote, linear history, no lock left).
  Two clones, 20 rounds: 20 of 20 rounds lost a file to a `LodgeError` (I1).
  Four worktrees plus three clones, 8 rounds: 8 of 8 rounds lost two or three files the same way.
- `p6_checkout_race.py`: four processes racing a checkout publish of one new path, 15 rounds: always exactly one `STAGED`, three `REJECTED`, no lock left.
- `p3_branch.py`: a branch-mode publish with staged, unstaged, and untracked changes left the index bytes, `git status --porcelain=v2`, `HEAD`, and the checked-out branch unchanged, wrote nothing under `lodge/` on disk, and left no temporary index; a publish with the remote gone raised `LodgeError`, left no lock, and did not move the tracking ref; reads then served the cache with `fetch failed; data as of …`; unborn and detached `HEAD` both initialise and publish; the remote's reflog and parents show a linear history (every commit one parent, the root none).
- `p2_checkout_odd.py`, `p5_misc.py`: odd input in both modes; results under the findings.
- Never seen: a force push, a rewritten or lost remote commit, a commit in checkout mode (`rev-list --count HEAD` unchanged after publish), a branch-mode change to her index or working tree, a lock or temporary index left after an error.

## Pass 1: correctness

### B1 (Blocking): checkout mode reads and writes outside `lodge/` through symlinks

Handles: `src/lodge/gitstore/checkout.py:42-46` (writes follow links), `checkout.py:66-76` and `checkout.py:80-87` (reads follow links), `checkout.py:28` (`lodge` itself may be a link), `src/lodge/gitstore/plumbing.py:16-22` (the path guard checks strings only).
Scenario, run in `p1_checkout_symlinks.py`:
- (a) `lodge/decisions/d-aaaaaa-x.md -> <outside>/secret.txt`: `trees()` returns the outside file's text, and `load` quotes it as a problem 1 on the record path.
- (b) `lodge/decisions/d-bbbbbb-y.md -> <outside>/victim.md`: `publish` returns `STAGED` and the outside file now reads `OVERWRITTEN`.
- (c) `lodge/spec/area -> <outside>/`: `publish` of `lodge/spec/area/s-cccccc-z.md` creates `<outside>/s-cccccc-z.md`, then `git add` fails "beyond a symbolic link" and raises `LodgeError`, leaving the file outside.
- (d) `lodge -> <outside>/`: `trees()` lists and reads every file in the outside folder.
A symlink is one commit away in any repository she clones or an agent writes to, git checks it out as a link, and lodge then writes wherever it points.
The ledger's Task 9 ruling adopts "both modes refuse writes outside `lodge/`" as fact; in checkout mode it is false, so the ruling needs this fix before it holds.
Fix: under the lock, before any write, `lstat` every existing component from `root/lodge` down to each target and refuse with a `LodgeError` naming the path when one is a symlink or not a folder or regular file; refuse `lodge` itself as a link in `trees()` and `init_store`.
In `disk_tree`, do not follow links: give a symlink its link text (`os.readlink`) as content, which is what `read_tree` already gives for a symlink blob in branch mode (`p5_misc.py` e: `'/etc/hostname'`), so both modes agree and `load` reports it.
Tests: the four cases above, each asserting the outside folder is unchanged.

### I1 (Important): a push that loses a true race raises `LodgeError` instead of returning `REJECTED`

Handle: `src/lodge/gitstore/plumbing.py:13` and `plumbing.py:54-56`.
When two pushes reach the remote together, the loser's receive-pack fails its ref update and the client prints `!	<commit>:refs/heads/lodge	[remote rejected] (incorrect old value provided)` with `remote: error: cannot lock ref 'refs/heads/lodge': is at X but expected Y`.
`_REJECTED` matches only `[rejected]`, so `push` raises; the store neither marks itself stale nor returns `REJECTED`, and `add` never retries.
Reproduced with plain git (two `git push --porcelain` in parallel, first iteration), and through the store in `p4_race.py` (two clones: 20 of 20 rounds), and deterministically in `p7_lockrace_hook.py`: a `pre-receive` hook on the bare remote runs `env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES git update-ref refs/heads/lodge <other>`, and `publish` raises `cannot lock ref`.
No commit is lost (the remote keeps the winner), but Review Focus 1 ("the later push is rejected, lodge re-applies its drafts on the new tip") fails exactly when two sessions add at once, and the spec's Storage says "retrying on a rejected push".
Fix: on any failed push, ask the remote where the branch is (`ls-remote <remote> refs/heads/<branch>`, compared exactly); when it is not at the commit's parent, mark the store stale and return `REJECTED`; otherwise raise as now.
This does not depend on the wording of a server's message, which differs between hosts.
Test: the `p7` hook as a store-level test asserting `REJECTED`, and an `add` over it asserting `PUBLISHED` on the retry.

### I2 (Important): a failed write in checkout mode is a raw `OSError` and leaves part of the change on disk

Handle: `src/lodge/gitstore/checkout.py:42-46`; also `src/lodge/gitstore/branch.py:98` (the stamp write).
Scenario, `p2_checkout_odd.py`:
- (a) `lodge/spec/gone` a dangling symlink, publish of `lodge/spec/gone/s-aaaaaa-x.md`: `FileExistsError` from `mkdir(exist_ok=True)`, not a `LodgeError`.
- (b) two writes, the second into a read-only folder: `PermissionError`, not a `LodgeError`; the first file stays written and unstaged, so the next read shows a half-applied change as the current state (must-not 1).
Fix: check every target (B1's walk) before writing anything; write each file to a temporary sibling and `os.replace` it, removing the written ones if a later write fails; turn any `OSError` into a `LodgeError` naming the path.
Same for the stamp: an `OSError` there becomes a `LodgeError`, or is ignored with the fetch still counted.
Tests: (a) and (b) above, asserting `LodgeError` and no new file left.

### M1 (Minor): the fetch stamp is shared by every remote and branch of a clone

Handle: `src/lodge/gitstore/branch.py:34`, `branch.py:79-91`, `branch.py:104-108`.
Scenario, `p5_misc.py` a: after a fetch of `origin/lodge`, a store with `remote = "nope"` or `branch = "records"` within `max_staleness_seconds` skips the fetch, finds no ref, and says "lodge has no data in this repository yet; run `lodge init`"; once the stamp ages, the same store says "cannot fetch nope/lodge: fatal: 'nope' does not appear to be a git repository".
Review Focus 5 asks for the sentence that says which; the first one sends her to `lodge init`, which then refuses.
Reached when worktrees of one clone carry different `.lodge.toml`, or within a minute of editing it.
Fix: write the tracking ref beside the time in the stamp and treat a stamp for another ref as never fetched; or fetch once before raising `NotInitialised` when this process has not fetched.

### M2 (Minor): `lodge init` in branch mode refuses when any branch ends in `/lodge`

Handle: `src/lodge/gitstore/branch.py:115-117`.
`git ls-remote --heads <remote> lodge` matches patterns from the end of the ref, so `refs/heads/feature/lodge` counts.
`p3_branch.py` e: with only `main` and `feature/lodge` on the remote, init says "lodge is already initialised: origin has a branch lodge".
Fix: `ls-remote <remote> refs/heads/<branch>` and compare the printed ref exactly.

### M3 (Minor): a FIFO under `lodge/` hangs every checkout read

Handle: `src/lodge/gitstore/checkout.py:74`.
`p2_checkout_odd.py` e: `mkfifo lodge/decisions/fifo`, then `trees()` was still blocked after 5 s.
Fix: read only regular files (`lstat`, `S_ISREG`); any other kind becomes `""`, so `load` reports it; this falls out of B1's fix.

### M4 (Minor): a gitlink under `lodge/` vanishes from the branch tree without a problem

Handle: `src/lodge/gitstore/trees.py:32`.
`p5_misc.py` e: a submodule entry at `lodge/spec/sub` on the branch is neither in `files` nor reported, though the brief says trees list every file so `load` reports strays.
Fix: give a non-blob entry under `lodge/` an empty text so `load` reports it as stray.

### M5 (Minor): `lodge` as a file gives a misleading init refusal

Handle: `src/lodge/gitstore/setup.py:47-48`.
`p2_checkout_odd.py` d: reads say "run `lodge init`", and init then says "lodge is already initialised: lodge/ exists".
Fix: refuse with "lodge is a file, not a folder" when it exists and is not a folder.

## Pass 2: practice

### M6 (Minor): the two `.gitkeep` paths are defined twice

Handle: `src/lodge/gitstore/branch.py:16` (`KEPT`, a dict) and `src/lodge/gitstore/setup.py:15` (`_KEPT`, a tuple).
Scenario: a third folder added to one and not the other gives the two modes different empty stores.
Fix: one constant in `trees.py` beside `DATA`, used by both.

Otherwise the practice pass is clean: every module is under 125 lines, docstrings state facts, `git.py` keeps every subprocess call in one place with `-C`, no terminal prompt, and a fixed locale, errors carry git's first line, and the tests read as behaviour, not as builder scaffolding.
The `tests/gitstore/__init__.py` and `sys.path` arrangement in `tests/gitstore/conftest.py` follows the pattern already in `tests/app/conftest.py`; I agree with report concerns 1 and 2.

## Pass 3: design

### M7 (Minor): the ruling's "attachments are never overwritten" holds in checkout mode only

Handle: `src/lodge/gitstore/branch.py:65-77` has no per-path check, so a branch-mode publish at `base.rev` overwrites any path, attachments included (read from the code, not run).
No cost today: `app` writes only record and area files (`src/lodge/app/writes.py:83`).
Fix: word the ledger ruling as "in checkout mode", or have both modes refuse a write to an existing attachment path.

Boundaries hold: `gitstore` imports only `app` and `core` through their front doors, the structure test passes, and the front door exports exactly the brief's names.
The ruling's other points stand: `raw` as the whole table, the in-process stale mark (an unfetched tracking ref only costs one rejected push and a fetch, confirmed in `test_branch_rejected_push_marks_stale` and `p4` worktree rounds), and her pre-push hooks running (`p5_misc.py` d: a refusing hook surfaces as `LodgeError: refused by hook`).
The concurrency tests in `tests/gitstore/test_concurrent.py` cannot catch I1, since no two pushes ever overlap in them; the `p7` hook test is the deterministic way to cover it.

## Checked and clean

- Settings: absent file, malformed TOML, non-UTF-8 bytes, `.lodge.toml` a folder, `store = 5`, unknown section, `mode = 1`, `branch = "-delete"` all give one-sentence `LodgeError`s (`p5_misc.py` b).
- Odd branch names bypassing the settings check (`a//b`, `x.lock`, `lodge/`, `a b`) give `LodgeError` or `NotInitialised`, never a crash (`p3_branch.py` d).
- A stale lock (mtime 700 s ago) is reported with its path and left in place (`p5_misc.py` c).
- Non-UTF-8 content and a non-UTF-8 file name, in both modes, become problem 1 naming the path (`p5_misc.py` e and f).
- `lodge/decisions` as a file: listed as a stray, and a publish into it is a `LodgeError` (`p2_checkout_odd.py` c).
- Brief's named tests: all present; `test_not_initialised` is split into `test_not_initialised_checkout` and `test_not_initialised_branch`.

## Not verified

- SSH remotes: git runs with `GIT_TERMINAL_PROMPT=0`, which does not stop `ssh` asking for a passphrase or host key on the terminal; I had no SSH remote to test, so whether a hook run can hang there is open.
- Hosted remotes (GitHub): I1's message comes from local receive-pack; the suggested fix does not rely on it.

## Files read

Read: `.claude/agents/reviewer.md`; `CLAUDE.md`; the brief and report for Task 9; the ledger (whole, at db48cc7 and the Task 9 lines at f8d5add); the spec's Must nots, Constraints, Storage, Structure, and Left to the builder; the plan's Global Constraints, Process, Calls made, and Review Focus; every file in `src/lodge/gitstore/`; `tests/gitstore/conftest.py`, `repos.py`, `test_branch.py`, `test_concurrent.py`, `test_checkout.py` lines 130 to 186, the test names in `test_setup.py` and `test_checkout.py`, `test_setup.py` lines 110 to 135; `tests/app/fakes.py` lines 1 to 60; `tests/app/conftest.py` head; `src/lodge/app/ports.py` (Store, Clock); `src/lodge/core/snapshot.py` lines 30 to 80; `src/lodge/core/fileformat.py` lines 80 to 110.
Not read: the review package diff as a whole (I read the files it adds instead); `test_setup.py` and `test_checkout.py` in full; the rest of `core` and `app`.
