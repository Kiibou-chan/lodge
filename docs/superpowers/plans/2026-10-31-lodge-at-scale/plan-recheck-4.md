# Plan recheck 4: lodge at scale, fix round 4

Status: complete.
Scope: `git diff f5da619 2dffc85`, its mapping in `plan-fix-4.md`, and R1 to R5 in `plan-recheck-3.md`, under the coordinator's ruling d-e3stjn and the planner's call d-c6cegr, both read with `lodge show <id> --reasoning`.
Plan line numbers refer to `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` at `2dffc85`, which `5a7dbc4` leaves unchanged (it adds only the record of SCALE-1, d-4pbeax).
The index modules do not exist yet, so this reviews the proposed design; the probes model it on scratch databases.
Probes and their output are under `/var/tmp/lodge-recheck4/`; no network, no `lodge add`, and no change to the worktree but this file.

## Status of R1 to R5

| Finding | Status | Plan lines | Assessment |
|---|---|---|---|
| R1, two rebuilders share a temporary database | Fixed | 31, 434, 439 | No temporary file, link, or rename remains (`grep -n -i 'generation\|os\.link\|\.tmp'` finds only the d-gvz66f citation at line 70); the clear is one `BEGIN IMMEDIATE` transaction, and a WAL reader keeps its snapshot across it (probe below). |
| R2, ten minutes untouched does not prove no reader | Fixed | 435, 442, 451 | Deletion of another build's file needs `LOCK_EX \| LOCK_NB` on a lock file every reader holds shared; the probe confirms the exclusion on ext4 and on the FUSE NTFS mount; W5 and W7 are gaps at the edges. |
| R3, a changed and restored attributes file | Fixed | 391 and 398 | The whole conversion key is compared before and after, and the change-and-restore test is named; a change and a restore that both fall inside one git call remain invisible to any before-and-after key, a window of the call's own length, which this recheck accepts. |
| R4, a rebuild inside the changed-read stop | Fixed | 80, 458, 532, 611 | The clearing read is reported with the cold reads and one clear is timed; how often a clear happens is not measured (W6), and the clear's own time depends on the SQLite build (W4). |
| R5, cached published facts not carried into a rebuild | Fixed in the contract | 506 to 512, 521, 527 | `keep_state` takes every unit and fact used, hits included, and writes them all when the epoch moved; this is only as sound as the epoch the build passes, which no interface supplies (W1). |

## New findings

### W1. Important: no interface yields the epoch, and the build's lookups may see several

Handle: plan lines 31, 429, 503, 506 to 512, and 521; the `Index` protocol has `parses` and `facts` returning values only, and no `epoch()`.
`keep_state` takes `epoch: int`, "the one the build's lookups saw", but a build's lookups run in separate read transactions (Task 9's `parses`, Task 10c's `facts`, each one operation in one transaction, line 444), so they can see different epochs, and nothing says which one to pass or how to read it.
Failure scenario: a build takes its parse hits at epoch 1, another process clears (epoch 2), and the build then reads the epoch in a later transaction (for example with its `facts` lookup) and passes 2.
`keep_state` finds 2, writes only the misses, and commits a state row naming parse units the file no longer holds.
`show` falls back to memory on the missing unit, but Task 10b's search takes candidates from the FTS table (line 553), so a record whose words row is gone is never a candidate and is silently left out of the results.
Verified with `python3 -I /var/tmp/lodge-recheck4/epoch_model.py` (`epoch_model.jsonl`), a model of the rule rather than lodge code: an epoch taken in the hits' snapshot leaves nothing absent, while one read after the hits leaves `[["a","1"],["b","1"]]` named but absent.
`test_keep_after_another_process_cleared` (line 527) catches an epoch read just before the keep, but not one taken with a lookup that falls between the clear and the keep.
Fix: add `Index.epoch() -> int`, which the build calls once before its first lookup; epochs never fall within a file, so any clear after that read shows as a difference.
Add a test with the clear between the `parses` and the `facts` lookups, asserting every key of the kept state has its parse and words rows.

### W2. Minor: "every ordinary table" includes `meta`, so the epoch can repeat

