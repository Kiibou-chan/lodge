# Feasibility and performance review

The plan needs changes before implementation.
Reviewed against the brief, planner report, all ledger decisions with reasoning, `lodge spec`, the code, and native-disk probes.
Scratch evidence is under `/var/tmp/lodge-review-feasibility-performance/`.
No implementation changes are made by this review.

## Findings

### F1: Important, checkout identity does not preserve the identical-state shortcut

Handle: Task 8, lines 307 to 313, conflicting with `src/lodge/gitstore/published.py:43` and `src/lodge/app/state.py:71`.
Scenario: a clean checkout uses `sha1(base, empty overlay)`, while its published state uses the raw Git tree ID, so the identities differ even when their files are equal, disabling Task 4 and falsely reporting uncommitted changes in the gate.
A staged edit reverted on disk also adds a redundant overlay entry, changing the identity without changing the files.
Verified with `identity_cases.py` in scratch: identical disk contents still produce a staged diff, and hashing the base tree ID gives a different ID from that tree.
Fix: define one canonical identity for both modes and the gate, remove overlay entries equal to the base, and test equality across clean, staged-then-reverted, committed, and published representations, including attachments whose bytes are deliberately not part of the snapshot.

### F2: Blocking, Git index flags can hide changed source files

Handle: Task 8 identity and its tests, conflicting with `src/lodge/gitstore/checkout.py:90` and `src/lodge/gitstore/checkout.py:110`.
Scenario: a tracked record marked `assume-unchanged` or `skip-worktree` is edited on disk, and both proposed diff commands return no path, while the folder walk sees a name already present in the base.
The old blob and stored state are then reused, hiding the edited record and its check failures, including from the parse-cache path used by the gate.
Verified in an isolated native-disk repository for both flags: `disk_tree` changed, `diff-files` returned nothing, and the cached diff returned nothing.
Fix: detect such index entries and always inspect their disk state, or fall back to the disk walk, with differential read and gate tests for edited and missing flagged files.

### F3: Important, the conversion recipe misses configured conversions

Handle: Task 8 conversion check, line 312, and Task 10 attribute-cache key, conflicting with `src/lodge/gitstore/checkout.py:115` and decision d-atsx8n.
Scenario: `core.autocrlf=true` produces a clean CRLF checkout whose five queried attributes are all `unspecified`, so the stated attribute-based selection adds no paths to the overlay and reads LF blobs instead of disk bytes.
The fast rejection also treats a configured `core.attributesFile` pathname as though it must equal `true` or `input`, and Task 10 keys the cached selection by attribute-file bytes without naming configuration values or file selection as inputs.
Verified for autocrlf and an external attributes file in `identity-cases.txt`, including empty `diff-files` output and unequal disk and blob bytes.
Fix: treat autocrlf as an explicit conversion rule, resolve every configured attribute source, include configuration and source identities in invalidation, and test configuration changes between warm reads.

### F4: Important, the superlinear work is not removed by the specified rewrites

Handle: Task 2, including its ten-line allowance for `derive.py`, conflicting with `src/lodge/core/derive.py:162`, `src/lodge/core/derive.py:242`, `src/lodge/core/doubts.py:44`, and `src/lodge/core/check_change.py:78`.
Scenario: thousands of decisions edit one entry, a valid dependency chain is long, or a change introduces many decisions against a large published state.
Replacing `.index` with position maps leaves a slice and full prefix scan per decision, `doubt_marks` traverses every entry's transitive dependencies even with no doubts, and `_dates` scans every published decision for each new decision.
Verified with GC disabled in `scale_shapes.py`: doubling a single-entry history from 2,000 to 4,000 to 8,000 decisions takes 0.169, 0.644, and 2.594 s for `derive`, an empty-doubt chain takes 0.218, 0.901, and 3.832 s, and doubling both unrelated old and new decisions takes 0.047, 0.193, and 0.783 s for `_dates`.
The existing synthetic stores distribute short histories and dependencies across thousands of areas, so their profile does not expose these cases.
Fix: precompute preceding eligible changes, propagate only actual doubts through reverse dependencies, index earlier decisions by the entries and explicit links needed by `_dates`, and add history, chain, and large-change shape probes with differential correctness tests.

