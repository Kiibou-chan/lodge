# Final whole-branch review, lodge at scale (0aa7759..efcd17a)

Reviewer worktree: /var/tmp/lodge-final-review/wt (detached at efcd17a).

## Check 3a: gate (own worktree, efcd17a)

`UV_FROZEN=1` ruff format --check (690 files already formatted), ruff check (All checks passed), mypy (Success: no issues found in 301 source files), vulture (silent), `pytest -q -rs`: **2236 passed, 2 skipped in 216.71s**; `LODGE_INDEX=off lodge check --gate`: `ok`, `note: area storage: order changed`, exit 0.
The last step ran with the index off so the shared index under the main checkout's common git dir is not written (as the t11fix recheck did).
Skips: `tests/core/test_yaml_guard.py:251` (libyaml is present, capability) and `tests/gitstore/test_index_db.py:186` (secure_delete default; examined below).

## Check 1: differential fuzzer (running)

`/var/tmp/lodge-final-review/fz/fuzz.py`: copies `/var/tmp/lodge-bench/s900` (copytree, never written), adds a linked worktree (`side`) sharing the common-dir index, sets `refs/remotes/origin/main`.
Per step 1 to 3 random actions in one worktree: edits, same-size edits with mtime restored, break, delete, revert, new records (also in new subfolders), future-dated records, duplicate codes, rename, move to new folder, mkdir, rmtree, file and folder symlinks, FIFOs, touch, CRLF rewrite, stage, unstage, commit, amend, checkout --, reset --hard, branch switches, trunk moves (origin/main set, moved, deleted), detach, stash and pop, assume-unchanged and skip-worktree with edits or deletes, .gitattributes (root, lodge/, info/attributes) with eol and -text, core.autocrlf in five spellings, .lodge.toml, `lodge ask` and `close`, index clear, corruption, deletion, read-only, 3.2 s sleeps so folder rows age past the margin.
Then 2 to 4 of the five indexed reads (show with several refs and codes, search with words, codes, phrases, filters, waiting, threads, thread) in one or both worktrees, each run 1 to 3 times indexed against one `LODGE_INDEX=off` run on stdout, stderr, exit status; 8 per cent also `check`, `check --gate`, or `spec`; 12 per cent of steps also 4 to 8 parallel indexed readers across both worktrees, 40 per cent of those with a thread clearing the index in a loop.
Smoke run (8 steps, 68 compares): 0 mismatches. Three seeds x 350 steps running.

## Check 4: public repository scan of 0aa7759..efcd17a

Method: `git diff 0aa7759 efcd17a | grep '^+'` (28,500 added lines, JSONL included) searched for home paths, user, machine, and project names, e-mail addresses, CPU and host names; `git grep` at efcd17a against 0aa7759 to separate new from pre-existing.
Pre-existing and accepted (final-review-design.md:105 of the first build): the GitHub identity `Kiibou-chan` and the author's name in the commit command in CLAUDE.md, the agent files, and the plan header.
JSONL (`task12-tools/results-fix.jsonl`, `relist-results.jsonl`): no path or name; scripts take `LODGE_BENCH_ROOT` with default `/var/tmp/lodge-bench` (generic, as the plan names it). E-mail addresses added: only `synthetic@example.invalid` and the no-reply address.

**PUB-1 (Important): three committed review files put the author's user name, home path layout, machine name, and other projects' names in the public repository.**
- `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-5-review.md:116`: an absolute path under the author's home folder.
- `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-9-review.md:7`: an absolute path under the author's home folder.
- `docs/superpowers/plans/2026-10-31-lodge-at-scale/task-1-2-review.md:16`: a scan pattern naming the user, the machine, other projects, and the mail provider.
All three are new in this diff (`git grep` at 0aa7759 finds none of them in these files; the files are added by 0aa7759..efcd17a). CLAUDE.md's hard rule: "no personal paths, machine names ... in code, tests, or docs".
Fix: rewrite the three lines in place (for example "the main checkout's agent file", "the shared common dir of the main checkout", "a pattern of personal paths, user, machine, and project names"); history keeps them unless the branch is rewritten before merge, which is the author's call (the branch is already pushed to the public `origin`).

