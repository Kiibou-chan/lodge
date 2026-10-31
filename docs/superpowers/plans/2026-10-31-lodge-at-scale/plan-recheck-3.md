# Plan recheck 3: lodge at scale, fix round 3

Status: complete.
Scope: `git diff d41fdfd a3f8eeb`, its mapping in `plan-fix-3.md`, and V1 to V8 in `plan-recheck-2.md`.
Plan line numbers refer to `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` at `a3f8eeb`.
The coordinator's ruling d-t3afj1 was read with `uv run --frozen --quiet lodge show d-t3afj1 --reasoning`.
This is a review of the proposed design, since the index modules have not been implemented.
All executable probes and their output are kept under `/var/tmp/lodge-recheck3/`.
No network or `lodge add` is used.

## Status of V1 to V8

| Finding | Status | Plan lines | Assessment |
|---|---|---|---|
| V1, eviction drops a unit or facts needed by a new state | Fixed | 28 to 30, 506 to 509, 517 to 518, 524 to 525, 549 | Within one generation, eviction never deletes shared units or facts, and the revert and two-process interleaving are explicit tests; R1 concerns publication, and R5 concerns copying to another generation. |
| V2, unspecified and unbudgeted eviction | Fixed | 78, 80, 507, 517, 529 | Eviction is specified as deletes of the state's own indexed rows by state key, with no reference counting or FTS deletion, and its timing is requested separately; the new rollover latency has the separate gap R4. |
| V3, implicit reads mix re-kept states | Fixed | 32, 435, 496, 508, 517, 524 to 525 | Explicit transactions, WAL, whole-state replacement, newest-on-re-keep ordering, and a test that distinguishes default Python behaviour are specified; R1 can still defeat isolation across pathname aliases. |
| V4, cache-key ordering | Partly fixed | 388 to 391, 398 to 399 | The index-file race is covered, but only that stat is checked after the call, leaving conversion sources and configuration exposed to R3. |
| V5, a family root has no citer row | Fixed | 513, 556 | Every code and every family root gets a row, including an empty row, and search tests include a root that is no record's own code. |
| V6, git status makes a seen read write | Fixed | 76, 388, 390, 437, 524 | Both caches are process-local, the flags call is budgeted, and the seen-read test explicitly follows a git status that rewrites git's index. |
| V7, path and blob words pollute FTS candidates | Fixed | 545, 549, 555 | The FTS table has no key column, its rowid joins to the parse, column filters are specified, and a regression test excludes path-only words. |
| V8, keep_parses callers and an import cycle | Fixed | 536, 544 | The pure helper lives in core, and the caller, export, and fake are listed. |

These are findings about the revised plan's contract and tests, not claims that its unimplemented index passes them.

## Confirmed new findings

### R1. Blocking: two rebuilders share the temporary database and defeat WAL snapshot isolation

Handle: plan lines 32, 434, 438, and 450, especially the single `index-<digest>.<n+1>.sqlite.tmp` pathname.
Failure scenario: A checkpoints and closes that temporary file, B opens the same temporary file, A publishes it with `os.link`, and B continues writing through the temporary pathname while a reader opens the published pathname.
The published main file and B's main file are one inode, but the two processes use different `-wal` and `-shm` pathnames.
B can checkpoint over pages the published reader is reading without respecting that reader's WAL snapshot.
Verified with `python /var/tmp/lodge-recheck3/generations.py`, whose `shared_tmp_breaks_snapshot` result has `first=old`, `last=new`, `in_transaction=true`, and a successful checkpoint by B.
A transaction containing both lookups therefore does not describe either build, despite following the explicit transaction rule.
The `os.link` destination collision only arbitrates publication after both writers have already shared the source database.
Fix: give each builder an exclusively created, unpredictable temporary pathname, close every connection and finish a checked checkpoint before linking, never reopen or mutate a published inode through a temporary alias, and remove only that builder's temporary file and sidecars.
Test two actual processes, including the interleaving between one builder's close and link, and assert that the published reader retains its snapshot as well as that only one publication wins.

### R2. Important: ten minutes without modification does not prove an old WAL generation has no reader