### F5: Important, the deep-chain acceptance test misses crashes in the read path

Handle: Task 2's 5,000-entry chain test and Tasks 8 to 10's read equivalence, conflicting with `src/lodge/core/order.py:46`, `src/lodge/core/order.py:81`, and `src/lodge/app/reads.py:51`.
Scenario: a valid chain passes the new iterative cycle check, but `show` still builds its recursive dependency tree, and `spec` recursively computes the reading order.
Verified on a 2,000-entry acyclic chain: both `rests_on_tree` and `derived_order` raise `RecursionError`.
Fix: use iterative traversals for these public reads and exercise `show`, `spec`, and the viewer path on the same deep chain, rather than testing `check_cycles` alone.

### F6: Important, broad warm searches cannot meet the stated budget with the proposed candidate path

Handle: Expected cost table and Task 10's FTS candidates, buckets, and core ranking, conflicting with `probes/fts.py`, `probes/codec.py`, and `src/lodge/core/search.py:118`.
Scenario: the benchmark's ordinary `berth crane` search returns 107,247 candidates, requiring almost all state buckets and those records' parses before core ranks them.
The expected 0.01 s SQLite allowance covers short lookups, not this path.
Verified in `search-cost-native.txt`: scoring and sorting already materialised matching Level1 views takes 0.726, 0.727, and 0.723 s with GC disabled, before startup, identity checks, FTS, or decoding, while the FTS rerun independently returns the same candidate count.
The existing ranking supplies a measured cost floor for the specified word-scoring approach, although the future implementation itself cannot yet be timed.
Fix: probe a concrete bounded-result design before approving this architecture, such as stored query answers or precomputed posting weights and ranks with exact totals, and retain a differential oracle for all filters and ranking tiers.
If the coordinator instead accepts slower broad searches, record that target change explicitly rather than quoting the point-lookup estimate for every seen-state read.

### F7: Important, the proposed module ownership creates import cycles and an incomplete front door

Handle: Tasks 6, 8, 9, and 10, conflicting with `tests/structure_imports.py:73`, `tests/structure_imports.py:104`, `tests/structure_tables.py:5`, and `src/lodge/app/__init__.py:5`.
Scenario: `search.py` retains `Filters` but calls ranking typed with `Filters`, while `snapshot.py` retains `Snapshot` but calls listing's assembly typed with `Snapshot`.
The direct implementation creates ranking/search and listing/snapshot cycles, including when imports are under `TYPE_CHECKING`, because the structure checker walks every import.
The index types also need an explicit shared home, since putting Row and StoredState beside their builder in read_model and importing them into ports would create a ports/read_model cycle.
Tasks 9 and 10 also require `gitstore` to consume `Index`, `FileKey`, rows, and stored states without naming an update to the app front door, leaving a past-the-front-door import as the immediate alternative.
Verified with the repository's cycle and import checkers in `structure-contracts.txt`, while the unchanged source has no structure violations.
Fix: assign shared value types to explicit leaf modules, export adapter-facing types through `app/__init__.py`, list those moves in the affected task files, and run a skeleton import/strict-mypy preflight before handing the tasks to builders.
Keep marshal encoding inside gitstore, since the same checker rejects `marshal` in app as well as core.

### F8: Important, stored states do not contain the check facts Task 10 consumes

Handle: Task 10's `StoredState` and published-facts optimisation, conflicting with `src/lodge/core/check_change.py:35`, `src/lodge/core/views.py:55`, and Task 2's `ChangeFacts`.
Scenario: a published decision already has a record-level problem, its state is cached, and one other record changes.
Task 10 supplies published `check_state` problems from the stored state, but its declared fields contain only unrecorded problems, while rows contain a `fails check` flag without the check number, wording, or the distinction between single-state and change problems.
It cannot reconstruct `published_problems` from those fields, so it must either recompute the published check, invalidating the changed-read estimate, or lose the existing-problem comparison semantics.
Verified by inspecting the declared types and current check implementation, and with a strict-mypy scratch contract that rejects accessing the absent `StoredState.problems` member.
Fix: persist and type the complete single-state check facts separately from the combined read flags, specify how published states are built and located, and test a published record-level problem together with a new problem on the same path.

