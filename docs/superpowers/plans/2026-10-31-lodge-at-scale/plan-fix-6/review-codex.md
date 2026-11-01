# Adversarial review of plan fix 6

Status: complete.
Findings: 2 Blocking, 9 Important, and 2 Minor.
Review target: detached 83ef70b in `/var/tmp/lodge-review-pf6/wt`, unchanged.
All probe writes are in `/var/tmp/lodge-review-pf6/scratch`; only synthetic `s900` is copied.
The `s90000` store and `/var/tmp/lodge-plan-fix6/venv` are used for sequential read-only measurements.
No command is run in the builder's worktree.

## Findings

### R1 Blocking: the `info/attributes` guard can permanently poison a raw entry

Where: `tasks.md:115-123`, Task 11b `usable`, refresh, and its proof.
Failure scenario: `info/attributes` is absent when `usable()` runs, appears with `* filter=up` during `update-index`, then disappears.
The old file passes both age tests and its two `lstat` results are equal, but Git records the clean filter's output, not the disk bytes.
Thereafter `info/attributes` is absent and `diff-files` reports nothing, so reads can reuse the wrong blob indefinitely.
Reproduced on the supplied Git 2.56.0, on a copy of `s900`, with every proposed override: `eligible True`, `L0==L1 True`, disk blob `27f5634…`, cached blob `4d38b4c…`, `diff-files b''`.
The runnable probe is `scratch/probe.py info-race`, with output `scratch/info-race.txt` under the review scratch directory.
The file never changed during the call; F1, F2, and F3 do not help.
A preflight existence check, even repeated after the call, cannot detect this absent-present-absent sequence.
Fix: make conversion isolation effective for the entire Git process, for example by using controlled private Git metadata with no shared `info/attributes`, or populate verified raw entries without invoking the conversion machinery.
Do not retain any entry produced while isolation was uncertain; test the transient-source race, including linked worktrees.

### R2 Important: `--info-only` leaves raw blobs unavailable to `texts()` on recovery

Where: `tasks.md:94-95,117-125`; unchanged `src/lodge/gitstore/listing.py:109-129`.
Failure scenario: an old unstaged edit is in the raw index, then the SQLite cache is deleted, cleared, corrupted, or invalidated by a new build.
A new store object takes that blob from `diff-index`, without reading the path, but the parse miss needs its bytes.
`update-index --info-only` never wrote the object, and `_texts` only has this process's disk texts or `cat-file --batch`.
It therefore raises `git cannot read the file` for an ordinary recovery which the Global Constraints say must be a cache miss.
Fix: explicitly extend `texts()` for raw-origin paths: read and hash the disk bytes on a parse miss, compare with the identity's hash, and restart/fall back if changed.
Alternatively store the raw objects, with a disposal/space policy, rather than using `--info-only`.
Add recovery tests with raw index retained but SQLite absent, a new build digest, and a clear between identity and parse lookup.

R2's direct probe is now complete (`scratch/probe.py missing-object`, `scratch/missing-object.txt`): age-eligible raw entry, identical before/after stat, correct raw hash, clean `diff-files`; `cat-file --batch` returns `<oid> missing` and `_texts` raises `LodgeError`.

### R3 Important: folder links still make the fast tree differ from the exact tree

Where: `tasks.md:79-83,117-118`, unchanged `identity.py:122-137`; Task 8b review A1.
Failure scenario: a real folder is renamed elsewhere and replaced by a symlink to it.
Git correctly names the indexed children as deleted because an ancestor is a symlink, but Task 11b then calls `read_disk` on those child paths.
`lstat` follows ancestors, so `read_disk` reads through the link and keeps those children in the overlay/base, alongside the new link entry.
`disk_tree` only lists the link.
The direct probe (`scratch/probe.py folder-link`, `scratch/folder-link.txt`) prints the child in `diff-files`, `read_disk through link b'original\n'`, `exact has child False`, and `exact has link True`.
Copying the outside folder instead also exposes arbitrary outside contents.
Attachments have the same ancestor issue; using `stat` for folder-row hits also follows symlinks.
Fix: track the reachable real directories, prune stale descendant rows when an ancestor disappears or changes kind, and treat an indexed child outside that reachable set as deleted without reading through it.
Carry all three A1 probes into Tasks 8c/11/11b explicitly, including a link inside an attachment path and a link swap during traversal.
Using Task 8b's current walk as the only oracle is insufficient: it has the same known bug.

