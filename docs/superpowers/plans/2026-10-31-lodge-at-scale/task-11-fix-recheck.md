# Recheck t11fix

Method: worktrees /var/tmp/lodge-recheck-t11fix/wt (d723cc8) and /old (ce5f5e1). Gate run with LODGE_INDEX=off so the shared index under the build repo's common git dir is not written (as in the review).

## Check 5 (M1) first, since flagged hard
- Test `test_reference_time_precedes_lstat_and_scan[1e9|2e9]` fails when I move `listed = time_ns()` back after `folder_entries` in folders.py (mutant on d723cc8): 2 failed. On ce5f5e1 sources the test also fails (late.md missing). The ordering fix is real.
- Residual (Minor M-A): margin equals the coarsest granularity. With 2 s timestamps and a kernel that stamps from its coarse clock (lags `time_ns()` by up to one tick, 4 to 10 ms), a row with ctime c0 and a scan reference R in [c0+2s, c0+2s+tick) is trusted (`folders.py:41` `ctime <= listed - 2_000_000_000`), and a change at T >= R stamped floor((T - lag), 2 s) = c0 is missed. Probe: copy of the test with now=12.000 s, change at 12.005 s, stat stuck at 10 s: `tests/gitstore/test_probe_boundary.py` in /var/tmp/lodge-recheck-t11fix/old (removed with the worktree) fails with `late.md` missing from the next read and every later read. Window = one tick at one phase of a 2 s tick, only on a 2 s file system (FAT/exFAT). The review's own alternative (margin strictly above the granularity, 3 s) closes it; the fix took only the first of the two alternatives and the docstring (`folders.py:3-5`) claims "covers rounding through two seconds".

## Check 4 (I1)
- Folder rows keyed `PRIMARY KEY(root,path)` with `folder_roots(root, folder_count)` (`index_schema.py:44-52`), root from `git rev-parse --absolute-git-dir` (`folders.py:83-84`), SCHEMA 7 -> 8 (`index_db.py:23`).
- `test_folder_rows_are_scoped_to_each_checkout` shares one IndexDB object between the two worktrees. My probe (scratch, `tests/gitstore/test_probe_i1.py` in the ce5f5e1-then-d723cc8 scratch worktree) uses two separate `open_index(common)` objects, alternating repo/other/repo/other across them: `scandir calls after warm-up: 0`; rows `[(.../work/.git, 5), (.../work/.git/worktrees/other, 5)]`. I1 closed end to end.
- On ce5f5e1 sources the test fails with "relisted another checkout" (the old-source run in the scratch worktree, see Check 1).
- Note: the SCHEMA bump has no behavioural test (the index file name embeds a digest of all sources plus SCHEMA, `index_db.py:26-43,89`, so any source change already abandons old files); nothing is wrong, the bump is formal.

## Check 7 (gate)
`UV_FROZEN=1`: ruff format --check, ruff check, mypy, vulture, `pytest -q`, then `LODGE_INDEX=off lodge check --gate` (index off only for the last step, so the shared index is not written). Result: `2228 passed, 2 skipped in 217.92s`, `ok`, `note: area storage: order changed` (pre-existing), exit 0. (A first run with LODGE_INDEX=off for the whole gate failed 19 e2e tests that need the index; that was my environment, not the code.) The 2 skips: FUSE-only capability skips (`test_folders.py:268` non-UTF-8 name, `test_index_db.py:186` secure_delete), no STALE-1 skip.

## Check 2 (production rule, leftovers)
- `identity.py:24-28` `candidates` returns `identity.stat_current(...)`; `current()` has no R11-A branch (diff removes it). Probe (test_probe_conv.py in scratch, `disk.read_at` spied, 4 files under lodge/): no conversion source -> 0 files read; `core.autocrlf=input` -> 4 of 4 read. R11-B without a source, CONV-1 with one, as asked.
- `grep -rn "LODGE_TEST_R11\|identity_rules\|awaits the author\|scratch switch" src tests scripts` : no hit (identity_rules.py deleted). `pytest.mark.skip` with STALE-1: none.

## FINDING I-A (Important): per-folder base listing makes every full relist spawn one git process per folder
`folders.py:147` (`before = names(path)`) calls `Committed.folder` (`committed.py:70-91`, one `git ls-tree rev:folder` via `git.attempt`) for each relisted folder. The row key includes the base tree id (`folders.py:41`, `Row.matches` `self.base == base`), so the first read after any commit that changes `lodge/`, the first read in a new worktree (I1 gives it no rows), and every cold index file relists all folders, each with its own process. Brief item M7 asked for "list the base per relisted folder", so this is the asked design, but the full-relist cost was not weighed (the review measured one changed folder).
Measured (my own copies on native disk, `/var/tmp/lodge-recheck-t11fix/cold.py` and `cold2.py`, `identities()` on a new store object, `open_index`, gate idle):
- s9000 copy (228 folders, 16,120 files): first read after a commit 0.785 s with 239 git calls; same read with `Committed.folder` replaced by a lookup in one cached `ls-tree -r` map (the pre-fix approach) 0.270 s with 11 git calls; hit 0.20 s.
- s90000 copy (about 2,250 folders, 160,800 files): first read after a commit **7.634 s, 2,264 git calls**; with the single map 2.069 s, 11 git calls; hit 1.85 s on this machine; cold index 7.566 s against 1.87 s.
Fix: when more than a few folders (say 16) are relisted in one walk, take the base from the per-commit `Committed.listing` (already cached, one `ls-tree -r`), and keep the per-folder call for the few-folders case; or one `cat-file --batch` for all relisted trees. Test: 200 relisted folders, a runner spy, constant process count.