Handle: plan line 439 ("`DELETE` of every ordinary table ... and `meta.epoch` incremented") and line 31.
Failure scenario: an implementation that empties every table from `sqlite_master` empties `meta` too, and its increment then updates no row, so the epoch reads as absent (0) after every clear.
A build that took hits at 0 in a fresh file, or between two clears, then sees no change and writes only its misses, as in W1.
Verified with case `c_meta_deleted_fresh_file` of `epoch_model.py`: build epoch 0, file epoch 0 after the clear, two units named but absent.
Fix: say "every table but `meta`", read and raise the epoch in the clear's transaction, start it at 1 when the file is created, and test two clears in a row with a build that took its hits between them.

### W3. Important: the cap is twice the footprint the author chose, and a clear in place never gives the space back

Handle: plan line 439 (`INDEX_FILE_CAP = max(16 MiB, 2 × INDEX_BYTES_PER_FILE × files in the tree)`), d-4pbeax ("about 240 MB ... at 160,000 record files, keeping four stored states"), and `questions.md` line 7, whose 240 MB already counts the parse cache, the words, and all four states.
Failure scenario: at 160,000 files the cap is 1,500 × 160,000 × 2 = 480 MB of used pages, so the file grows to about 480 MB before the first clear.
The clear frees pages without shrinking the file, and nothing vacuums (line 439), so the file then stays at about 480 MB for the life of the build, twice the author's figure.
Verified with `python3 -I /var/tmp/lodge-recheck4/clear_cost.py /var/tmp/lodge-recheck4 200` (`clear_cost.jsonl`): `main_mb_before` 179.6 and `main_mb_after` 179.6, with 0.04 MB of used pages after the clear.
Under the generations of round 3 a fresh file held only its snapshot, so the doubling only became permanent with this round.
Fix: `INDEX_FILE_CAP = max(16 MiB, INDEX_BYTES_PER_FILE × files in the tree)`, which still holds one full state with its parses and words (about 163 MB by `questions.md` line 7), or take the doubled figure back to the author as a revision of SCALE-1; Task 12 reports the file's size against d-4pbeax's figure either way.
A lower cap makes clears more frequent, which W6 quantifies.

### W4. Important: on SQLite builds with secure delete, a clear writes the whole file through the WAL

Handle: plan lines 436, 439, and 458; the ruling's cost line "a clear costs one cold read".
This machine's system Python (3.14.7, SQLite 3.53.4) is compiled with `SQLITE_SECURE_DELETE` (`pragma secure_delete` returns 1); the project's uv Python (3.13.5, SQLite 3.47.1) returns 0.
Failure scenario: under secure delete every freed page is zeroed, so the clear's transaction writes about the file's whole size into the `-wal`, and a checkpoint copies it back.
Measured: a 179.6 MB index gave a 180.3 MB `-wal` and a 0.57 s clear on ext4 (0.06 s with secure delete off), and an 89.6 MB index on the FUSE NTFS mount took 2.5 s (0.03 s off), so about 13 s at the 480 MB of W3 on that disk, holding the write lock.
While another connection stays open (the viewer holds one for its life), the `-wal` keeps that size after checkpoints: 39.4 MB after a 39.2 MB clear, and 0 with `journal_size_limit=0` (`wal_held.jsonl`).
The cap counts used pages of the main file only, so the folder holds about twice the cap meanwhile.
Task 9 Step 4 times one clear "on a copy" under whichever Python the builder runs, so the uv Python reports the cheap case.
Fix: every index connection sets `pragma secure_delete=OFF` and a `journal_size_limit`; a test sets secure delete on through the pragma before the index opens a connection and asserts that a clear of a populated index leaves a `-wal` under a small bound.

### W5. Minor: a refused upgrade from shared to exclusive drops the shared lock

Handle: plan line 442 ("recreated only while this process's lock can be made exclusive without waiting").
On Linux a conversion removes the old lock before trying the new one, so a refused `LOCK_EX | LOCK_NB` leaves the process with no lock at all.
Verified with `python3 -I /var/tmp/lodge-recheck4/flock_protocol.py` (`flock_protocol.jsonl`): after the upgrade was refused and the other holder released, a third process got `LOCK_EX | LOCK_NB` while the upgrader was still alive, on ext4 and on the FUSE mount.
Failure scenario: a process meets corruption after opening (the failure-mode list does not say the corrupt rule is confined to `open_index`), its upgrade is refused, and it carries on reading unlocked; another process of the same build then upgrades, deletes, and recreates the file under it, and its lookups fail with an I/O error, so they miss.
Output is preserved by the fallback; the protocol's promise is not.
Fix: state that the corrupt rule applies in `open_index` only, and that a refused upgrade closes the lock file and returns `None` (or takes `LOCK_SH` again, blocking, before any further use); test the refused upgrade.