Handle: plan lines 31, 434, and 450, including the claim that a process holding a deleted file keeps reading it.
Failure scenario: a process opens generation n and is descheduled before its first lookup, generation n+1 is published, and another opening unlinks n and its sidecars after the modification-age checks pass.
Reading does not refresh those modification times, and a process can remain paused for longer than ten minutes.
Verified with the `prune_before_first_read` case in `/var/tmp/lodge-recheck3/generations.py`: the already-open connection's first lookup fails with `SQLITE_IOERR_FSTAT`, code 1802.
An already-established transaction with the old WAL mapped did finish in the separate `prune_during_transaction` case, so the failure is specifically wider than that favourable case.
The generic SQLite-error fallback should preserve printed output, but the promised ability to finish on the old file is false, and the fallback can repeat throughout the lifetime of the pinned connection.
Fix: pin generations with a reader lease or a shared lifetime lock and require an exclusive non-blocking lock before pruning the main file and both sidecars, with an opener rechecking the selected generation under that protocol.
Alternatively, explicitly abandon the finish-on-old-file guarantee, invalidate the failed connection, reopen a current generation, and test the fallback for a reader paused before its first statement and between transactions.

### R3. Minor: V4 remains partly fixed because conversion sources are not checked again

Handle: plan lines 388 to 391 and 398 to 399.
Failure scenario: the conversion-cache key captures an attributes file with a filter, that file changes before `git check-attr`, and the index-file stat stays unchanged.
The new rule accepts the answer for the changed attributes under the original attributes bytes.
Restoring those original bytes makes the incorrect answer a cache hit.
Verified with `python /var/tmp/lodge-recheck3/cache_key.py` in a scratch git repository: both index stats match, the restored source hits the recorded key, the cached filter is `unspecified`, and the real filter is `demo`.
The tracked record is clean according to `git diff-files`, while its blob says `title: GIT` and its disk bytes say `title: DISK`, so trusting the stale conversion answer makes the fast read use the wrong text.
Taking the key before the call fixes the reported index-file race, but the conversion key includes source bytes and configuration values too.
Fix: capture and compare the complete conversion key before and after the git operation, decline to cache a changed key, and add the attributes-change-and-restore interleaving alongside the existing index-file test.

### R4. Important: the newly budgeted rebuild exceeds the changed-read stop and the replay never measures it

Handle: plan lines 78, 80, 83, 114, 438, 450, and 610.
Failure scenario: ordinary edits grow the immutable cache past its cap, then the next changed read synchronously rebuilds every parse unit, its words, and the state before returning.
The plan budgets that write at about three seconds more than its read, while the unchanged stop applies to every changed read above three seconds.
The replay restores the same saved seen index before each changed run, so that replay need not encounter the accumulated size that triggers a rebuild.
The tiny-cap unit test establishes correctness rather than the full-size latency, and thus cannot supply the missing performance evidence.
This is a contradiction between the new cost row and the existing acceptance rule, rather than a measured lodge timing, since the implementation does not exist.
Fix: add a full-size forced-rollover benchmark with the same output comparison and phase timing as an ordinary changed read, then either fit rebuilding within the existing stop or obtain an explicit separate acceptance bound for rollover reads.
Also check whether the intended snapshot alone fits the cap and what a process pinned to an over-cap old generation does after another writer has already published its successor, so repeated attempts do not each pay for a rebuild that cannot win its link.

### R5. Minor: the rebuild contract does not carry forward a published-facts cache hit

Handle: plan lines 29, 438, 504 to 509, and 572.
Failure scenario: the build finds its published facts in generation n, so it does not compute them, and the cap sends its `keep_state` into a fresh generation.
Line 572 requires the build to store the current facts and the published facts when it computed them, whereas line 509 explicitly expands only the parse units to all units on a rebuild.
That wording admits a new state whose current facts exist but whose named published ident has no facts row in its generation.
`/var/tmp/lodge-recheck3/rebuild_facts.py` demonstrates that reading of the contract with two scratch databases, rather than claiming to test an implementation.
A later build can recompute the missing facts, so this is a completeness-contract and performance gap rather than demonstrated wrong output.
Fix: pass all facts the build used, including cache hits, into `keep_state`, write them all when rebuilding, and test rollover after a published-facts hit.

## Answers on the new design