## Check 1 (each item, red on ce5f5e1, green now)
Copied the changed tests onto ce5f5e1 sources (scratch worktree): `test_committed_batch` (I2 batching), `test_disk_descriptor_stack` (M6: 16,654 opens against a bound of 720), `test_folder_fix_round` (I1 "relisted another checkout", I2 [True], M1 both quanta, M5 "clear lost folder rows", M7 "full base map" and DELETE FROM folders, M9 "DID NOT RAISE", healing of an invalid row), `test_index_cap_ruling` (1500 != 1900), plus item 0: `test_production_uses_stat_candidates`, `test_removed_attributes_follow_the_index` x4, `test_seen_identity_takes_no_base_names` all fail on ce5f5e1 (6 failed). Mutants on d723cc8 kill: removing the `absent` skip fails `test_three_hundred_changes_use_constant_git_processes[False]`; removing the 64 bound fails the descriptor test; moving `time_ns()` back fails both M1 cases. [False] of the 300-file test passes on ce5f5e1 because ce5f5e1's production is R11-A (the brief said to run it with R11-B, the mutant covers it).
Test counts verified: `pytest --collect-only` 2254 on ce5f5e1, 2230 on d723cc8 (as the fix report says).
M8 (R11-A gone, nothing to assert), M10 (`disk.open_root`, `Committed` imported from `committed` in listing.py:11, no `disk._` use left), M11 (docstring, plan Step 4 sentence), M3 (plan paragraph states production rule) all present in the diff; M2 covered by the M1 test.

## Check 3 (cap)
`index_space.py:17` = 1_900; `tests/gitstore/test_index_cap_ruling.py` pins the constant, `index_file_cap(160_000) == 304_000_000`, `KEPT_STATES == 4`. Plan line 451 and ledger line 25 rewritten in place (no appended note). Plan invariants line 4 and 6 amended in place.

## Check 6 (commit message)
"retain a bounded stack of descriptors" = M6; "preserve folder rows across state clears" = M5 (review: leave `folders` out of `clear`). Both asked. Not asked but needed: `folder_roots` table / `folder_count` dropped from `meta` (consequence of I1), `_keep` re-reading rows inside the write lock and deleting extra invalid rows (needed for M7's "changed or vanished only" and heals a bad snapshot). Nothing unasked found beyond that.

## Check 8 (public repo)
No personal path, user or machine name, or other project's content in the added lines (grep for home paths, user and project names, machine names, mail: empty). `/var/tmp/lodge-bench/...` paths in the new fix report (lines about M6) match existing practice (4 occurrences in the plan, more in earlier reports at ce5f5e1). No new finding.

## Remaining Minor
- M-A (above): 2 s margin equals 2 s granularity; sub-tick residual window.
- M-B: `folders.py:83` runs `git rev-parse --absolute-git-dir` through `git.run` as an extra sequential process on every indexed read (outside the `run_many` group; about 2 ms); the root could ride in the existing group. The 10-call bound in the 300-path test counts `attempt` only.
- M-C: `Committed.folder` (`committed.py:75-78`) turns any `ls-tree` failure into an empty base (`return {}`), so a transient failure stores a row whose `added` is the whole folder; the output stays exact (overlay compares bytes), but the row and the ident differ until the folder changes. Missing folder and failure share return code 128, so they need distinguishing (for example by `tree_id`-style `cat-file -t` first) or the failure should raise like `listing` does.
- M-D: `index_space.clear` now keeps `folders` and `folder_roots` (`index_space.py:97`); rows of roots that no longer exist (removed worktrees) are never deleted, about 330 kB per root at s90000 (2,253 rows, measured: sum of column lengths 327,908 B), and they stay outside the clear. Needs a pruning rule (for example roots whose git dir is gone) or a statement in the plan.
- M-E: ledger entries in `2026-10-31-lodge-at-scale-progress.md` still state R11-A as current: lines 130, 146, 172 (earlier tasks, "Production retains interim R11-A"), and Task 11's own entry lines 196, 198, 199 (R11-A timings and "both branches") beside line 200 "Production now runs R11-B". Also lines 9 and 20 still say SCALE-1 is open and line 30 names d-4pbeax unqualified (pre-existing). The author's rule is rewrite in place; these lines sit as history next to the new facts. The plan itself (Task 8c step 4, line 530) still says "about 3.1 s with R11-A" as an expectation, harmless.
- M-F: `test_index_db` / SCHEMA bump 7 -> 8 has no test; harmless since the file name embeds a digest of all sources.
