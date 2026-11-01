# Adversarial review of plan fixes 6b and 7

Status: complete. Target: detached 094e9cef866769de115da18a485f05698f98e737; tracked files remain unchanged. All new probes and copied stores are under `/var/tmp/lodge-review-pf6/scratch/67`. No command runs in, or writes to, `/var/tmp/lodge-build`.

Binding rulings: no RAW-1 or private stat cache, no LAZY-1, conversions read every file and are reported separately, gate and add exact, changed target remains 3 s. Both STALE-1 branches are reviewed; no ruling is inferred from elapsed time or performance.

Measurements distinguish a measured prototype/stage sum from an implemented command. Final verdicts are at the end.

## Findings

### F1 Blocking: joined decoding can silently associate a parse with another key

Where: `tasks-7.md:18-23`, Task 9c Interfaces and Step 1 (`test_one_bad_value_is_one_miss`); `measure-7/phases.py`, joined-decoding lever.
Failure: one stored value is `null,null`, invalid as a standalone JSON value. Joining it into the array succeeds, so the specified fallback on a `json.loads` error never runs. Zipping rows with decoded values makes the first two keys `None` and shifts all later records by one key. Validators accept the records, since their shapes are valid. The gate and add also use this lookup, so this violates the exact parse-cache boundary.
Probe: `scratch/67/probe_scan.py` and `probe_scan.txt`: 1,500 rows produce 1,501 values without raising; the candidate differs at all 1,500 keys, whereas today's per-key reader makes only the bad key a miss.
Fix: validate that each decoded element belongs to exactly one stored JSON document before assigning keys; at least reject a cardinality mismatch and fall back per key, and prove boundary isolation for malformed individual documents (or retain per-value decoding). Add joined-success corruption cases, not only a truncated value. Retain per-element exception isolation for `from_plain` too.

### F2 Important: token-only citer deltas miss changes in ordering

Where: `tasks-7.md:41-47`, Task 10a amendment 4 and amendment 7's property test; `plan-fix-7.md`, DELTA-7.
Failure: two unchanged entries cite TARGET-1. A new decision edits the older entry and makes it the newest citer, without mentioning TARGET-1 in its own title or statement. No changed parse unit has that token, so its citer row is copied unchanged. Full `core.citers` orders by an entry's newest decision date and reverses the order.
Probe: `scratch/67/probe_checks.py` and `probe_checks.txt`: order changes from `(s-007000, s-006000)` to `(s-006000, s-007000)`, both entry objects shared, new decision's tokens lack TARGET-1. With more than ten citers, merely re-sorting an already limited result also selects the wrong records. Line 43 may intend safe query-time sorting, but it does not replace the existing newest-first `Index.citing(..., limit)` contract with unordered memberships or specify sorting the entire current candidate set before limiting; that interpretation must be explicit and tested.
Fix: either keep unordered memberships and rank the complete relevant set against current state rows before limiting, or invalidate/re-sort every token row whose member's date/ID ordering input changed. Also handle family exclusion and moving a code at query time against the new state's code map. Require deterministic ordering-only cases in the full-build differential test.

### F3 Important: the measured scoped-check prototype drops unchanged context needed by check 4

Where: `measure-7/scoped.py:71-76`, Task 10c amendment 3 (`tasks-7.md`); the 0.112 s equality claim.
Failure: add a decision with CREATE for an existing, unchanged entry. `touched` is empty; the prototype's reduced published snapshot contains no entries. `check_entries` therefore cannot report that CREATE names an already existing entry. The old body reports check 4, the prototype reports nothing for it. Skipping an entry's own comparison is safe only if the full entry maps remain available to checks of new decisions.
Probe: `scratch/67/probe_checks.py` extracts and executes only the supplied prototype function; `new CREATE of existing shared entry equal False`, missing `lists create for ... which already exists`.
Fix: retain full before/after context while scoping iteration; separate entry comparisons from new-decision validations. Re-measure the corrected form. Add explicit failing CREATE/LINK/import cases with unchanged referenced entries; general random pairs alone do not establish this proof.

### F4 Important: shared bucket lifetimes are shorter than a delta build's lifetime