### R4 Blocking: the racy-rule proof is false for an ordinary writable mmap on native ext4

Where: `tasks.md:118-123`, Task 11b's F1 and “a recorded blob is never stale”; `plan-fix-6.md:35,54`.
Failure scenario, reproduced without a fake clock or stat shim: keep a regular file mapped `MAP_SHARED` and writable, dirty its page, wait 2.1 seconds, and cache it with the exact proposed overrides and `update-index --info-only`.
Both eligibility times are older than 2 seconds and L0 equals L1.
Write a different byte through the still-writable mapped page.
The disk read sees different bytes, but inode, size, mtime, and ctime are identical; `diff-files` returns no paths.
Probe: `scratch/probe.py mmap`, output `scratch/mmap.txt`: `eligible True L0==L1 True`, `post-change stat==cached stat True bytes changed True diff-files b''`.
This is a concurrent writer allowed by the current contract, on this machine's native ext4, not a hypothetical broken filesystem.
Linux documents delayed timestamp updates for writable shared mappings in [mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html).
F1 is an additional restriction on writers, not a property established by d-8kq2nk or by enabling Git's ctime comparison.
Git itself can miss this case, which does not satisfy lodge's stronger “equal identities imply equal exact trees” requirement.
Fix: withdraw the unconditional proof, add this regression, and retain a byte-reading path where byte stability cannot be established.
If the coordinator instead accepts Git's weaker observational contract for indexed reads, record that explicitly as a correctness-contract change, including the mmap exception; do not describe it as exact-tree equivalence or as already authorised by the folder-cache decision.
A larger age threshold alone does not fix it.

### R5 Important: filesystem and clock assumptions are neither checked nor safely bounded