### F9: Important, the codec contract cannot encode the stored answers

Handle: Tasks 9 and 10's plain codec and `StoredState.answers`, conflicting with `src/lodge/app/results.py:24`, `src/lodge/app/results.py:73`, and `src/lodge/app/threads.py:106`.
Scenario: caching `waiting` or `threads` reaches their titles dictionary and `Read.statuses` mapping, for which `to_plain` specifies no representation.
Tuple-to-list conversion and tagged dataclasses do not encode mappings, and passing the original dictionary through leaves nested dataclasses unconverted and defeats the promised shape validation.
Verified by inspecting the actual result dataclasses in `structure-contracts.txt`, including the default empty mapping in every `Read`.
Fix: define tagged recursive mapping support, register result classes in app without a reverse core dependency, keep serialisation in the adapter, and add round trips for complete waiting, threads, and thread answers, including populated statuses and titles.

### F10: Important, the listing migration leaves existing typed consumers without a source tree

Handle: Task 8's removed `trees()` port, new `publish(Listing, ...)`, and twelve-line write allowance, conflicting with `src/lodge/app/writes.py:84`, `src/lodge/app/threads.py:84`, `src/lodge/core/apply.py:41`, and `src/lodge/gitstore/plumbing.py:14`.
Scenario: the new state exposes a `Listing` with blob IDs, but writes still pass its current tree into `apply_drafts`, read `.files`, overlay text into a `Tree`, and call the old `check_writes(Tree, ...)` helper.
`Listing` supplies neither text files nor the `Tree` type those interfaces require, and `core/apply.py` and `gitstore/plumbing.py` are absent from Task 8's modification list.
This is a static contract gap visible in the existing call sites, rather than a runtime test of code that has not been built.
Fix: explicitly specify and budget a text materialisation helper for write and draft operations, keep the listing separately for optimistic publication, adapt the shared write-safety helper, and preflight all front-door consumers under strict mypy.

### F11: Important, lock errors are also DatabaseError and must not trigger destructive repair

Handle: Task 9's corruption handling and tests, conflicting with its locked-index guarantee, decision d-kj554d, and scratch probe `sqlite_cases.py`.
Scenario: another process holds `BEGIN EXCLUSIVE` while a new lodge process reads the meta table.
After the timeout SQLite raises `OperationalError`, which is a subclass of `DatabaseError`, so using the plan's stated meta-read exception as the corruption detector can delete a healthy, actively locked database.
Verified in `sqlite-cases.txt`: the meta read raises `OperationalError: database is locked` after 0.203 s, and `isinstance(error, sqlite3.DatabaseError)` is true.
The named lock test exercises `keep_parses` on an already open connection, so it does not cover this opening failure.
Fix: distinguish lock and permission failures from recognised corruption error codes, fall back without deleting on operational failures, and test opening a populated index under an exclusive lock, including after timeout and lock release.

### F12: Important, state installation, eviction, and multi-step reads have no concurrency contract

Handle: Tasks 9 and 10's `state`, `rows`, `parses`, `keep_state`, and four-state eviction, conflicting with d-kj554d's unchanged-output guarantee and `src/lodge/app/reads.py:39`.
Scenario: reader A fetches state metadata, writer B installs a fifth state and evicts A's buckets or parse rows, then A fetches rows and parses from separate calls.
A can receive missing records despite having accepted the state as a hit, and a partial state installation or interrupted commit can similarly expose metadata without complete answers, buckets, and words.
No proposed test covers concurrent state builders, eviction during a read, interruption during installation, or a database error after the state hit.
This finding is based on the proposed interface and test coverage, since the index implementation does not yet exist to run.
Fix: specify atomic state publication and eviction, pin a consistent SQLite read transaction across dependent lookups or validate completeness and fall back for the whole read, roll back failed writes, and add deterministic two-connection interleaving and interrupted-write tests comparing output and exit status with `LODGE_INDEX=off`.