Where: Task 10a amendments 2, 3, 5 and 7 (`tasks-7.md`); existing `keep_state` epoch recovery in the plan, lines 505-514.
Failure: A reads newest state S0's facts/listing/bucket digest map, ends the read transaction, and builds a delta. B keeps four states and evicts S0, collecting a bucket only S0 named. A then copies S0's digest into its new map. The epoch has not changed, but the bucket no longer exists. A clear between base lookup and keep loses all the base's payloads too; the old epoch recovery only replays parses and facts, not these new shared payloads. The new state is incomplete. Existing miss handling saves the printed answer by falling back, but the promised complete keep fails and repeated readers can rebuild indefinitely.
Probe: `scratch/67/probe_base_lifetime.py` / `.txt`, two WAL connections, sequential transactions following the specified lifetime: epoch unchanged, A maps bucket 0 to h0, joined payloads empty.
Fix: bind the delta to one explicit base key, epoch, facts, listing, and digest map obtained in one read snapshot. Inside the write transaction verify every referenced payload still exists; if any is gone, skip keeping or rebuild from a full result, including after the writer's own cap-triggered clear. Never select a different "newest" base at keep time for a delta computed against an earlier one. Add interleaved different-state keeps, eviction of the selected base, both cross-process and own-clear cases, and re-keeping the selected base with different rows. `test_shared_bucket_survives_eviction` only tests a bucket already referenced by committed states; it cannot catch the building reader's gap. Add the base/delta interface explicitly; the unchanged full-row `keep_state` signature does not specify this protocol. Amend Global Constraints invariants 2 and 3 to distinguish owned map rows from the new shared payloads and their collection; leaving all buckets described as state-keyed own rows contradicts this design.

### F5 Important: the oracle can share the helpers it is meant to test

Where: Task 10c amendments 2 and 4 (`tasks-7.md`), `tests/core/oracle_check_change.py` copied from the base while production changes `check_entries.py` and `check_immutable.py`.
Failure: copying `check_change.py` preserves `from lodge.core.check_entries import check_entries` and `from lodge.core.check_immutable import check_immutable`. Both candidate and oracle then call the rewritten production helpers. A lost check inside either helper affects both equally, and the claimed equality test passes. A copied function body alone does not freeze its transitive dependencies.
Probe: `scratch/67/probe_checks.py` copies the old module body into a separate test module after replacing the production entry helper with an empty iterator. The copied oracle imports that rewritten helper, and candidate equals oracle while both omit the CREATE problem. This demonstrates coupling; it is not a run of the unbuilt property test.
Fix: freeze all bodies being rewritten and their required constants/helpers under test-only names, with no import back into modified production logic. Cover facts/no facts, shared/deep-copied records, non-None `current`, problems and ordered notes. Plant omissions in check 4, decision/thread immutability, and the scoped outer body and require the equality tests to fail for each mutant.

### F6 Important: comparison-dependent failing IDs cannot be immutable facts keyed by current ident alone

Where: Task 10a amendment 1 (`tasks-7.md:32-33`), `StateFacts.failing`; original Task 10a `StateFacts` at plan lines 484-487, Task 10c facts keyed by ident alone.
Failure: `State.failing` includes `check_change` problems, so it depends on the published snapshot (and for dates on time/current). The same current tree compared with an older published decision flags an illegal rewrite; compared with itself it does not. An immutable `StateFacts` row keyed only by that current ident can store only one of those failing sets. Delta comparison against that row can reuse wrong `fails check` flags, including an entry's `decision fails check` flag.
Probe: `scratch/67/probe_checks.py`: the identical current snapshot has failing `{d-00c000}` against the older publication and the empty set against itself.
Fix: retain only snapshot-intrinsic facts (`Derived`, `check_state` problems) under the current ident. Store the final failing set with the full stored-state key and validity interval, and select that exact base's set for deltas. Distinguish both explicitly; using check_state-only failing IDs for row construction is also incorrect. Add the same-current/different-published case to the differential test.

### F7 Important: the target amendment still offers the rejected 4 s target

Where: `plan-fix-7.md:12` and its “Decisions needed / TGT-7” paragraph; `tasks-7.md:67`, Task 12 amendment 1.
Failure: the build brief still says TGT-7 is needed before Task 12 and permits a 4 s target “if recorded”, although the coordinator has ruled no TGT-7 and kept 3 s. Following that stale branch would turn the measured miss into a pass against a different target.
Fix: remove the TGT-7 request and conditional 4 s branch. State unconditionally that Task 12 measures against 3 s and records the miss with its phase table and stop. The measured evidence may remain; it does not authorise changing the target.