Where: `tasks.md:115,119,133`; Task 11 Step 4 at `tasks.md:86`.
Failure scenario: the default is to enable RAW-1 everywhere unless a few build-time tests happen to fail on an available FUSE mount.
That does not establish F1 or the one-second clock bound for the user's filesystem, mount options, remote clock, or a later wall-clock rollback.
Linux FAT truncates mtime and ctime to two-second units and shares their on-disk field, so ctime is not an independent defence against an mtime restored by `utime`; see the [kernel FAT implementation](https://raw.githubusercontent.com/torvalds/linux/master/fs/fat/misc.c).
NTFS through FUSE is not automatically unsafe, but the driver's `delay_mtime` option deliberately delays both modification and change times for open files, defeating a two-second admission rule; see the [NTFS-3G manual](https://github.com/tuxera/ntfs-3g/wiki/Manual).
A coarse two-second timestamp can also be more than one second behind the wall clock without any clock skew at all.
`statvfs` gives no filesystem type, and `/proc/mounts` plus a generic `fuseblk` blacklist cannot prove the behaviour of an individual mount, nested mount, bind mount, or another platform.
Fix: define a conservative supported-filesystem/mount/writer contract and exact fallback for everything else, covering every traversed mount and the git-dir mount; handle clock epochs/rollback rather than assuming F2 forever.
Test coarse timestamp and delayed-update models explicitly, as well as symlink/hardlink writes and open mapped writers.
Do not treat a successful finite test run as a proof or permit a failed native test such as R4 to be bypassed by the FUSE-only wording.
I confirmed `/home` is `fuseblk` and `/var/tmp` is ext4 with read-only `findmnt`; I did not write to `/home`, per the scratch constraint, and make no claim that this particular NTFS mount reproduces the delayed-update failure.

### R6 Important: unverified entries are visible to another reader before the post-check

Where: `tasks.md:117-118,129`, Task 11b refresh publication and concurrent-refresh tests.
Failure scenario: process A passes L0 for an old regular file; a writer replaces that path with an initialised submodule directory before `update-index` examines it.
`update-index --add` can publish a mode-160000 gitlink in the raw index, even though the plan says that index only contains regular files and symlinks.
A is suspended after Git commits the index and before L1/`--force-remove`.
Process B's before-and-after index keys match, because the invalid entry is already published and stationary throughout both diff calls.
`diff-files` can name nothing (for example with ordinary `diff.ignoreSubmodules=all`), while `diff-index --raw` supplies the submodule commit ID, which the prescribed algorithm treats as a raw file blob.
The exact tree has files below that directory and no blob at the gitlink path.
Probe: `scratch/probe.py gitlink-race2`, output `scratch/gitlink-race2.txt`.
Post-validation removal by A cannot repair B's answer, and A can also exit before that removal.
Fix: make validation part of atomic publication, or make readers reject entries not covered by a completed validation generation; serialize the whole refresh/validation/read protocol with a separate persistent lock if necessary.
Independently reject mode 160000, sparse-directory entries, and unexpected flags on the raw path, and take the exact fallback for them.
Test a reader in the interval after `update-index` and before L1, plus a crash in that interval; the current “one holds the lock, the other skips” test does not exercise this.

### R7 Important: age does not prove a Git lock is abandoned

Where: `tasks.md:118`, “a lock older than 10 minutes is deleted first”.
Failure scenario: Git is suspended, the machine sleeps, an I/O call stalls, or a clean filter blocks while the lock remains owned.
Another lodge process unlinks that live lock solely on age and starts a second writer.
Git's exclusive-create lock protocol no longer excludes concurrent writers, and the suspended writer can later commit or remove the second writer's lock pathname.
The assumptions that Git only holds the lock during one call and that the call normally takes milliseconds do not bound its wall-clock duration.
The same age-is-not-liveness argument is explicitly recorded in d-e3stjn's reasoning.
Fix: skip refresh when the Git lock exists, irrespective of age, or introduce real ownership/liveness locking; leave an abandoned lock to explicit recovery which cannot race a live holder.
Replace `test_stale_lock_is_removed` with tests that a suspended/aged holder is never stolen and reads still succeed by fallback.

### R8 Important: the 12.5 ms `diff-index` result is for a different raw-index construction

Where: `plan-fix-6.md:88-91`, `measure/private_index.py:1,9`, `tasks.md:117,124`, expected-cost table at `tasks.md:21`.
Failure scenario: the timing script explicitly uses `raw.index` built by `read-tree HEAD` plus refresh, which preserves a useful cache-tree extension.
The specified production build uses `update-index --add --info-only --stdin` into an empty private index.
At `s90000` I measured the latter's clean `diff-index --cached --raw HEAD` at 50.97 ms best, 51.92 ms median, versus the reported 12.5 ms.
A control using `read-tree HEAD` and refresh reproduces 12.21 ms (13.50 ms with attachment exclusion).
Changing only the negative attachment pathspec does not explain the gap: the stdin-built index takes 50.8 to 52.4 ms with all four pathspec variants.
The `diff-files` result does reproduce at 42.42 ms best, 47.72 ms median; build is 1.128 s and 21,734,784 bytes.
Fix: rerun the complete proposed hit against the actual raw-index build and after a persistent unstaged edit, with every proposed override and no attachment entries.
Use that number in the cost table, including any publication locks/isolation changes needed by R1/R6.
Do not assume that a cache-tree optimisation from a HEAD-seeded control survives raw edits or the production build.
This does not itself prove 0.3 s impossible: the two diff calls are intended to overlap, but that overlap needs its own representative measurement.

### R9 Minor: the fallback estimate contradicts the measured identity cost

Where: `tasks.md:21`, expected-cost row says “without Task 11b ... about 0.6 s under core.autocrlf=input”.
Failure scenario: RAW-1 is disabled by old Git, `info/attributes`, permissions, or a filesystem restriction, so the builder/coordinator budgets against 0.6 s.
Task 8c Step 4 and this report's own measurements instead leave the identity alone at about 3.1 s, before CLI startup or any indexed read.
The rerun is 3.192 s.
Fix: correct the fallback row to the measured value and distinguish the rejected SQLite stat-cache alternative (about 0.6 s total) from the actual Task 8c/11 fallback.
Do not describe the performance guarantee as applying under any `core.autocrlf` without naming the prerequisites for RAW-1.

R5 also has a deterministic clock/coarse-stat model probe: `scratch/clock_model.c` interposes only this fixture's Git `lstat` timestamps, keeping them in a tick three seconds behind the process clock.
`scratch/probe.py clock-model` rewrites `AAAA` to `BBBB` on the same inode; Git retains the old blob and returns `diff-files b''` (`scratch/clock-model.txt`).
This is a model of the rejected F2/finite-resolution case, not a claim to have mounted FAT or altered the machine clock.

### R10 Minor: `--attr-source` did not exist in Git 2.40

Where: `tasks.md:115`, `plan-fix-6.md:36`.
Failure scenario: the stated “Git 2.40 or later” requirement is used for version gating and a supported-looking 2.40 executable rejects the global option.
[Git 2.40's option parser](https://raw.githubusercontent.com/git/git/v2.40.0/git.c) lacks it; [Git 2.41's parser](https://raw.githubusercontent.com/git/git/v2.41.0/git.c) has it.
Fix: retain capability probing as the authority and correct the version annotation to 2.41; a rejected option must choose the fallback that matches the exact tree without rewriting the raw index.
An old-Git probe must test the actual refusal path, not just a version comparison.

### R11 Important: a stable index key does not fix historical conversion claims on the fallback path

Where: `tasks.md:50-53,115`; Task 8b conversion fallback, inherited `attributes.py:41-70`.
Failure scenario: an old CRLF file is staged under an untracked root `.gitattributes` containing `*.md text eol=crlf`, so the real Git index records HEAD's LF blob with the CRLF file's current stat.
Remove that attributes file without touching the record or Git's index, then read on the Task 8c/11 fallback (old Git, disabled RAW-1, etc.).
All five Git calls can see the same index; current conversion sources are empty; Git's stat check is clean.
The fast listing keeps HEAD's LF blob although `disk_tree` reads CRLF.
Reproduced on a copied `s900` with isolated configuration and a 2.1-second wait before staging: `index key unchanged True`, `raw differs HEAD True`, `fast==HEAD True`, `fast==disk False`, `diff-files b''`.
Probe: `scratch/removed_attrs.py`, output `scratch/removed-attributes.txt`.
This is already stable before the read starts, so retries around the index file cannot close it.
The same provenance issue applies when an autocrlf setting or clean-filter source that produced an entry is removed or changed.
Fix: make the fallback exact whenever raw-byte provenance of the real index cannot be established; do not infer historical non-conversion from the absence of current sources.
Add attribute-removal and conversion-setting-removal tests on fresh store objects, as well as transient-source tests where a changed source key causes the current answer to fall back rather than merely declining to cache it.
RAW-1's isolated raw entries can solve this particular provenance problem only after R1/R6 are fixed; the fallback still has to preserve the Global Constraints.

### R12 Important: a seen CRLF checkout still produces a full-tree raw overlay

Where: `plan-fix-6.md:10,35-37`, `tasks.md:21,117`, Task 11b's `diff-index` and overlay identity.
Failure scenario: a normal `core.autocrlf=true` checkout has CRLF disk bytes and LF HEAD blobs for all record files.
Even after the raw index is fully warm and `diff-files` is empty, `diff-index --cached --raw HEAD` returns every record on every read, since each correct raw blob differs from HEAD.
The plan has no persistent identity/digest for this raw-index generation, so it must emit, parse, and hash the full overlay in every new CLI process.
The clean-LF benchmark under an overridden `autocrlf=input` does not measure that case.
An actual copied `s900` probe confirms it: 1,607 CRLF files, real Git status clean, raw `diff-files` clean, raw `diff-index` 1,607 entries (`scratch/crlf_seen.py`, `scratch/crlf-seen.txt`).
A performance model at `s90000`, changing only OIDs in a scratch index to represent 160,800 differing raw blobs, returns 27,119,445 bytes in 175.01 ms best; parsing the raw overlay takes 93.36 ms and the specified sorted identity another 57.46 ms (`scratch/overlay_measure.py`, `scratch/overlay-measure.txt`).
The model is explicitly not asserted to match the unchanged benchmark disk; its purpose is to measure the real full-size diff output and the prescribed identity computation without copying or editing `s90000`.
The measured 158.58 ms startup/dispatch plus the 175.01 ms Git call already exceed 0.3 s without LAZY-1, before parsing, folder rows, or lookups; the straightforward whole estimate is about 0.496 s including those pieces.
This is a steady seen state, not a cold read or the one-changed-record case.
Fix: retain a validated raw-index generation's overlay/tree identity persistently and reuse it when the raw index and HEAD are unchanged and `diff-files` is clean, or adopt another measured identity representation which avoids a full overlay per process.
Add an all-CRLF seen replay at full size and withdraw “under any core.autocrlf” until it passes; LAZY-1 alone cannot cover this gap.

### R13 Important: the old-Git/disabled-RAW fallback still inherits the known gitlink mismatch

Where: `tasks.md:35,47,63,115`, Task 8c's `Committed.listing` and its requirement to consume Task 8b unchanged; Task 8b review A4.
Failure scenario: HEAD and the real index contain a mode-160000 gitlink below `lodge/`, with an empty submodule directory on disk.
The fallback's committed listing retains the commit ID as a file blob, the diffs need name nothing, but `disk_tree` lists no file at that path.
In branch mode a gitlink commit absent from the superproject's object database also makes the existing `_texts` ask `cat-file` for an object it cannot read, whereas the exact committed-tree reader represents the non-blob as empty text.
This was already demonstrated in the requested Task 8b review; RAW-1's happy-path tests cannot repair the retained fallback or branch path.
Fix: carry A4 into Task 8c's new committed-listing abstraction explicitly, preserving entry kinds and matching the exact readers' treatment of non-blobs in each mode.
Add the empty/uninitialised submodule, populated submodule, and absent submodule-object tests, and compare with the exact readers rather than Task 8b's eager implementation alone.

## Task 8c's index-race fix

For the specific `measure/race.py` interleaving, the proposed before/after key is the right correction on a filesystem where replacing the index changes that key.
I reproduced Task 8b's miss on a copied `s900`: edit already on disk; `diff-index` returns no changes; injected `git add`; `diff-files` returns no changes; the fast listing misses the edit.
The index key changes, and retrying the identity sees the edit.
A small direct pair probe in both command orders also rejects the mixed pair when staged between them (`scratch/race_review.py`, `scratch/race-review.txt`).
This covers an ordinary `git add`, `git reset`, flag update, or other atomic index replacement during the group, regardless of which child process finishes first.
Starting the commands together alone would not fix it; rejecting the mixed result does.
The implementation must pin commit IDs, take the key before starting any member and after collecting all results, discard the entire group's dependent flag/conversion results on retry, and give `listings()`/`texts()` the same exact fallback state when all attempts are unstable.
Reversing the two calls on retry is not a substitute for that key or fallback.
A stable raw-index key does not certify validated entries (R6), file content (R4), conversion history (R11), or source stability (R1).
On coarse timestamps with inode reuse an ABA index replacement may repeat the stat tuple; no pure stat key is a universal content snapshot.
For supported normal atomic index replacements I found no additional way for `git add` itself to evade the whole-group recheck.

## Sequential measurement rerun

Commands used the supplied `/var/tmp/lodge-plan-fix6/venv/bin/python` and the existing native `/var/tmp/lodge-bench/s90000` in place.
Each timed subprocess was run one at a time; I did not rerun the overlapping `run_many` group, so I do not claim to reproduce its 44.2 ms wall time.
All generated indexes and SQLite databases are under the review scratch directory, with `GIT_INDEX_FILE` for Git writes and `--info-only` when hashing working-tree paths.
The normal real-index reads set `GIT_OPTIONAL_LOCKS=0`.
A scratch global configuration holds only `[core] autocrlf = input`; the isolated runs use `/dev/null`.
Best of nine unless stated otherwise; times in milliseconds.

| Measured piece | Plan fix 6 | Rerun best | Rerun median / qualification |
|---|---:|---:|---|
| Python `-c pass` | 18.0 | 18.57 | 19.28 |
| Python `-c 'import lodge.main'` | 142.3 | 147.48 | 152.47 |
| `lodge --version` | 165.7 | 155.50 | 158.57 |
| `lodge guide --read` | 172.6 | 158.58 | 163.15 |
| New-object identity, isolated | 785 | 800 | best of three: 800, 830, 811 |
| New-object identity, autocrlf input | 3,148 | 3,192 | best of three: 3,215, 3,224, 3,192 |
| Raw-index build, stdin, no attachment entries | 1,152 | 1,136.59 | one build; 21,734,784 bytes |
| Raw `diff-files`, production-shaped index | 39 to 54 | 44.03 | 50.31; output empty |
| Raw `diff-index`, production-shaped index | 12.5 | 50.78 | 52.12; output empty |
| Raw `diff-index`, HEAD-seeded control | 12.5 | 12.21 | 14.72; 13.50 best with exclusion |
| Small Git operations individually | about 1 to 3 | 1.65 to 1.90 | rev-parse 1.90, merge-base 1.73, config 1.65 |
| SQLite lock/connect/pragmas/state/bucket/parse | 2.6 | 2.7 to 2.9 | same 166 MB synthetic row layout, two runs |
| Installed-package digest | 2.2 | 2.2 | same 315,994 source bytes |
| Folder-row hit, 2,252 folders | 6.4 | 6.4 to 6.7 | no stale folders or extras, two runs |
| Python full-path file `lstat` | 389.3 | 388.1 | best of seven |
| Relative-to-open-folder file `lstat` | 358.6 | 352.1 | best of seven |
| SQLite per-folder stat cache, complete hit | 405.8 | 405.3 | best of seven |
| CLI floor + two raw diffs + rev-parse + merge-base, sequential | unmeasured as one process | 265.68 | 285.73; no lazy imports, app work excluded |
| Full-overlay `diff-index` at 160,800 entries, model | unmeasured | 175.01 | 182.24; 27.1 MB output |
| Full-overlay Python parse / sorted ident, model | unmeasured | 93.36 / 57.46 | separate best-of-nine components |

The startup results are near the reported scale but not identical: this run imports about 5 ms slower, while version/guide run about 10 to 14 ms faster.
The material non-reproduction is the production-built raw index's `diff-index`, explained by the cache-tree control in R8.
The no-attachment input still has 160,800 entries: this benchmark has no attachment files to remove.
The full-overlay model is separate from the actual clean-disk timing; no claim of end-to-end indexed-command timing is made for either.
Reproduction scripts and raw outputs are named in the findings and under `/var/tmp/lodge-review-pf6/scratch/`.

## Is 0.3 s seen reachable without LAZY-1?

For a clean LF checkout on native disk with a usable, sound raw cache, it remains plausible.
A real unmodified CLI startup/guide dispatch plus four sequential Git operations is 265.68 ms best; adding the independently measured folder rows, SQLite hit, and digest gives about 277 ms before the unbuilt indexed-app work.
That deliberately sequential estimate leaves only about 23 ms at the best and about 3 ms at the median.
Overlapping the two diffs and small calls as proposed could recover roughly 40 ms in the clean case, which makes a roughly 0.24 s subtotal credible, but this review did not measure that overlap or the correctness fixes' cost.
There is therefore no evidence that the structure exception LAZY-1 is necessary for this narrow clean workload.

For the plan's general “seen” claim, no: the current all-CRLF algorithm already exceeds the target before Python parses its full raw diff (R12), and the filesystem/writer cases in R1/R4/R5 cannot be solved by importing fewer modules.
Neither “0.23 s without LAZY-1” nor “under any autocrlf” is an established end-to-end result.
Keeping the structure rule is a reasonable coordinator choice; implement and measure the necessary identity/correctness changes first, retaining Task 12's stop.

## Configuration, worktree, and boundary assessment

- The explicit `core.trustctime=true` and `core.checkStat=default` overrides are necessary and work for ordinary writes: a probe with repository `trustctime=false`, `checkStat=minimal`, and `fileMode=false` still names a same-size rewrite with restored mtime.
- Leaving `core.fileMode=false` in effect does not itself lose raw bytes: executable permission changes are irrelevant to the exact blob identity, and `core.symlinks=true` keeps file/symlink kind changes meaningful.
- A normal hardlink-alias write with restored mtime is detected through shared inode ctime; a plain symlink's raw target hash is correct (`scratch/extra_probes.py`).
- Static worktree attributes with a real clean/smudge filter, `text`, `eol`, and `working-tree-encoding` are ignored by the proposed empty attribute source in the direct probe; a static global attributes file is suppressed by `core.attributesFile=/dev/null`, and system attributes by `GIT_ATTR_NOSYSTEM=1`.
  Those settings do not suppress `info/attributes`, as R1 proves; the claim that content comparison never runs is also too strong for clock skew, old persisted entries, or a Git build with different timestamp precision.
- A fresh private index in a sparse checkout did not inherit skip-worktree flags in the probe: an out-of-cone file was tagged `H`, and its edit was named.
  Retain sparse-index coverage and reject unexpected sparse-directory/flag entries rather than assuming the property forever.
- Linked-worktree discovery is correct in principle: the probe resolves a distinct absolute git dir under `.git/worktrees/...`, with the shared common dir and shared `info/attributes` in the main git dir.
  The filter probe confirms that shared attributes still affect `update-index` there (`scratch/probe.py worktree`).
  Resolve the shared attribute path through Git, not by appending `info/attributes` to the per-worktree git dir, and never share a raw stat index between worktrees.
- Missing `--attr-source` must take the safe fallback, with the corrected capability/version annotation in R10 and the provenance fix in R11.
- The proposed amendment correctly keeps the gate, `add`, `trees()`, branch-mode identity, and the viewer off RAW-1.
  Wire it only into the five indexed reads and add tests that poisoned raw entries and an unusable raw index cannot affect gate/add results; both must still hash the exact working-tree bytes.
- The module placement, front doors, pure core/app clock rule, and conditional nature of Part B respect the structure rules on paper.
  No lazy import or rule-table exception is authorised until the author's LAZY-1 decision exists.
  RAW-1, STOP-2, and FOLD-1 are explicitly proposals, not recorded rulings; d-q0tb8r/d-7e8zhd must remain binding when they are recorded.
- The proposed property test's removal of root attributes addresses the old masking problem on the raw path, but advancing only `time.time_ns()` by three seconds does not advance actual file/index timestamps coherently with F2.
  Add the real-clock mmap regression and explicit coarse/delayed timestamp models instead of treating that fake-clock test as the racy proof.

The review worktree still resolves to 83ef70b; final `git diff --exit-code` and `git status --porcelain` are clean.
No commit or push was made.

## Verdict

Task 8c's whole-group index recheck is worth keeping and closes the demonstrated ordinary `git add` race.
The raw-index approach as specified cannot be accepted under the existing exact-tree contract: R1 and R4 are reproduced stale-blob failures, with additional publication, link, conversion-provenance, and recovery problems.
The broad performance conclusion also needs revision because the clean benchmark omits full raw overlays in a common CRLF checkout.
Rework RAW-1's isolation, validation/publication, recovery text source, and persistent identity representation, explicitly resolve the permitted writer/filesystem contract, then measure the resulting implementation without LAZY-1 before considering a structure exception.
Keep the gate/add exact-byte boundary and Task 12's stop throughout.

**Verdict: reject.**