### F13: Important, time validity only handles forward movement

Handle: Task 10's expiry rule and `test_expired_state_is_rebuilt`, conflicting with `src/lodge/core/check_change.py:71`.
Scenario: a new decision is dated at 12:00, the state is built at 12:01 with no future-date error and no expiry, and another process reads the shared index with its clock at 11:59.
The cached read omits the future-date failure that a fresh check produces.
Verified with `_dates` in `time-state.txt`: the same unchanged snapshots have no date problem at 12:01 and a check 1 problem at 11:59.
Fix: store both ends of the time interval in which the result is valid, compare timezone-aware instants, and test backward clock movement and shared-index readers with differing clocks as well as the existing forward-expiry case.

### F14: Important, a successful C parse can still change the existing parser's diagnostics

Handle: Task 3's fallback only on C errors and equivalence tests, conflicting with `src/lodge/core/yamlio.py:62`, `src/lodge/core/document.py:35`, and the correctness-first ruling d-1bww1r.
Scenario: a header contains a 600-level nested sequence in `title`, which Python's loader refuses as nested too deeply but the C loader successfully constructs.
The fallback never runs, changing the check problem from invalid YAML with no line to a non-empty-string error at line 4.
Verified with the probe's C-loader construction and fallback in `yaml-depth.txt`, including `parse_record` results on the complete synthetic record.
Fix: route potentially deep or otherwise unsupported successful C parses through the original loader, and extend the differential corpus to successful-C/error-Python cases, preserving the complete Problem including its wording and line.

### F15: Important, the changed-read benchmark times only its first command after a cache miss

Handle: Task 1's `bench_reads.py --changed` contract and Tasks 10 and 12's changed-read acceptance tables, conflicting with the rebuild phases measured by `probes/phases.py` and the per-state reuse specified by Tasks 9 and 10.
Scenario: the benchmark copies the store, edits one statement once, then times every command in sequence.
The first `show` builds the changed state, so subsequent searches and other reads hit that same state and are labelled changed-record timings despite avoiding its rebuild cost.
Repeated runs have the same cold-versus-warm ambiguity unless cache preparation is specified per timed command.
This is verified from the benchmark algorithm in the plan, since `bench_reads.py` has not yet been written.
Fix: prepare a warm baseline cache and restore it outside the timed interval before each independent changed-state command, or create a distinct controlled edit for each trial, and report cold, seen-state, and changed-state measurements separately with successful output and exit-status comparisons.

### F16: Important, package metadata is not a parser or implementation identity

Handle: Task 9's package digest, line 349, conflicting with brief ruling 3's content-and-parser-version cache and `src/lodge/core/document.py:34`.
Scenario: an editable build or a restored installation replaces a Python module with different same-length contents and preserves its modification time.
The specified digest over relative names, sizes, and mtimes is unchanged, so old parses and check results are accepted under different code.
Verified in `digest-case.txt`: a same-length source replacement with the original timestamp has the same proposed metadata digest and a different content hash.
Fix: hash package source bytes or a content-derived immutable build identifier, include the parse format and relevant dependency identities, and test that a same-size, same-mtime parser replacement invalidates the index.

### F17: Important, the performance stop precedes the optimisation needed to pass it

Handle: Task 10 Step 4, Task 11, and the Expected cost table, conflicting with the reproduced `probes/walk.py` timings and decision d-8kq2nk.
Scenario: a warm read is slightly above 0.3 s because Task 8 still lists every directory, and Task 10 must stop before Task 11 can replace that walk with cached folder signatures.
The planner's expected 0.2 s warm path already assumes the 0.01 s folder-signature cost that Task 11 has not delivered, whereas the final reproduced names-only walk alone takes 81.1 ms.
Fix: move folder-signature work ahead of final target acceptance, or make Task 10's measurement an explicitly provisional diagnostic and apply the coordinator's stop only after every planned local optimisation has landed.
Keep the separate broad-search issue F6 as an acceptance blocker even after fixing the order.