### W6. Minor: facts rows make clears periodic, and no step measures how often

Handle: plan lines 28 (facts never deleted but by a clear), 575 (every build stores its current snapshot's facts), 80, and 611.
Each changed read keeps a facts row for its new current ident, and none is ever evicted.
Its status mapping alone is about 2.4 MB at 160,000 records (`facts_size.py`, `facts_size.json`: 15 bytes per record marshalled, problems not counted).
So a clear comes about every 100 changed reads under the cap as written, and about every 32 under W3's single cap; each clearing read rewrites every unit it used (about 5 s by the cost table's parse cache, FTS, and state rows) outside any stop.
Nothing in Tasks 10a, 10c, or 12 reports clears per changed read, so a store that clears every few reads would pass the replay.
Fix: in the eviction transaction, also delete facts rows whose ident no remaining state names, and have `keep_state` always `INSERT OR IGNORE` both facts rows it used (a missing facts row is a miss for the next build and is no part of a read's completeness); or, at least, record facts bytes per changed read in Task 10c Step 4 and clears per hundred changed reads in Task 12.

### W7. Minor: the lock's order and the lockless cases are unstated

Handle: plan lines 435, 441, and 442; lodge supports Windows (`docs/superpowers/plans/done/2026-10-29-lodge.md` line 58, `src/lodge/viewer/server.py` line 23).
The plan does not say that `LOCK_SH` is taken before `sqlite3.connect` and released after `close`; a reader that connects first can be deleted under between its connect and its lock.
A process that cannot create the lock file (the read-only folder of line 441) reads without the lock, and a writable process of another build may delete the file under it after 7 days; its lookups then fail with an I/O error and miss.
Without `fcntl`, a corrupt file can never be made exclusive, so line 442 returns `None` for that build until the folder is removed by hand, with no message.
Fix: take `LOCK_SH`, blocking, before connecting and release it after closing; open an existing lock file read-only when it cannot be created; without `fcntl`, delete the corrupt file and let the delete fail while another process holds it open (Windows refuses), or say that the index stays off; one test each.

### W8. Minor: "last written" ages a build that only reads, and the folder is no longer bounded

Handle: plan lines 434, 435, and 527 (`test_seen_read_writes_nothing`).
A seen read writes nothing by design, so a build used every day for seen reads only has a main file and `-wal` older than 7 days, and another build deletes it at its next opening whenever no process of it is running; its next read is then cold (about 12 s at scale).
The count and folder-size limits of round 3 were dropped, so within 7 days nothing bounds the number of builds' files, and lock files, one per digest and never deleted, accumulate for good; the digest changes with every edit of lodge's source (line 434).
Fix: `open_index` touches its own lock file, and a build's age is its lock file's modification time; keep a count bound (the oldest other builds beyond a few go, under the same `LOCK_EX | LOCK_NB`).

### W9. Minor: leftovers of the sweep

Handle and fix, each an edit:
- line 27: the invariants' heading cites d-t3afj1, d-4j98ph, and d-gvz66f, but invariant 4 is now d-e3stjn's and d-c6cegr's; add them.
- line 410: `index_db.py` still lists "pruning" while `index_space.py` now holds the deletion of old builds' files; drop it from `index_db.py`.
- line 547: Task 10b's comment gives `keep_state(..., parses, misses, words)`, without the new `epoch`, so the order of the two trailing parameters is open; give the full signature.
- line 527: `test_keep_after_another_process_cleared`, in Task 10a, asserts words rows, which exist only from Task 10b (as does the older `test_unit_found_by_one_process_survives_another_keep`, line 528); move the words clause to Task 10b.
- line 80: "and the reads after it" are each called a cold read, but the clearing writer rewrites every unit it used, so only the clearing read pays; say so.

### W10. Minor, outside this round: personal paths in a public repository

Handle: `brief.md` lines 9 and 35, `review-brief.md` line 3, and `plan-recheck-3.md` lines 109 and 121 hold absolute home paths, against `CLAUDE.md`'s public-repository rule.
Failure scenario: the paths reach `main` with the plan folder.
Fix: replace them with paths relative to the repository or a generic placeholder.

## Answers on the clear-in-place design

| Question | Result |
|---|---|
| Does a WAL reader keep a consistent snapshot across a clear? | Yes: inside `BEGIN`, a reader that had read the epoch and 10 rows of an FTS cursor finished all 4,000 old rows, matched the old words and none of the new, and read the old parse at reused rowid 1 and the old state, after the writer cleared, dropped and recreated the FTS table, raised the epoch, wrote new rows into the same rowids, and checkpointed; the checkpoints returned busy while the reader held its snapshot; the reader's next transaction saw epoch 2, the new rows, and `integrity_check` ok; on ext4 and on the FUSE mount, secure delete on and off (`clear_snapshot.jsonl`). |
| Can `meta.epoch` and the rewrite rule leave a state without its units? | Not when the epoch is read before, or in the snapshot of, the build's first hit and never repeats; the plan supplies neither (W1, W2). |
| Is the flock protocol correct? | Yes for a reader holding `LOCK_SH` from before its connection to after its close: `LOCK_EX \| LOCK_NB` was refused while another process held `LOCK_SH` and granted after; a reader blocked on `LOCK_SH` during a deletion waited 0.46 s and opened a fresh, intact, empty file; the same on the FUSE mount; the edges are W5 and W7. |
| Is the FTS recreate inside the clear safe for concurrent readers? | Yes, as in the first row, including a cursor open across the drop, and statements prepared before it in the reader's next transaction. |
| Can a deletion interrupted between the main file and its `-wal` poison the next file? | Not reproduced: with the `-wal` and `-shm` of uncheckpointed commits left behind, or the main file alone, the next opener found an empty schema and `integrity_check` ok, on both filesystems (`orphan_wal.jsonl`). |

## Verification

The worktree was clean at `5a7dbc464d7d10e17a535da6d7eeeb6b704478e4`; `git diff --stat 2dffc85 5a7dbc4` touches only `questions.md` and the SCALE-1 record.
`/var/tmp` is ext4, and the worktree's folder is `fuseblk` (NTFS), by `findmnt -T`.
Probes ran with the system Python 3.14.7 and SQLite 3.53.4 (`python3 -I`); the project's interpreter was read with `uv run --frozen --quiet python`.

| Command | Evidence under `/var/tmp/lodge-recheck4/` |
|---|---|
| `python3 -I clear_snapshot.py /var/tmp/lodge-recheck4 <the FUSE folder>` | `clear_snapshot.jsonl`: two processes, a reader's snapshot across a clear, an FTS drop and create, rowid reuse, and four checkpoint modes. |
| `python3 -I clear_cost.py /var/tmp/lodge-recheck4 200` and `... <the FUSE folder> 100` | `clear_cost.jsonl`: clear time and `-wal` size with secure delete on and off, used pages and file size after. |
| `python3 -I wal_held.py /var/tmp/lodge-recheck4` | `wal_held.jsonl`: the `-wal` after a clear with a second connection open, with and without `journal_size_limit`. |
| `python3 -I flock_protocol.py /var/tmp/lodge-recheck4 <the FUSE folder>` | `flock_protocol.jsonl`: shared against exclusive, a refused upgrade, and a reader blocked during a deletion. |
| `python3 -I orphan_wal.py /var/tmp/lodge-recheck4 <the FUSE folder>` | `orphan_wal.jsonl`: three orders of an interrupted deletion. |
| `python3 -I epoch_model.py` | `epoch_model.jsonl`: three placements of the epoch read. |
| `python3 -I facts_size.py` | `facts_size.json`: one status mapping at 160,000 records. |

Every scratch folder on the FUSE mount was removed by its probe.

Read: `.claude/agents/reviewer.md` in lodge, `CLAUDE.md`, `plan-recheck-3.md`, `plan-fix-4.md`, the diff `f5da619..2dffc85` in full, plan lines 1 to 90, 405 to 460, 470 to 535, and 540 to 579, and d-e3stjn, d-c6cegr, and d-4pbeax through lodge.
Not read: `lodge spec`, `lodge guide`, the plan's other tasks, `plan-report.md`, and the earlier reviews; lodge's source was read only for `fcntl` and Windows mentions.

## Counts

R1 to R5: 5 fixed (R5 in the contract, subject to W1), 0 partly fixed, and 0 not fixed.
New findings: 0 Blocking, 3 Important (W1, W3, and W4), and 7 Minor (W2 and W5 to W10).
The most important finding is W1: `keep_state` takes an epoch that no interface supplies, and an epoch read after the build's hits lets a state be kept whose parse and words rows a clear removed, which search then silently omits.