### F8 Important: merging a descendant code's ancestor citer rows changes exact-token semantics

Where: `tasks-7.md:43`, Task 10a amendment 4 (`show CODE` reads its row and its family roots' rows).
Failure: `show A-1.child` includes an unrelated record citing only A-1 if the ancestor rows are unioned and only the family is excluded. `core.citers(..., 'A-1.child')` returns no such record; it matches the queried token exactly. Excluding coded family members does not exclude unrelated root-only citers. `code_tokens('A-1.child')` itself returns only `a-1.child`, not `a-1`.
Probe: `scratch/67/probe_checks.py`: root citers `(s-00f000,)`, child citers empty, outsider outside both code families.
Fix: use the exact queried token's membership row and exclude that query's current family. A family-root query uses the root's own row. If the extra ancestor reads serve some other purpose, specify that they never contribute non-matching citers. Add indexed-versus-memory output checks for descendant codes and root-only citers; comparing only the stored rows will miss a lookup union bug.

### F9 Important: the delta property test omits the input transitions that distinguish it from full rebuilding

Where: `tasks-7.md:46-47`, Task 10a Step 1 amendments; existing Task 10a concurrency tests were designed for complete per-state rows.
Failure: the listed edit generator has no rename, date edit, code transfer, area metadata/order change, statement-only token edit, publication-baseline change, alternate newest kept base, or clear/eviction between selecting and using a base. Thus 300 passing sequences can miss F2, F4, and F6, and correct membership rows can still miss F8's lookup error. “Each step” does not specify a sequence length, durable reload, or that the implementation under test actually took a delta.
Fix: require deterministic cases for those transitions and seeded sequences with several steps, deleted paths/records and duplicate-ID winner changes. Exercise the actual keep, close/reopen, and indexed outputs against independent full construction. Force bases other than the preceding edit; inject an interleaved keep and clear before use. Assert both that equality holds and that the delta path was taken (a full-rebuild-only implementation must fail the work-count checks). Mutate one invalidation edge, old-token removal, base selection, and bucket deletion separately and require each mutant to fail. The full-build oracle must construct all rows and citer memberships independently of the dirty-set helper.

### F10 Minor: O_NOFOLLOW alone does not make the new reader safe against a raced special file

Where: `tasks-6b.md:40-44,58,67`, Task 8c `disk.py`, Links, and Step 1; inherited static `test_fifo_agrees`.
Failure: the reader observes a regular file, it is replaced with a FIFO before `open(..., O_NOFOLLOW)`, and the open blocks waiting for a writer. An `fstat` after opening cannot prevent that block. The new descriptor-relative reader is also used by the gate and add. The planned link-swap test does not exercise the regular-to-FIFO interval.
Fix: spell out a nonblocking open plus descriptor type validation (`O_NONBLOCK`, then `fstat`; consume bytes only for a regular descriptor), preserving empty text for special files and using relative `readlink` for a link. Add a deterministic regular-to-FIFO swap between classification and open, with a bounded child-process test. This is a missing hardening/test requirement, not a claimed failure of an implementation of `disk.py`, which does not exist in the reviewed build.

## 6b closure of the previous R1-R13

These are plan-level closures. Task 8c and Task 11 are unbuilt at 094e9ce, so no claim below substitutes a model for an implementation regression test.

| Earlier finding | Disposition in 6b |
|---|---|
| R1 transient `info/attributes` poisoning private raw entries | Removed with RAW-1 and Task 11b. No conversion-producing private index remains. |
| R2 unavailable `--info-only` blobs on recovery | Removed with RAW-1. Exact fallback additionally must retain its read bytes for later `texts()`, which line 54 now requires. |
| R3 folder links / attachment ancestor links | Addressed explicitly in Task 8c lines 40-44 and 58 and Task 11 lines 90-94: parent-relative O_NOFOLLOW/O_DIRECTORY traversal, a reachable-real-folder set, prune descendants when a parent changes kind, no overlay read through an unreachable ancestor, and real exact-reader comparisons. The static outside-link and within-attachment cases are named, as is the pre-entry swap. See the new special-file hardening F10. |
| R4 writable mmap / raw stat admission proof | The private-stat proof and admission scheme are withdrawn. Git's own index observations remain the accepted limitation already documented in 6b; I do not reinstate the rejected RAW-1 discussion. R11-A reads bytes, while R11-B retains Git's observation limits. |
| R5 unsupported filesystem/clock claims for a private stat cache | That new file-stat cache is gone. FOLD-1 retains the separately existing directory-signature contract d-8kq2nk; it is not evidence for adding another file-stat cache. |
| R6 publication of unvalidated private entries | Removed with RAW-1; no separate refresh/validation/publication protocol remains. |
| R7 stealing an aged Git lock | Removed with Task 11b. No ten-minute age-based lock deletion survives in the replacement tasks. |
| R8 production raw-index construction differs from the timing fixture | Moot without that raw index. 6b times the real index calls instead; the seen prototype is re-run below. |
| R9 wrong conversion fallback estimate | Corrected to about 3.4 s, with 3.148 s identity, in the 6b table. It is a separately reported configuration. |
| R10 wrong Git minimum version for `--attr-source` | Moot: that option and capability gate are removed with RAW-1. |
| R11 removed conversion provenance | Explicitly unresolved, not silently declared fixed. Both rulings have task text and tests. The output divergence is real and reproduced below. |
| R12 steady CRLF raw overlay cost | Removed with the raw overlay design; conversions now pay the byte-reading cost and are reported separately. The unconverted seen target cannot be advertised as a conversion result. |
| R13 gitlinks on checkout and branch paths | Addressed explicitly: retain entry kinds; every non-blob base path enters the checkout overlay even if Git ignores submodule changes; disk supplies absence/descendants; branch text is empty without requesting an unavailable submodule commit. “Read_tree's representation” must include its empty-text blob key (`blob_id(b'')`), not the commit ID. The named tests compare against exact readers. Add an explicitly absent checkout submodule alongside the empty/populated cases when implementing. |

The index-file race fix is now stated correctly at `tasks-6b.md:54,66`: pin revisions, take `(ino,size,mtime_ns,ctime_ns)` before starting the whole git group and after collecting every result, discard the entire group and dependent flags/conversions on mismatch, retry twice (three attempts total), then make identity, listing, and texts come from one retained exact disk tree. It no longer merely declines to cache an answer built from a mixed pair. This closes the earlier ordinary `git add` race under Git's atomic index replacement protocol. The continuous-change test must force the final fallback and then call both listings and texts, not just compare an identity string. No private Git lock may be deleted by age as a side effect.

A small descriptor model in `scratch/67/probe_fd.py` verifies the proposed mechanism: an ancestor link makes the child inaccessible, a leaf link yields only its target string, and the attachment ancestor link is inaccessible. It also reproduces F10's blocked O_NOFOLLOW-only FIFO open in a killed child process and shows the nonblocking/type-checked result. This is supporting evidence for the design, not a run of the unbuilt `disk.py`.

## R11 / STALE-1, both branches

I re-ran `measure-6b/r11_probe.py` against 094e9ce's code, using only its interpreter/dependencies from the native venv and a new scratch copy of s900 (`scratch/67/r11`). The corrected CLI launcher propagates exit status. Output is `scratch/67/r11_probe.txt`.
The exact rerun matches all reported counts: CRLF decision/entry/area/thread/every-file changes only the gate; ident decision 6/15 commands; ident entry 7/15; UTF-16 decision 15/15; length-preserving filter 8/15. The test changes disk texts to compare outcomes; it does not itself establish a stat-clean Git index history. The separate provenance probe below tests that history.

- **R11-A / STALE-1 answer B:** reading and hashing every working-tree file through the safe reader closes the provenance issue. It must enumerate disk files even without conversion sources, including files Git considers stat-clean. Full-byte cost remains on every read; the targets are measured and missed, then reported by Task 12. No stat cache or target change follows from selecting this branch.
- **R11-B / STALE-1 answer A:** this explicitly permits the demonstrated output difference for stat-clean conversion history. It does not make the fast path exact and must be recorded as the stated exception to d-dqpf59/d-rs76ks before use. Test removed ident, encoding, and length-preserving filter histories as well as CRLF; size comparisons cannot recover exactness. Gate, add, and the other exact readers remain byte-based. The ordinary Git-index mmap limitation is not repaired by an index-file stability check.

The “A/B” labels are reversed between 6b's R11 names and 7's STALE-1 names, but `plan-fix-7.md:78` maps them explicitly and correctly. Implementation briefs should carry the full ruled sentence, not just a bare A or B.

Further direct evidence: `scratch/67/probe_gitlinks_history.py` / `.txt` uses a synthetic unavailable gitlink commit `111...111` and `diff.ignoreSubmodules=all`. The unbuilt-fix baseline fails for empty/populated checkout submodules and requests the missing commit in branch texts; applying just 6b's kind-aware overlay rule in the model matches the exact reader for absent, empty, and populated folders. Branch `read_tree`'s key is `e69de29b...` for empty text, as required. This is why the checkout and branch treatments must differ.

The same script recreates a real ident-smudged file, ages it, stages it, removes its untracked attribute source, and takes a fresh `CheckoutIdentity`. Result: expanded ident present, index key unchanged, `diff-files` empty, fast blob differs from disk blob. Thus R11 is not merely a constructed pair of texts or a line-end-only concern. Both its provenance and its output consequences reproduce on the new build.

## What can be proved equal, and what still needs a stronger test

For the **row** delta, the proposed dependencies are broadly a safe over-approximation if implemented as actual input dependencies: old and new records of the union of differing paths; added/removed map keys and changed values; symmetric differences of set-valued `Derived` fields (including `awaiting_author`); final failing IDs keyed by the full state; then newest-decision dependants and link/rests_on dependants. Compute the dependant additions in that order using old/new relationships where needed. Compare against one selected, retained base, not the most recent in-memory snapshot or a newly selected database state. Rebuild a dirty bucket's complete contents, removing dead IDs; a dictionary update alone leaves removed records behind.

Renames must change `Row.key` even if the content blob is unchanged. Retirements and replaced/narrowed/confirmed decisions affect reverse maps and link target statuses; those invalidate both the record and its dependants. An area order/rank edit does not itself change a Row field; the new state's answers/notes are nevertheless rebuilt and checked, rather than copied with buckets. Moving a code requires the new state's code/family map, without rescanning unchanged text. Statement-only citer edits remove old memberships as well as add new ones. Text-token membership is unit-local; ordering and family exclusion are state-dependent (F2, F8). None of this requires reintroducing a file-stat cache or skipping full derive/check_state.

For **scoped check_change**, the proof obligations are:

| Part | Equal skip rule / required context |
|---|---|
| Checks 1, 2, 3, 7, 8 from `after_problems` | Keep the same facts, problem-key classification, notes, and final sorting; do not substitute delta-local problems. |
| Missing records (check 2) | Difference of the unions of all three record ID sets, then sort, preserving `problem_at(published, ...)`. Per-kind differences are not the old union rule for arbitrary Snapshot pairs. |
| `_dates`, `_imports_over_live` (check 1) | With no new decision, both yield nothing. Otherwise run the original logic against full published context and pass through `current`, including its date constraints and already-held IDs. The timing prototype hardcodes `None`; the new public body must not do so. |
| Entry comparisons (check 4) | Shared entry plus unchanged retired-or-not status cannot emit an own-entry problem. Keep full entry context for new-decision CREATE/LINK and import-source checks; F3 is a counterexample to reducing that context. |
| Decision/thread immutability (check 5) | Same immutable record object implies equal compared fields/messages. Non-shared objects still require all old field and closed-thread rules; different paths must still be used for emitted problems. |
| `_links_to_dead` (check 6) | A shared entry adds no new rests_on target. New decisions still need all original published/standing status maps, their complete changes, and the existing target records. |
| Area notes | Compare the full area maps and preserve the original name/field order, including order/rank-only changes. |

The algorithm can be made exact without sharing: copying every record only removes the skips. But the supplied benchmark pair and a self-coupled oracle do not prove that result. In particular, the gate uses this same body, so F3/F5 must be fixed before claiming full gate semantics by proof.

For **Task 9c**, one rowid-ordered SELECT inside the existing explicit read transaction is sound with immutable parse units and clear-in-place: a concurrent clear commits a new WAL version, and the reader finishes on its own snapshot. Match full `(path,blob)` tuples, carry the filtered rows and decoded elements together, and return a dictionary; rowid order need not match request order. Duplicate request keys and stale blobs are harmless under that rule. The current adapter already wraps `find_parses` in `BEGIN ... COMMIT`. Preserve that wrapper, per-element validator exception handling, and None-as-a-hit semantics. The unsound part is joined document boundaries (F1), not scanning or WAL ordering. A clear after a state keep but before indexed use is likewise safe only through the existing state-row/missing-payload miss and whole-read fallback; after a read transaction starts, its WAL snapshot preserves the old complete state. The immediate changed read should answer from its in-memory result as planned. Do not treat a remembered successful keep as proof that digest payloads still exist in a later transaction; extend those fallback tests to shared buckets/citer payloads.

A cardinality check alone is not a full corruption proof: stored fragments `null,"foo` and `bar"` join to `[null,"foo,bar"]`, with the same number of elements as rows, even though both standalone values are invalid. The first key falsely becomes a None hit. This second case is also in `probe_checks.txt`. A safe first implementation can retain the scan and per-value `json.loads`: its measured penalty is only about 33 ms here.

## Timing rerun on the new build

All timings below use 094e9cef's package copied unchanged to `scratch/67/build/lodge`, compiled with normal native-disk bytecode, and imported through explicit `PYTHONPATH`. `/var/tmp/lodge-plan-fix6/venv/bin/python` supplies only CPython 3.13.5 and the same dependencies: PyYAML 6.0.3, libyaml 0.2.5, SQLite 3.47.1; Git 2.56.0. No older lodge package is imported. `phases.txt` prints the source location. No timing jobs overlap each other; individual Git calls inside the planned seven-call group intentionally overlap as that design requires.

The reference `/var/tmp/lodge-bench/s90000` is read-only throughout. For changed-state phases I read its exact trees once, append the benchmark edit to the same `s-01z2c4` file's text **in memory**, recompute that file's blob hash, and populate a fresh scratch parse index with this build. This gives 160,800 keys, 160,801 cached parse rows, one differing path, 158,550 records, and 158,549 objects shared with published. Only synthetic s900 copies are edited on disk. This rerun measures the same phase workloads, not a completed changed CLI call or the time to write that edit to disk.

| Claim | Rerun | Assessment |
|---|---|---|
| Seen prototype 0.273 s best, 0.278 median | **0.243048 s best, 0.252974 median**, nine fresh processes | Faster here. The real seven Git calls, unchanged index key, 2,252 folder stats, digest and scratch state/bucket hit run. Rendering, printing, and application row reconstruction still absent. The scratch state/bucket fixture retains the supplied marshal prototype layout; 7's content-addressed JSON layout is not benchmarked by this process. |
| `derive` 0.994 s | **0.9897 s**, best of three | Reproduces. |
| `check_state` 0.569 s | **0.5683 s**, best of three | Reproduces. |
| Parse scan 0.189 s | **0.1951 s** | Close. Full `(path,blob)` filtering over 160,801 rows. |
| Joined loads + validated decode 0.838 s | **0.8320 s** | Close on valid rows; F1 invalidates the corruption equivalence. Per-value JSON loads 0.3152 s versus joined 0.2824 s. |
| Full per-key lookup/decode 1.413 s | **1.4330 s** | Close; includes validators. |
| Assemble 0.149 s | **0.1458 s** | Close. |
| Published snapshot substitution 0.152 s | **0.1430 s** | Close; equal parses shared by identity. |
| Published facts load 0.029 s | **0.0285 s** | Reproduces. |
| Scoped `check_change` 0.112 s | **0.1128 s**, full body with facts **0.8950 s** | Both reproduce on the benchmark pair. Equality there reproduces too; exactness on other inputs does not (F3). |
| Failing IDs + unrecorded problems 0.070 s | **0.0647 s** | 0.0268 + 0.0379. |
| Delta row estimate 0.328 s | **0.3304 s**, plus **0.0002 s** bucket rewrite | 0.0983 decode + 0.1737 dirty set + 0.0584 encode. One record/bucket, as reported. The prototype still omits the general link-neighbourhood work and complete Row construction. |
| Changed “best exact” 3.836 s | **3.8165 s reconstructed stage sum**, retaining its 0.406 s fixed-stage estimate | Numerically close; **not reproduced as an end-to-end exact read**. Its joined decoder and scoped checker are not exact as supplied, and answers, FTS, full Row/link work, state maps/code/citer metadata, corrected invalidation, and their persistence are not fully timed. |

The new seen subtotal plus separately measured committed mapping (0.144944 s, including a tree-ID rev-parse) gives an alternative approximate fixed-stage term of 0.387992 s. Substituting that yields **3.798492 s** for the same incomplete sum. It is another composite estimate, not a runnable changed command. Its first five stages total **3.118892 s**, versus the report's 3.145 s; retaining the old fixed term gives 3.1369 s. Thus the measured miss remains under either treatment of fixed stages, before restoring the omitted work. A safe per-value decoder adds only about 33 ms here and does not change that conclusion.

The claimed “best exact” qualification does not reproduce; a roughly 3.8 s sum of the named prototype stages does. The evidence supports recording a miss with the currently listed full derive/check_state design, not changing the 3 s target and not an impossibility claim about all future exact implementations. R11-A adds the full-byte identity cost; neither branch makes these dependent prototype shortcuts exact by itself.

Raw timing outputs: `scratch/67/seen-native-normal-pyc.txt`, `phases.txt`, `levers.txt`, `scoped.txt`, `dirty.txt`, `rows.txt`, `fixed_stages.txt`, `keepfacts.txt`. Source scripts beside them show the adaptations. The initial diagnostic runs with `PYTHONPYCACHEPREFIX` were much slower at imports (about 0.43 s total); they are retained as `seen.txt` and `seen-native-venv.txt` but excluded from like-for-like compiled-package comparisons.

Additional byte-read reference (`scratch/67/exact.txt`, best of three, same read-only s90000): current `disk_tree` **3.635901 s** (median 3.641963), and one `git hash-object --no-filters --stdin-paths` process plus path mapping **0.959469 s** (median 0.960662). These are reference algorithms, not timings of the unbuilt hardened reader or a rerun of 6b's autocrlf identity routine. The advertised 0.855-0.900 s C-hashing range does not reproduce here. It is also not a proposed exact reader for symlinks/FIFOs. Both references remain far above the seen budget before application work.

I also repeated the original Git-index race probe on a fresh scratch s900 (`scratch/67/race_review.py` / `.txt`): old Task 8b misses the edit when git add lands between diff calls, the index key moves, a fresh retry sees the edit, and the before/after guard rejects the mixed pair in both diff-call orders. The 6b text's final retained exact-tree fallback is the necessary additional rule after bounded retries; it is not present in 094e9ce and has not been represented as an implementation test here.

Final worktree check: `git diff --exit-code` and `git status --porcelain` are clean; HEAD remains 094e9cef866769de115da18a485f05698f98e737. No worktree commit or push was made.

## Scope, limitations, and verdicts

Read: the plan's Global Constraints and Tasks 8b-12, its brief, Task 9 review and recheck, the complete earlier R1-R13 review, both replacement task documents, both fix reports, their measurement scripts and outputs, and the implementation dependencies cited above. Decisions were read with `LODGE_INDEX=off uv run --frozen --quiet lodge show ... --reasoning`, including d-dqpf59, d-rs76ks, d-q0tb8r, d-8kq2nk, d-232gxs, d-26e6zj, d-c4w7xy, d-4j98ph, d-c6cegr, d-t3afj1, d-gvz66f, and d-e3stjn. The new probes exercise real core functions, SQLite ordering/lifetimes, Git on synthetic copies, and the supplied pure scoped-check prototype. No final Task 8c/9c/10/11 implementation or its proposed property tests exists in this build, so none is claimed tested. I did not run a full repository gate or mutate its tests.

Findings: **1 Blocking, 8 Important, 1 Minor**. F1 is the blocking parse/key association failure. F2-F9 concern delta/context/oracle correctness, the retained rejected target branch, and insufficient differential coverage. F10 is the new reader's special-file race hardening.

**6b verdict: accept with fixes.** Its withdrawal of RAW-1 and LAZY-1 follows the rulings, and the surviving R3/R13/index-race repairs are explicit enough to build. Add F10's nonblocking/type-check requirement and race test; carry the empty-text gitlink key and absent-folder case into the implementation tests. Implement the full chosen R11 sentence and its regression tests; neither an unresolved choice nor the 0.243 s subtotal is evidence that an exact seen command meets 0.3 s. Keep conversion reads reported separately and gate/add byte-based under both branches.

**7 verdict: reject.** The useful scan and shared-parse optimisations can stay, but joined decode can corrupt key association, the measured scoped check is not equivalent, its oracle can share rewritten logic, and the delta protocol has unresolved state-dependent citer/failing inputs and base lifetimes. Correct those contracts, strengthen and mutation-check the independent full-build/oracle tests, amend the shared-payload invariants/interfaces, and re-measure the corrected path. Keep **3 s** unconditionally; Task 12 records the measured miss and invokes the existing stop, with no TGT-7.