### F18: Minor, the named linearity test does not test linearity

Handle: Task 2's `test_missing_uses_one_union`, conflicting with `src/lodge/core/check_change.py:55`.
Scenario: the original quadratic implementation is left unchanged or later restored, and the proposed 2,000-entry test still returns exactly the expected one missing-record problem.
The specified assertion checks output alone, so the old implementation passes the supposed performance regression test.
Fix: instrument the relevant mapping key or union operations and assert that the full union is built once, while retaining the exact-problem assertion and keeping wall-clock limits out of pytest.

## Verification and limits

The three synthetic stores already existed on native disk and contained 1,593, 16,008, and 159,716 files.
I used the existing native virtual environment, confirmed its installed Python source was byte-identical to `src/lodge/`, and compiled its package bytecode before the final sequential reruns.
Its Python is 3.13.16, whereas the planner reported 3.13.5, so these are mechanism checks on the available interpreter rather than a claim of an exactly reproduced historical environment.
Native startup including `import lodge.main` took 0.105, 0.102, and 0.096 s, consistent with the planner's approximate 0.10 s figure.
The final phase reruns used the supplied `phases.py` with its linear `_missing` and C-loader patches and one run per store, excluding process startup from each phase.
They are diagnostic measurements, not production timing acceptance tests or best-of-three phase results.

| Phase, seconds | 1,593 files | 16,008 files | 159,716 files |
|---|---:|---:|---:|
| Trees | 0.086 | 0.513 | 5.111 |
| Current parse | 0.058 | 0.655 | 6.690 |
| Current check_state | 0.008 | 0.101 | 8.464 |
| Current derive | 0.003 | 0.042 | 1.353 |
| Published parse | 0.058 | 0.592 | 6.577 |
| check_change | 0.028 | 0.450 | 24.263 |
| Search | 0.012 | 0.183 | 2.265 |

These broadly confirm the planner's measured parse and check bottlenecks, including the large-store superlinear check growth.
The final native-disk walk rerun, internally best of three, found 159,716 files and 2,253 folders, with 81.1 ms for names, 3.7 ms for known-folder stats, 42.3 ms for `diff-files`, 12.6 ms for the cached diff, and 148.0 ms for status.
The codec scratch variant with GC disabled measured 0.080 s to select every row, 0.114 s to unmarshal, 0.154 s to rebuild decisions, and 0.039 s to rebuild entries, so the proposed 0.45 s parse-cache allowance is plausible for this specialised tuple decoder alone.
It does not measure the proposed generic validated decoder, listings, assembly, published-state materialisation, or stored read-model construction.
The changed-read budget remains unverified, and its listed phase estimates already sum to 3.31 s before process startup and identity checks.
The FTS probe again measured a 52.8 MB word index and 107,247 candidates for the two-word OR query, confirming the candidate-volume concern rather than an FTS availability problem.
The existing structure, branch-rewrite, checkout, checkout-gate, and published-read tests passed, 77 tests in 4.43 s, with pytest's temporary files and cache configuration kept in scratch.
Those tests establish today's behaviour for rewritten branches, missing bases, and gate comparisons, but cannot establish the correctness of the future indexed versions.
No index implementation exists yet, so full read-only, corruption, version-mismatch, and concurrent-writer behaviour could only be checked against the proposed contracts and SQLite primitives, not against a completed lodge index.
I did not rerun the unpatched 160,000-file end-to-end CLI baseline or attempt to verify the future 0.3 s and 3 s targets as though they were implemented.
No network operation or `lodge add` was run, and the only worktree output is this review.

The final sequential timing commands are reproducible with `/var/tmp/lodge-bench/venv/bin/python /var/tmp/lodge-review-feasibility-performance/rerun_native.py`, and the individual correctness and shape probes are saved beside it.

Counts: 1 Blocking, 16 Important, 1 Minor.
F2, Blocking: index flags hide changed disk records and can let the gate inspect stale blobs.
F6, Important: broad-search scoring alone takes at least 0.723 s before any index overhead.
F12, Important: concurrent state installation and eviction lack a consistent-read and fallback contract.