## Check 1 (continued): fuzzer power

A first version picked show refs at random among about 1,200 records, so an edited record was rarely read; a mutant dropping `git diff-files` from the changed set (`identity.py:107` `results[:2]` to `results[:1]`, in `/var/tmp/lodge-final-review/old`) gave 0 mismatches in 30 steps, although a manual edit-then-show on that mutant prints stale text (md5 3e81... indexed against de44... exact).
Fixed: every burst now also shows the last three touched IDs with `--reasoning --provenance`, and each edit plants a unique token that `search` asks for.
The same mutant then mismatches at step 3 (`show s-1ehv61 d-xathap d-xwj410 --reasoning --provenance`, `fz/mut2.log`). The earlier unpowered runs (3 seeds, about 65 steps each, 1,742 compares, 0 mismatches) are discarded; three new seeds x 300 steps run on efcd17a.

## Check 2: the last fix round (60ecffe..efcd17a)

Red on the code before: worktree `/var/tmp/lodge-final-review/old` at efcd17a with `git checkout 60ecffe -- src scripts/bench_reads.py`, the round's tests run: 9 failed, 21 passed.
Failing on the old code: `test_three_hundred_relisted_folders_bound_spawns[False|True]` (I-A), `test_three_hundred_changes_use_constant_git_processes[False|True]` (M-B, every spawn counted), `test_folder_failure_is_not_an_empty_base` (M-C), `test_reference_time_precedes_lstat_and_scan[2000000000-12000000000-12005000000]` (M-A), `test_clear_prunes_only_removed_checkout_roots` (M-D), `test_one_changed_folder_writes_and_lists_only_it` (new ls-tree spelling), `test_replay_refreshes_once_before_measuring` (F-1 refresh).
Passing on the old code, as expected by their nature: `test_stored_threads_are_required` (P-3 is a guard; the report's two mutants, a tuple default and `default_factory`, are the red evidence) and `test_task12_setup_refreshes_each_copy_once` (it tests the new docs script, which exists in both trees).
Code read: `Committed.folders` (`committed.py:106-111`) takes bases from the cached `ls-tree -r` above 16 folders; its kind mapping (`committed.py:65-75`: 120000 link, blob file, else other, ancestors folder) matches `Committed.folder` (`committed.py:95-103`) for every entry `ls-tree -r` lists; the folder map is evicted with the listing (`committed.py:35`). `ls-tree <rev> -- <folder>/` disables wildcards in ls-tree, so names with glob characters are literal; an absent folder is an empty result with exit 0, a failure raises through `run_bytes` (M-C done as written). `rev-parse --absolute-git-dir` is the eighth `run_many` call (`identity.py:66`, M-B). Margin 3 s (`folders.py:48`), docstring `folders.py:3-6`, plan Task 11 "at least 3 s" (M-A). `clear` prunes roots whose directory is gone (`index_space.py:100-103`) and the plan's Task 11 says so (M-D).
Numbers recomputed from `task12-tools/results-fix.jsonl` (358 rows; best of three per command, mode, and conversion): all 66 replay cells equal the fix report's "after" columns and timings.md (for example `show {code}` seen 0.318994, changed-1 4.763202, `search berth tide --brief` changed-2 15.376479, CONV-1 `waiting` changed-1 6.257886); the ten cycles' best per sighting equal the cycle table (cycle 1: 4.766836, 10.276971, 0.326203), epoch stays 1 in every cycle row (no clear) and states reach 4; `relist-results.jsonl` best of three: before 5.740158 s / 2,267 processes and 5.730874 s, after 0.555728 s / 15 and 0.532518 s / 15, as reported.

**FIX-1 (Minor): P-3 is still a constructor test, not the behavioural test the brief asked for.** `tests/app/test_index_review_facts.py:58-64` builds `StoredState(**values)` without `threads` and expects `TypeError`; brief item 8 asked for "a stored state written without threads is refused, or a read of such a row falls back to memory ... not only a constructor-signature test". It now also catches `default_factory` (the review's point). The read side is protected by arity, not by the constructor: `core/codec.py:158-159` refuses a row whose field count differs from the class's, and builds the object with `object.__new__` (`codec.py:181-182`), so a stored row without `threads` is a miss whatever the default; the constructor test guards writers. The gap is small; record it as accepted or add the read-level test.

## Check 3b: decisions the build relies on

Every `d-` ID in the plan, the ledger, `src`, and README (94 distinct) shown with `LODGE_INDEX=off lodge show`: 63 current, 4 replaced and cited as replaced (d-4pbeax, d-6hb3yd, d-aej8rs, d-f3r5aq), the rest synthetic IDs in code (`d-3m8qk2` in `core/apply.py:261`, `d-xxxxxx`).

**DEC-1 (Important): the cap's clearing rule in code is recorded nowhere; d-a8gkrh, current, says the opposite.**
- Code: `src/lodge/gitstore/index_space.py:110-113` clears when over the cap and `(kept or written >= files)`: a working set inserted since the last clear arms the cap without any kept state.
- Plan Task 10a, `docs/superpowers/plans/2026-10-31-lodge-at-scale.md:631`, states that rule ("the review of 7b, B2, replacing Task 9's condition"), from `plan-fix-6/plan-fix-7b.md:89`.
- d-a8gkrh (`lodge show d-a8gkrh`, current, narrowed only by d-j51qmy on bytes): "The cap is checked before a keep only when a state has been kept since the last clear", title "one state over the cap alone never triggers a clear"; plan Task 9, line 451, still says "a writer that finds the index over the cap, and at least one state kept since the last clear, first clears it".
- Cost: an agent reading lodge (the authority, CLAUDE.md) gets the old rule; the next round touching the cap may "fix" the code back to it, which the 7b review showed lets the index grow without bound (30 MB against a 16 MiB cap).
Fix: a process decision narrowing d-a8gkrh (and d-e3stjn's "past the cap") with B2's rule, and line 451 rewritten in place to match line 631.

**DEC-2 (Minor): two index decisions read as current with text the build does not implement, one of them in front of the author.**
- d-gvz66f is listed by `lodge waiting` under "waiting for the author" and describes `index-<digest>.<generation>.sqlite` files swapped by rename and a cap of twice the bytes per file; the build has one file per build cleared in place (d-e3stjn, `index_db.py:89`, `index_space.py:92-105`). The plan says "its generations replaced by d-e3stjn" (line 73), the record does not.
- d-4n5tr6 (current, narrowed by d-gvz66f) says writes use `synchronous=FULL` with the rollback journal; the code runs WAL with `synchronous=NORMAL` (`index_db.py:62-67`).
- Plan call 25 (`2026-10-31-lodge-at-scale.md:76`) still reads "SECOND-1 (proposed, for the coordinator ...)", though d-n65rhr records it (ledger line 114).
Fix: replace d-gvz66f's generations and d-4n5tr6's FULL through a decision (or retire them), so the author is not asked to confirm them, and drop "proposed" from call 25.

## Check 1 (continued): targeted probes on copies of s900

- Future-dated new decision (valid ID from `lodge id d`, date now + 10 s), `show`, `waiting`, `check` three times before and twice after the date passed: indexed equals exact every time; `check` (exact) changes across the boundary (ce906d98 to e304e23b), the indexed `show` and `waiting` print the same before and after and match exact. `read_model.py:133-147` bounds a stored state by the new decisions' dates; `indexed.py:100-104` checks both ends.
- **STAT-1 (Minor): R11-B serves stale text after a write through a shared memory map that keeps the file's stat; d-jwpwe7 does not name this case.** Reproduced on a copy (`/var/tmp/lodge-final-review/pa`): map a tracked record, write a byte and restore it (mtime set by the fault), `git update-index --refresh`, then write `Z` through the same still-writable page; `os.stat` before and after equal, `git status --porcelain -- lodge` clean, three indexed `lodge show d-01n1rd` print the committed text (`Mooring barge pilot`), `LODGE_INDEX=off` prints `ZMooring barge pilot`. This is the "write through a memory map on native ext4 that kept a file's stat" that d-egknpk's reasoning cites against a private stat cache; R11-B takes git's index stat the same way. It is within d-jwpwe7's "as `git status` does", and the gate and `add` read exactly, so no code change is implied; but d-jwpwe7's statement lists only conversion histories as the stale case. Fix: one sentence in a decision narrowing d-jwpwe7 (stat-preserving writes, such as through a shared memory map, are read stale as `git status` reads them), so the accepted exception is stated whole.
- Linked-worktree base names: in a copy with folders named `g[ab]`, `ga`, `star*`, `q?`, `sp ace`, `:colon`, one with a line break, a nested `deep/a/b`, and a folder link, `Committed.folder(rev, f)` (per folder, `ls-tree <rev> -- f/`) equals `Committed.folders(rev, all)` (above 16, from the cached `ls-tree -r`) for all 37 folders plus two absent ones: 0 mismatches (wildcards are literal in ls-tree; the two kind mappings agree).
- Conversion-removal history (d-jwpwe7's case): `core.autocrlf=true`, index rebuilt and files checked out with CRLF, then the setting removed; `git status` shows the files modified, three rounds of `show --reasoning`, `search tally --brief`, `waiting`, and `check` equal the exact reader (line ends normalised, as the decision says).

## Check 3c: docs and tests

- **DOC-1 (Minor): the README now has two index paragraphs that disagree.** `README.md:75-79` (Reading) says removing the folder "is safe at any time and reclaims all its space"; the new section `README.md:234-239` ("Disposable read index") says to stop lodge commands and the viewer first. Keep one paragraph; removal is safe at any time, the space returns when open connections close.
- **DOC-2 (Minor): plan checkboxes.** Tasks 1 to 10c keep every step `- [ ]` (85 unchecked, for example `2026-10-31-lodge-at-scale.md:128-132`, `:713-717`), Tasks 11 and 12 are `- [x]`; all were built.
- **TEST-1 (Minor): `test_secure_delete_off_and_wal_bounded` never checks the WAL bound on this machine and cannot fail it anywhere.** `tests/gitstore/test_index_db.py:184-186` skips when SQLite's default `secure_delete` is not 1 (it is 0 here: one of the gate's two skips), and the bound it then asserts follows `PRAGMA wal_checkpoint(TRUNCATE)` (`:190-192`), which truncates the WAL to zero bytes whatever `journal_size_limit` is. The pragma values themselves are asserted before the skip, so nothing is lost but the bound; either drop that part or check the WAL size after a `PASSIVE` checkpoint.
- Skips otherwise: capability only (root, libyaml present or absent, FIFOs, file system rejecting non-UTF-8 names, network); no STALE-1 or scratch skip (`grep -rn 'skip' tests`). Vulture clean, `vulture_allow.py` unchanged since 0aa7759; no `TODO`/`FIXME`; the only environment switch in `src` is `LODGE_INDEX` (`main.py:57`), plus git's `GIT_ATTR_NOSYSTEM` (`attributes.py:118`).
- Production source is unchanged since the measured commit: `git diff --stat 2a82ebe efcd17a -- src` is empty.

## Check 5: merge points

- The parent has not moved: `git rev-parse read-speed origin/read-speed` = 0aa7759 = merge base, so the merge is a fast-forward.
- No dependency or gate change: `git diff --stat 0aa7759 efcd17a -- pyproject.toml uv.lock scripts/check.sh` empty; structure rules only tightened (`tests/structure_imports.py:87-91`: `marshal`, `pickle`, `shelve` banned, `sqlite3` only in `gitstore`), no new allowed edge.
- Store format: the record writer (`core/apply.py`) is unchanged; `core/yamlio.py` takes the C loader only for guard-admitted headers and falls back to the Python loader on any C error (`yamlio.py:31-35`); record files changed only through `lodge/` records added on the branch (17 files), and the gate passes on them.
- New on-disk side effect of every read: `<git common dir>/lodge/index-<digest>.sqlite` (with `.lock`, `-wal`, `-shm`), up to about 305 MB at 160,000 files (d-j51qmy); unwritable or broken, reads fall back (d-kj554d). Documented in the README (see DOC-1).
- CLI behaviour changes, each a recorded product decision with a spec edit: `show REF...` with siblings and citers (d-y94v0n), several search queries, codes first, `--phrase`, brief lines without ` · current` and a first line saying so (d-e8pdqe, d-p60ka9, d-kx50jd), `guide --read`. Scripts that parse the old brief lines see a new first line and a missing ` · current`; that is the recorded decision, not a defect.
- `gc.disable()` for every command but `view` (d-s2ypth, `main.py:121-122`).
Nothing found that breaks the parent branch's users outside what the decisions name.

## Check 1: fuzzer interim (efcd17a, powered version)

At step 100 of 300 per seed (seeds 21, 22, 23): 1,222 + 1,135 + 1,195 = 3,552 compares, 0 mismatches. Index state mid-run (run21): epoch 6, 4 kept states, folder rows for both checkout roots (26 and 30 folders), so stored-state hits, clears, and folder hits are exercised. Final counts follow.

## Check 1: fuzzer final (efcd17a)

Three seeds (21, 22, 23) x 300 steps = 900 steps, 1,587 actions, **10,459 indexed reads compared with `LODGE_INDEX=off`, 704 of them in parallel bursts across both worktrees (about 40 per cent with an index clear racing), 0 mismatches** in stdout, stderr, or exit status (`/var/tmp/lodge-final-review/fz/run2{1,2,3}.log`, `.out`).
Actions taken (all seeds): sleep 155, edit 149, revert 84, new_record 70, same_size_keep_mtime 68, crlf 54, ask 50, commit 49, idx_writable 48, attrs 45, delete 43, branch_switch 41, touch 41, symlink_file 39, detach 31, fifo 28, rm_fifo 28, unlink_links 27, stash_pop 26, break 26, move_folder 25, reset_hard 23, stage_all 23, mkdir 22, future_record 22, unstage 22, symlink_folder 21, amend 21, settings 21, idx_clear 20, close 20, idx_corrupt 19, stage 19, rename 19, checkout_discard 19, move_trunk 19, dupcode 19, noflags 18, assume 18, idx_readonly 17, autocrlf 17, rmtree 17, skip 16, idx_delete 15, stash 13. Sixteen index actions failed harmlessly (read-only folder: clear, corrupt, delete refused).
Power: the same fuzzer finds the diff-files mutant at step 3 (12 mismatching steps in 25, `fz/mut2.log`).
Limits: s900 only (25 folders; full relists above 16 folders and partial relists at or below 16 both occur, partial relists above 16 do not; `Committed.folders` equivalence is checked separately above); checkout mode only; no `lodge add` (the dispatch forbids running it; `add` is covered by the suite and by `check --gate` in the fuzzer).

## Summary

Blocking 0, Important 2, Minor 7.
- Important: PUB-1 (personal path, user name, machine name, and other projects' names in three committed review files), DEC-1 (the cap's clearing rule in code is recorded nowhere; d-a8gkrh says the opposite).
- Minor: FIX-1 (P-3 test still constructor-level), DEC-2 (d-gvz66f awaits the author with replaced text; d-4n5tr6 says FULL; plan call 25 "proposed"), STAT-1 (mmap stat-preserving writes read stale under R11-B, unnamed in d-jwpwe7), DOC-1 (two README index paragraphs disagree), DOC-2 (plan checkboxes), TEST-1 (WAL-bound test skipped here and trivially true after TRUNCATE).
Correctness: no mismatch in 10,459 differential reads; the fix round's items done as written except P-3's form; its numbers recompute exactly.
Verdict: ready after fixes (PUB-1 and DEC-1 are text and record fixes; no code change is needed for either).