| Question | Result |
|---|---|
| Can ordinary eviction leave a state without its words or facts in the same generation? | No under the specified atomic writer: parse and words insert together, immutable units and facts survive every eviction, and the state marker commits with its own rows. |
| Does a fresh generation necessarily contain every fact named by its state? | Its current facts are computed, but the wording does not carry a cached published-facts hit into the fresh file, as R5 explains. |
| Does the missing-value fallback alone protect search? | No: a missing FTS candidate is invisible to search, so the atomic-unit invariant remains essential, and R1 invalidates the snapshot proof. |
| Does a reader already using the old file survive publication to a distinct generation name? | Yes in the probe: the old transaction retained its WAL-backed value while a complete new generation was linked under a new pathname. |
| Are two writers swapping at once safe as written? | No, because of their shared temporary pathname, as R1 demonstrates; distinct private sources make the final destination collision safe. |
| Is a single-writer process crash mid-swap safe? | Yes at the five probed publication boundaries: the highest published generation was either complete-old or complete-new, and integrity_check returned ok. |
| Does ten-minute pruning protect every slow reader holding an old file? | No, because it does not protect an open connection paused before its first lookup, as R2 demonstrates; an established transaction succeeded in the separate probe. |
| Does WAL work on native ext4 here? | Yes for the tested cross-process snapshot, write exclusion, and recovery operations. |
| Does WAL work on the NTFS filesystem through FUSE on /home here? | Yes for those same operations, including actual shared-memory sidecars; this installation did not reproduce the suspected shared-memory failure. |

The same-generation completeness statement covers normal operations and injected statement failures, not arbitrary external deletion or undetectable storage corruption.
A generation with a private temporary name, a completed and checked checkpoint, all connections closed before publication, and a distinct published pathname preserves that argument across publication.
The current shared temporary name does not provide those conditions.
A process crash leaves no partially committed state visible in the isolated single-writer cases, but a crash after linking and before removing the temporary alias makes it especially important never to reuse that alias.
The probes kill processes and do not simulate power loss, device failure, or a machine reboot.
WAL with synchronous=NORMAL can lose recent committed cache work after power loss, so the design must retain its disposable-cache and in-memory fallback semantics.
The filesystem result applies to this mounted NTFS implementation and SQLite build, rather than proving that every FUSE implementation supports WAL correctly.
Keep the generic I/O-error fallback and exercise the index's WAL tests on supported filesystem kinds, since Task 11's FUSE folder-signature tests alone do not test WAL.

## Verification

The worktree began clean at `a3f8eeb6ac19867bd2aba2d915c520a578b3c83d`.
`findmnt -T /var/tmp` identified `/dev/nvme0n1p3`, ext4, and `findmnt -T /home/kiibou/.cache/lodge-work` identified `/dev/nvme0n1p4`, fuseblk.
The probes used Python 3.14.7 and SQLite 3.53.4 on scratch databases only.
The coordinator's ruling was read with the exact command in the brief, and no index code exists yet to run as a lodge integration test.

| Command | Evidence saved under /var/tmp/lodge-recheck3/ |
|---|---|
| `python /var/tmp/lodge-recheck3/filesystems.py` | `filesystems.jsonl`: WAL mode, -wal and -shm creation, cross-process old/old/new snapshot, a competing writer rejected as locked, hard-link identity, and killed-writer recovery with only the committed row and integrity_check ok on each filesystem. |
| `python /var/tmp/lodge-recheck3/generations.py` | `generations.jsonl`: two actual processes with shared temporary aliases mix a snapshot; separate private sources preserve it and reject the losing link; distinct-generation publication preserves an old reader; pruning before the first lookup raises SQLITE_IOERR_FSTAT. |
| `python /var/tmp/lodge-recheck3/atomicity.py` | `atomicity.jsonl`: all 12 statement boundaries rolled back an interrupted keep including eviction, parse, words, and facts; a reverted immutable unit and its words and facts survived eviction; default Python reads mixed builds while explicit reads did not; five killed-writer publication stages selected complete generations. |
| `python /var/tmp/lodge-recheck3/cache_key.py` | `cache_key.json`: an attributes-change-and-restore sequence accepts an incorrect conversion cache entry with unchanged index stats and different disk and blob text. |
| `python /var/tmp/lodge-recheck3/rebuild_facts.py` | `rebuild_facts.json`: a small model of the permitted keep_state payload omits a cached published-facts row from the new generation. |

The single NTFS probe directory was created under `/home/kiibou/.cache/lodge-work/recheck3-ntfs-jyxem4sb/` and removed in a finally block, with its removal recorded in `filesystems.jsonl`.
The remaining scripts, fixture repositories, and databases are under `/var/tmp/lodge-recheck3/`.
No network, `lodge add`, commit, push, or benchmark against a real store was used.
This report is the only worktree change.

## Counts

V1 to V8: 7 fixed, 1 partly fixed, and 0 not fixed.
New findings: 1 Blocking, 2 Important, and 2 Minor.
The most important finding is R1: two writers sharing the temporary generation pathname can silently defeat an explicit WAL read transaction, so each builder needs a private, exclusively created temporary database before os.link can safely choose a winner.
