# Review of f10bd8c (Task 10b fix round) and b50be4b (Task 11)

Status: complete.
Method: committed code read in a detached worktree at b50be4b (`/var/tmp/lodge-review-t11/wt`); every probe ran there or on copies (`c900`, `c9000`, and per-run copies under `/var/tmp/lodge-review-t11/runs`) of `/var/tmp/lodge-bench/s900` and `s9000`, with their `.git/lodge` deleted first and the git index refreshed.
Git config was isolated for every R11-B run (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`, an empty `HOME`).
The shared index under the build repository's `.git/lodge` was never written; the one `lodge check --gate` I ran used `LODGE_INDEX=off`.
The builder's tree was only read.

## Verdict

Blocking 0, Important 2, Minor 11.
Production R11-A and the dormant R11-B branch equalled the exact tree in every fuzz run (about 3,000 compared steps in 42 runs, list at the end); the cache's key and its fault handling are sound for fine-grained and 1 s timestamps.
The two Important findings are costs, not wrong output: folder rows are not scoped to a checkout, so two worktrees of one repository defeat the cache and rewrite it on every read (I1), and R11-B spawns two git processes per untracked file on a seen read (I2).
The 10b fix round closes I1, I2, M1, M2, M3, and M5 as claimed; M4 and M6 stay open by the dispatch.

Why skips rose from 6 to 39: 33 new skips, every one with the reason "awaits the author's STALE-1": 30 in `test_folders.py` (the `b` parameter of each test, plus the always-skipped `test_index_race_after_overlay_keeps_exact_fallback`), 2 in `test_folder_recovery.py`, 1 in `test_folder_property.py` (`pytest -rs` over the three files: 31 passed, 33 skipped).
The coordinator ruling in `task-11-report.md` (Task 11 coordinator ruling and scope) asks for exactly this: R11-B cases beside the active ones, skipped until STALE-1, run through a scratch switch; Task 8c's six skips are the precedent.
None is a platform or flakiness skip on native disk; the FUSE-only capability skips (non-UTF-8 name, directory permission bits) occur only in the builder's FUSE run and are not among the 39.
Full gate re-run by me on the commit: ruff format, ruff, mypy (293 files), vulture, pytest 2,189 passed and 39 skipped in 212 s; `lodge check --gate` with `LODGE_INDEX=off` prints `ok` and the existing storage note.

## Important

### I1 Important: folder rows are not scoped to a checkout, so two worktrees of one repository defeat the cache and rewrite it on every read
`src/lodge/gitstore/index_schema.py:44` (`folders(path TEXT PRIMARY KEY, ...)`), `src/lodge/gitstore/folders.py:107` (`_rows` loads every row), `:165-166` and `:172-192` (`_keep` deletes and rewrites the whole table), `src/lodge/gitstore/setup.py:41` (every checkout store gets `Folders(index.db)`; the index lives under the *common* git directory, which linked worktrees share).
Failure scenario: `git worktree add` a second checkout of the repository (how this project builds: builder and reviewer worktrees) and read in both alternately.
Each checkout's folders have other inodes, so its rows never match the other's; each read lists every folder and replaces the whole table inside a `BEGIN IMMEDIATE` write.
Probe (`scratch/worktrees.py`: copy of `s900`, a second worktree, rows mature): `os.scandir` calls per read were 25 of 25 folders for each of `main, w2, main, w2, main, w2`, so no read ever hit; with one checkout the same reads list nothing.
Output stays exact (inode, times, and base must all match, and two directories on one file system never share an inode); the cost is that the cache is worse than none: every read pays a listing and a delete and insert of all rows (about 0.15 s at 20,000 folders, M7), and I expect two worktrees' writers to contend for the write lock (not measured; a failed `_keep` is swallowed).
Fix: key the rows by checkout, for example a `root` column holding the checkout's real path (or a hash of `git rev-parse --absolute-git-dir`, which differs per linked worktree) in the primary key, with `folder_count` kept per root; test: two worktrees, alternate reads, `os.scandir` patched to fail on the second round.
The plan's table (`folders(path, ino, ...)`) has the same gap, so this is a plan assumption the code inherited.

### I2 Important (R11-B only): a seen read spawns two git processes per untracked file
`src/lodge/gitstore/committed.py:70-91` (`selected`: `git rev-parse --verify rev:path` at `:80`, then `git cat-file -t` at `:84`, once per changed path), reached from `src/lodge/gitstore/identity.py:120`, where `changed` holds every name in the rows' `added` (`:91`).
Failure scenario: an agent writes a batch of new records and has not committed them; under R11-B every read until the commit looks each untracked path up in the base with its own process, though the base cannot hold a name that a folder delta lists as added but not as removed.
Probe (`scratch/untracked.py`: `s900` copy, git index refreshed, switch flipped in scratch): 0 untracked files, seen read 0.018 s with 8 `rev-parse` calls; 300 untracked files, seen read 0.60 to 0.61 s with 308 `rev-parse` calls, about 2 ms a file; 1,000 files would be about 2 s (extrapolated, not run) against the 0.3 s target.
`test_seen_identity_takes_no_base_names` passes because it counts `ls-tree` only.
The report names the cost ("a large untracked overlay may still add process overhead", Concerns), but the ledger's STALE-1 note does not, and it decides whether R11-B meets its own number with uncommitted work.
Fix: skip the lookup for a path in `added` whose name is not in the same folder's `removed` (the base lacks it by construction), and send the remaining lookups through one `git cat-file --batch-check` with `rev:path` lines on stdin; test: 300 untracked files, a runner patched to count processes, a constant number allowed.

## Minor

### M1 Minor: the racy margin equals the coarsest timestamp, and the reference time is taken after the listing
`src/lodge/gitstore/folders.py:38` (`self.ctime_ns <= self.listed_at_ns - 2_000_000_000`) with `listed = time_ns()` at `:133`, after the `lstat` (`:120`) and the scan (`:132`).
On a file system whose directory times have 2 s resolution, a change that lands after the `lstat` inside the same 2 s bucket as the folder's previous change gets the same ctime and mtime, and the row is trusted because the listing ended two seconds after the bucket began.
The window is the listing's duration (milliseconds for a folder of hundreds of names) at one phase of the 2 s tick, and only on such a file system (FAT is the usual case); on a 1 s file system it needs a listing slower than 1 s.
Probe (`scratch/racy.py`: a patched `folder_stat` rounding times to the granularity, a controlled clock, a file created inside the scan): with 2 s granularity the next read and every later read lacks the new file (`MISSED late.md`); with 1 s and 4 ms granularity the later read is exact.
The fuzz with the same rounding kills the mutant that drops the margin (mismatch at step 1) and passes the real code, so the simulation is sound; the real code fails only in that one phase.
Fix: take the reference time before the `lstat` and store it as `listed_at_ns`, or use a margin strictly above the coarsest granularity (3 s); add a test with a rounding `folder_stat`.

### M2 Minor: the `time_ns` patch in the fixtures hides the margin from the FUSE run and the property oracle
`tests/gitstore/test_folders.py:37` and `tests/gitstore/test_folder_property.py:28` shift `folders.time_ns` three seconds ahead for every test except `test_change_in_the_same_second_as_the_listing` (`test_folders.py:140`), which rewrites `listed_at_ns` by SQL.
The builder's FUSE run therefore shows the signature (inode, mtime, ctime) behaves on that mount (my own fuzz on the same mount: both branches exact over 60 steps), and says nothing about the margin on coarse timestamps.
Fix: one test with a `folder_stat` that rounds to 1 s and 2 s and a clock the test controls (`scratch/racy.py` is a sketch).

### M3 Minor: FOLD-1 (d-eg5nra) and the Task 11 text promise what only R11-B does
`lodge show d-eg5nra` says "a read whose folders are unchanged takes none of the base's names"; production R11-A takes all of them on every read (`identity.py:43` calls `committed.listing(rev)` before the walk; the report's table gives R11-A identity 1.74 s).
The ruling limits the requirement to R11-B, but the record and the plan's "No base names on a hit" paragraph are unqualified; only the ledger line says "R11-B takes no base names or full mapping on a hit".
Fix: a follow-up record narrowing d-eg5nra to the rule it binds (`lodge add`, a handle per argument), or a sentence in its reasoning.

### M4 Minor: the R11-B cases cannot be run from the repository
The skip markers are removed by `/var/tmp/lodge-bench/task11-r11b-tests.py`, outside the repository; the 33 skipped tests, `Folders` under `stat_current`, and the lazy listing (`identity.py:109-123`, `:158-176`) are code that no CI run executes (the 10b review's M6 smell).
`tests/gitstore/test_folders.py:66-69` also pins production R11-A to taking base names (`pytest.raises(AssertionError, match="base names")`), a seventh R11-A-only assertion beside the six the ledger lists for STALE-1.
Fix: an environment switch in `tests/gitstore/identity_rules.py` (for example `LODGE_TEST_R11=b` unskips the `b` parameters and flips the one function), and the new case added to the ledger's STALE-1 list.

### M5 Minor: the cap's clear empties the folder rows but not their count
`src/lodge/gitstore/index_space.py:92-101` deletes every table but `meta`, `folders` included, and leaves `meta.folder_count`; the next `_rows` sees `len(raw) != count` and returns `{}` (`folders.py:68-69`), so output is right, but every over-cap clear (the report counts them at `s90000`) costs the next read a full listing and rewrite of rows that are tiny and independent of the cap.
Fix: leave `folders` out of `clear`, or reset `folder_count` in it; test: a clear, then a hit read lists nothing.

### M6 Minor: a deep chain costs the same on a hit as on a listing, and the reopen is quadratic
`src/lodge/gitstore/disk.py:33-63` (`parent`) reopens every ancestor on each switch of parent; the hit loop (`folders.py:118-129`) switches parent for every folder of a chain.
Probe (`scratch/many.py ... deep 1500`): 3.0 s per read for cold, relist, and hit alike in both branches, so the cache gives a deep tree nothing; output stays exact.
Inherited from Task 8c (the 10b review measured 600,000 opens at 1,100 levels); named here because Task 11 is where a hit should have become cheap.
Fix: keep a bounded stack of open descriptors for the current path, or record the depth limit in the report.

### M7 Minor: one listed folder rewrites every row, and the base's full folder map is built on every read that lists
`folders.py:165-166` calls `_keep` with the whole snapshot when any folder was listed; `:142-143` builds `_base_folders(names())`, which needs the full `ls-tree` of the base.
Measured: 20,000 folders, one changed folder, 0.83 s against 0.68 s for a pure hit, and for 2 s after a change every read repeats it because the changed folder is racy.
At `s90000` (2,253 folders, 160,800 names) the base listing is 0.375 s and `_base_folders` 0.13 s (timed with `Committed` on the benchmark store, read only), added to every read in the racy window and every changed read, in R11-B as well.
Fix: write only the rows that changed or vanished in one transaction (the plan says "replacing earlier rows in place"); for R11-B list the base per relisted folder (`git ls-tree <rev>:<folder>`) instead of the whole tree.

### M8 Minor: the 10b property oracle no longer asserts blob equality under R11-A
`tests/gitstore/test_identity_property.py:14-26` (`parsed_agrees`) compares texts with line ends normalised and parsed values; `test_folder_property.py` reuses it, so a production R11-A regression that changes only a CRLF file's blob (and so the ident) passes the 200-history oracle.
The 10b review's M1 asked for this weakening for the R11-B history; the fix applied it to both rules.
Fix: assert `dict(listing.blobs) == dict(exact.blobs)` when the rule is R11-A (`identity_rules` is already imported by the folder test).

### M9 Minor: a lazy listing is a valid-looking object with no blobs
`identity.py:158-163` returns `Listing(base.rev, ident, {}, frozenset())` in the lazy case, and `materialise` (`:172-176`) returns it unchanged when `_pending` is `None`; `current()` sets `_pending = None` first (`:36`), so a `current()` that raises leaves `CheckoutListing._states` holding the empty listing, and a later `listings()` answers with no records instead of failing.
Not reachable today (a failing `identities()` propagates); reachable once R11-B is switched on and a caller catches the error.
Fix: have `materialise` raise when `_pending` is `None` and the listing is the lazy one (mark it), or make the lazy object a distinct type.

### M10 Minor: a private name and a re-export
`folders.py:110` uses `disk._FOLDER`; `identity.py:9-10` imports `Committed as Committed` only so that `listing.py` can keep importing it from `identity`.
Fix: `disk.open_root(root)`; import `Committed` from `committed` in `listing.py`.

### M11 Minor: file-system assumptions are unstated
The key (inode, mtime_ns, ctime_ns, base) assumes that renames and directory changes update the directory's mtime and ctime, a local wall clock comparable with the file system's (a network mount whose server runs ahead or behind breaks the 2 s test in either direction), and no attribute caching (NFS `acdirmax`); `st_dev` is not in the key.
The fuzz found none of these failing on ext4 or on the FUSE mount, so this is documentation: one paragraph in the module docstring of `folders.py` or in the report, and the plan's FUSE sentence could name NFS and SMB.

## Task 10b fix round (f10bd8c) against `task-10b-review.md`

- I1 (a query-level fallback kept the stored state): closed. `QueryFallback` (`index_lookups.py:17`) is raised for `needs_memory` and for `candidates` returning `None` (`indexed.py:206-213`); `_run` answers in memory, returns `_nothing`, and neither marks nor keeps (`:107-117`). `show A`, `show THE`, `show d-zzzzzz`, `show no-one`, `search THE`, and `search A` kept the state 0 times in four reads each (`scratch/showfault.py`); the six-search tests with a one-byte cap pass.
  A fault in the stored data still raises `Miss` and heals by a re-keep: `rows()` returns `None` on a missing or malformed bucket (`index_states.py:102-118`), and all 256 buckets exist for every state (`:53-57`), so an empty bucket is not mistaken for a fault.
- I2 (a historical parse poisoned searches): closed. The check is now `{*members, *citing} <= rows.keys()` (`indexed.py:239-243`); a parse whose ID has no row, or whose key differs from the row's, is ignored (`:248-253`); `test_deleted_record_does_not_send_search_to_memory` and the real-file e2e test pass with zero keeps over six reads.
- M1: closed, with the cost in M8 above. M2: closed (`empty_candidates`, `index_lookups.py:45-68`; for an empty query `rank` reads only kind, status, decided_by, date, scope, area, and the areas, `core/ranking.py:45-48, 82-90`). M3: closed (an exact ID with no row yields no candidate; memory's exact-ID step finds nothing either). M5: closed (the 300-query differential also runs against `IndexDB` with `café`, `港口`, `Straße`, and `42`, and asserts zero keeps). M4 and M6: unchanged by the dispatch and still disclosed.
- Differential on the fixed code (`/var/tmp/lodge-review-t10b/scratch/run2.py`, 60 edit steps on a copy of `s900`, seeds 21 and 22; indexed output, stderr, and exit status against `LODGE_INDEX=off`): 335 and 328 compared queries, 0 mismatches, 227 and 226 answered from stored rows, 108 and 102 in memory (function words, unknown IDs, and filters that need memory by design; the 10b review's run with seed 21 sent 132 of 336 to memory).

## Task 11 against the plan, step by step

- Key and trust rule (`folders.py:33-39`): inode, mtime, ctime, base tree ID, and the 2 s margin, as the plan states; `lstat` before the scan, listing time after (the correctness review's M7 order); a link or file is recorded by name in the parent's delta and its descendants' rows are dropped (`:124-126`, `:165-166`); one `BEGIN IMMEDIATE` replaces the snapshot (`:172-194`) and a failed or read-only write is swallowed; an unlistable folder keeps the earlier snapshot (`:165`).
- A row keyed by one base never applies to another: `base` is part of `matches`, and every folder of a walk is either a hit on the current base or relisted and rewritten with it. The mutant that drops the base test is caught by the fuzz (`softreset`, then reads; mismatch at step 6, both granularities).
- Each of inode and ctime, the base, and the margin was mutation-tested against the fuzz; only the margin needs the rounding simulation to be seen, which is what M1 and M2 ask the tests to include.
- Fault recovery: damaged rows (non-string path, bad kind, traversal name, deep JSON, undecodable, missing parent, missing `meta` row, wrong count) all return `{}` (`_rows`, `:64-87`) and the walk lists everything; a closed or read-only connection falls back to `disk.walk`; the interrupted-write test stops after each statement; a stale count after a clear is a miss (M5). Three processes reading one store for 40 s while a fourth fuzzed it: 1,833 reads, 0 exceptions, and the fuzz 0 mismatches.
- The plan's FUSE sentence: run by the builder on `/home` (fuseblk) with the capability skips named; my fuzz there is exact in both branches.
- The plan's R11-B figure (about 0.1 s isolated): the builder's isolated identity is 0.158 s without a conversion source, above the plan's estimate; the report states it and defers to Task 12.

## Practice and design notes (no finding)

- `folders.py` is 194 lines; `identity.py` shrinks through the `committed.py` extraction; comments state facts.
- `Folders.walk` is one 65-line function with a nested if/else; "hit" and "list" helpers would read better.
- `create=True` in the tests' `patch.object(folders, "time_ns", ...)` is unneeded (the name exists).
- The incomplete construction skeleton ("Process deviation" in the report) is disclosed; no code consequence.
- The e2e change (`test_indexed_reads.py`) primes mature rows before the no-write assertion; the assertion is unchanged. For Task 12: a `seen` timing must wait 2 s after the last edit, or the read lists and writes.

## Probes run (a mismatch is any difference from the exact tree in listing blobs, attachments, texts, or idents)

- `scratch/fuzz.py`: create, delete, rename, touch, modify, mkdir, rmdir, nested and deep new trees, attachment add and delete, `rm -r`, folder moves, folder replaced by a file or a link, mtime set back, commit, and `reset --soft`; 1 to 4 operations per step, 30% of steps sleep up to 2.1 s, a new store object per read, half of the steps read twice; timestamps native or rounded to 1 s and 2 s by a patched `folder_stat`.
  - Under the user's global `core.autocrlf=input` (every path converts, so R11-B ran its all-paths route): 12 runs of 60 steps on `s900`, 4 runs of 40 steps on `s9000`, 4 runs of 150 steps on `s900`; 0 mismatches.
  - Config isolated, index refreshed (the real R11-B route): `s900`, seeds 41 to 43, 100 steps, both granularities, both branches (12 runs); `s9000`, 40 to 50 steps, both branches (6 runs); seed 7, 80 steps, both branches; 0 mismatches.
  - FUSE mount (`/home`, fuseblk), both branches, 60 steps: 0 mismatches.
  - Mutants of `folders.py` (`scratch/mut-*`): ignoring ctime caught at step 27 (native) and 13 (2 s rounding); ignoring the base caught at step 6; dropping the margin caught at step 1 with 2 s rounding and not on native timestamps, as expected.
- `scratch/direct.py`: `rmtree`, folder to file, folder to link, folder moved; both branches exact on the read and the read after.
- `scratch/links.py`: folder replaced by a link, link retargeted, atomic retarget by `rename`, link back to a real folder, link to a sibling inside the repository; both branches exact on every read and its hit (`lodge` itself as a link is refused by the store, as designed).
- `scratch/many.py`: 20,000 folders (cold 0.85 s, hit 0.68 s, one change 0.83 s) and a 1,500-level chain (3.0 s per read), both branches exact (M6, M7).
- `scratch/stress.py`: three readers for 40 s while the fuzz mutated the store: 0 errors.
- R11-B suites (builder's scratch switch): `test_folders.py`, `test_folder_recovery.py`, `test_folder_property.py`: 32 passed; the property test five more times: 5 of 5 passed in about 18 s each.
- Full gate on the commit, without the shared index: 2,189 passed, 39 skipped.

## Files read

Plan (Global Constraints, Task 10b and 11 text, Task 12 stop), `task-11-report.md`, `task-10b-review.md`, ledger diffs of both commits, reviewer rules, `CLAUDE.md`, d-eg5nra and d-8kq2nk (`lodge show`, index off); all of `git show f10bd8c` and `b50be4b` under `src/` and `tests/`, with `folders.py`, `disk.py`, `identity.py`, `committed.py`, `listing.py`, `setup.py`, `checkout.py`, `index_schema.py`, `index_space.py`, `index_states.py` (`rows`, `all_rows`, `buckets`), `index_transactions.py`, `indexed.py`, `index_lookups.py`, `core/ranking.py`, `core/views.py` read in full or in the parts the diffs touch; tests `test_folders.py`, `test_folder_property.py`, `test_folder_recovery.py`, `test_indexed_search_review.py`, `test_search_deleted_file.py`, `test_identity_property.py`, `identity_rules.py`, the `test_indexed_reads.py` and `test_indexed_search.py` diffs.

## Files not read

`attributes.py` and `flags.py` beyond their use in `stat_current`; `tests/gitstore/test_identity*.py` other than the helpers; the viewer; the builder's replay and phase scripts under `/var/tmp/lodge-bench/task11`, so the 96 `s90000` timing samples and the 78 kept-state checks are the builder's numbers, not mine; branch mode; `s90000` (only its `ls-tree` was timed, read only).
