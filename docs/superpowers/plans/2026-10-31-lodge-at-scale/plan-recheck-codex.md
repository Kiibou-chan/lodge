# Feasibility and performance recheck

The fix round is not ready for implementation approval.
This review checks `git diff 7aaef43 dea8dcb`, the current numbered plan, the original Codex review, the fix mapping, and all seventeen decisions named by that mapping, read through `lodge show ID --reasoning`.
Statuses below assess the revised specification, rather than claiming that its unimplemented tests have passed.
Scratch evidence is under `/var/tmp/lodge-recheck-feasibility-performance/` on native ext4 disk, with benchmark stores under `/var/tmp/lodge-bench/`.
No network access or `lodge add` is used.

## Original findings

| Finding | Status | Revised plan lines | Assessment |
|---|---|---|---|
| F1, identical-state identity | Partly fixed | 375 to 387, 487 | Clean and redundant overlays now share the base tree ID, but the asserted equivalence across committed and overlaid representations still fails for edit-then-commit and attachment-only commits. |
| F2, index flags hide edits, Blocking | Fixed | 25, 348, 375 to 385, 437 | Exact-tree consumers hash disk bytes, while fast reads include flagged entries and disable the named Git stat shortcuts. |
| F3, conversion sources and invalidation | Partly fixed | 46, 375 to 386 | Autocrlf, global sources, and configuration keys are addressed, but the no-source shortcut still misses a root attributes file that Git reads from its index. |
| F4, residual superlinear work | Fixed | 118 to 154 | Running predecessors, reverse doubt propagation, and indexed earlier decisions replace the three reported scans, with differential tests and doubling probes. |
| F5, deep-chain read crashes | Partly fixed | 118, 145, 150 | Core traversal and `render_spec` are covered, but the requested viewer path still recurses in `viewer/pages.py:86`. |
| F6, broad-search budget | Partly fixed | 5, 61, 69, 532, 579 to 581 | The cost is acknowledged and measured separately, but d-me8vm3 leaves the coordinator’s acceptance decision open and does not supply a design meeting the original target. |
| F7, module ownership and front doors | Fixed | 21, 28, 256, 325, 397 to 398, 448 | Leaf types and adapter-facing exports are now assigned explicitly, although the new skeleton procedure itself needs a runnable preflight. |
| F8, published check facts absent | Fixed | 465 to 467, 482 to 484, 543 to 547 | `StateFacts` persists the complete single-state problems and statuses by identity, with differential published-problem cases. |
| F9, codec cannot encode answers | Fixed | 408 to 411, 433 | Recursive mappings cover titles and populated `Read.statuses`, with app-supplied classes and an explicit mapping round trip. |
| F10, writes lose their text tree | Fixed | 9, 25, 342, 349, 370 | `Store.trees()` and the write contracts remain, with listings added alongside them. |
| F11, lock errors delete healthy data | Fixed | 422 to 435 | Recovery is restricted to corruption codes, operational failures fall back, and opening under an exclusive lock is tested. |
| F12, installation and eviction races | Fixed | 477 to 498 | Dependent reads share a transaction, installation and eviction are atomic, and deterministic interleavings plus interrupted writes are specified. |
| F13, backward clocks | Fixed | 471 to 472, 488, 496 | Both validity bounds are stored and compared as aware instants, with forward and backward tests. |
| F14, successful C parses change diagnostics | Fixed | 171 to 184 | Deep nesting and the known divergent syntax are excluded by the guard, with a two-direction differential corpus. |
| F15, changed-state timing contamination | Fixed | 103 to 105 | A saved seen index is restored before every independent timed changed-state run. |
| F16, metadata digest misses source changes | Fixed | 421, 434 | Source bytes replace metadata and the same-size, same-mtime replacement is explicitly tested. |
| F17, premature performance stop | Fixed | 502, 532, 550, 581 | Intermediate numbers are provisional and the target stop follows the folder cache. |
| F18, Minor, false linearity test | Fixed | 148 | Counting mapping-key calls rejects the old per-record unions while preserving the problem assertion. |

## Residual findings

### F1: Important, identity is still dependent on the representation of equal files

Handle: Task 8b, lines 375 to 387, and Task 10a, line 487.
Failure scenario: an edited entry is read and then committed without changing its disk bytes, or an attachment-only change is committed, or disk contents are reverted to the published state while `HEAD` still differs.
The edited state’s overlay hash differs from its later Git tree ID, attachment bytes and file modes remain part of a clean Git tree ID, and an overlay over a different `HEAD` does not become the published tree ID.
`git-cases.txt` verifies equal exact mappings across edit and commit with unequal identities, and an attachment-only commit with the same mappings but a changed identity.
The gate remains exact, but the stated identity equivalence test cannot pass, previously seen equivalent contents rebuild, and the identical-state shortcut is still missed in these cases.
Fix: use one identity of the semantic file mapping and attachment names across overlays and committed trees, or explicitly narrow the identity contract to its one-way safety property, retain exact equality for the build-time shortcut, and obtain agreement on the additional rebuilds.
Test commit-after-edit, attachment-only commits, and a working tree reverted to published contents while its `HEAD` differs.

### F3: Important, Git can still apply an attributes source the no-source shortcut misses

Handle: Task 8b, line 378, against its exact-tree contract at lines 383 to 387.
Failure scenario: a committed root `.gitattributes` selects a clean and smudge filter, a record is checked out through that filter, then the root attributes file is removed from disk without staging its removal.
The shortcut finds no root file and none under `lodge/`, but Git falls back to the root attributes file in its index, so both diff commands still report no record change.
`filter_fallback.py` verifies a valid entry whose disk statement is `Working payload.` and committed statement is `Canonical payload.`, with no overlay path from either diff command and no special index flags.
`attributes_fallback.py` verifies the same source-discovery gap with CRLF conversion.
Even after the invalid command in R3 is corrected, the recipe reads the committed text and can serve a different entry from the exact-tree read.
Fix: include index-backed attributes sources for the root and every relevant ancestor in source selection and invalidation, or conservatively query Git whenever it might apply such a source.
Add a removed-but-indexed root attributes file with a content-changing filter to the exact-tree differential tests, including a warm source-selection change.

### F5: Important, the viewer still crashes after the iterative traversal returns

Handle: Task 2, lines 118, 145, and 150, against `src/lodge/viewer/pages.py:86`.
Failure scenario: a valid deep dependency chain reaches the viewer after `rests_on_tree` has been made iterative, then `_branches` recursively renders that same tree and raises `RecursionError`.
`viewer_chain.py` constructs the returned `Branch` shape iteratively and verifies that depth 30 renders, while depths 2,000 and 5,000 still fail in the unchanged renderer.
Fix: render the viewer’s dependency tree with an explicit stack and include the actual viewer rendering path in the deep-chain acceptance test.

### F6: Important, broad-search acceptance still needs the coordinator’s ruling

Handle: the goal at line 5, the open call at line 61, and Task 12 at lines 579 to 581.
Failure scenario: implementation finishes with broad seen-state searches exceeding 0.3 s and declares its target stop satisfied because only smaller candidate sets are checked.
Decision d-me8vm3 explicitly leaves whether the original target covers broad searches to the coordinator, so the planner’s exemption is not yet a recorded acceptance change.
Fix: obtain that concrete target ruling before implementation approval, or retain the original stop condition and prove a bounded-result design against the differential oracle.
The separate reporting and delayed stop are useful changes, but neither closes the original feasibility finding.

## Newly identified findings

The findings below distinguish regressions introduced by the split from further gaps exposed while rechecking it.

### R1: Important, the split publishes searchable states before their words are complete

Handle: Task 10a, lines 483 to 498, and Task 10b, lines 517 to 522, against d-her016 and d-rs76ks.
Failure scenario permitted by these interfaces: `keep_state` commits a new state and its rows, then `keep_words` fails because the database is busy, unwritable, or the process exits.
Task 9 makes failed writes do nothing, so the state remains a hit, while `candidates` returns an ordinary empty or partial dictionary for its absent word rows.
Calling `keep_words` first is insufficient on its own, since its `None` return cannot establish that the swallowed write succeeded.
No lookup returns fewer rows than promised, since the absent records were never candidates, so Task 10a’s completeness fallback cannot detect the omission.
This gap is introduced by removing `words` from the original transactional `keep_state` signature and adding an independent `keep_words` operation.
`split_words.py` reproduces the interleaving with two real SQLite connections, then verifies that a locked word write leaves the installed state visible with zero candidates for a matching record.
Fix: publish the state’s search-ready marker, word references, and all missing word rows in the same transaction as the state, or retain a complete manifest and fall back for the whole search until completeness is proved.
Add deterministic two-connection tests for a search between the writes, interruption, and a swallowed word-write error, comparing text and exit status with `LODGE_INDEX=off`.

### R2: Important, Task 10a has no bounded path for a coded record’s citers

Handle: Task 5, lines 226 to 241, and Task 10a, lines 457 to 486 and 502, against Task 10b at lines 508 to 522.
Failure scenario: the second `show CODE` must print the newest ten citing records and the exact omitted count, but its stored row has no citer IDs or count, its stored state supplies only a code-to-ID map for discovery, and its named answers cover waiting and threads only.
The split puts word lookup in the later Task 10b, leaving Task 10a’s independently buildable `show` dependent on a scan of every record’s text.
Even after Task 10b, a valid function-word code such as `A` has no postings from `core.words`, so word lookup cannot prove its citers.
`citer_cost.py` scans the definition’s whole-token boundaries over 157,466 already parsed native-disk benchmark records, with the collector disabled, taking 0.294 s best of three for `CODE-17` and 0.306 s for `A`, before startup, identity, SQLite, decoding, or output.
This is a measured scan cost for the stated definition, rather than a timing of future indexed code.
Fix: persist each coded record’s ordered citer IDs and exact count when building its state, or add an equivalent complete citation index available in Task 10a.
Specify bounded lookups for coded `show` and add seen-state benchmarks for a normal code and a function-word code with citers, without assembling or scanning the snapshot.

### R3: Important, the conversion-source discovery command is invalid

Handle: Task 8b, line 378, and call 4 at line 46, introduced by the conversion-source fix.
Failure scenario: `attributes.py` executes the written `git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM` command to discover conversion sources before an indexed read.
Git accepts one variable per invocation, so that command exits 129 and prints usage, either aborting the read through the Git adapter or losing the conversion sources if its error is treated as absence.
`git_cases.py` verifies the exit code on Git 2.56.0 and verifies that each variable separately resolves successfully.
Fix: invoke `git var GIT_ATTR_GLOBAL` and `git var GIT_ATTR_SYSTEM` separately, or parse `git var -l`, and handle an unsupported variable as a conservative fallback rather than no attributes.
Repeat d-dqpf59’s cache-key contract in the task and test a warm change to `core.autocrlf`, `core.attributesFile`, and the selected source file, since the replacement task no longer specifies that invalidation test.

### R4: Important, replacing a tracked file with a directory leaves a phantom file in the overlay

Handle: Task 8b, line 375, and its exact-tree oracle at lines 383 to 387, against `src/lodge/gitstore/checkout.py:90` and `src/lodge/gitstore/checkout.py:110`.
Failure scenario: tracked `lodge/decisions/old.md` becomes a directory containing `new.md`.
`diff-files` names `old.md`, that path still exists, and `_read` returns empty text for a directory, so applying the written overlay retains an empty `old.md` in addition to its child.
The exact `disk_tree` never includes the directory itself, so the fast snapshot adds a spurious unreadable record or stray problem.
`path_kind.py` verifies the named diff path, directory existence, empty `_read`, and the exact tree containing only the child.
This recipe was inherited from the original plan rather than introduced by the split, but the expanded identity tests still omit the case.
Fix: distinguish a path that the disk walk would enumerate from mere existence, tombstone a base file replaced by a real directory, and handle transitions in both directions without following directory links.
Add differential file-to-directory and directory-to-file tests, including an empty directory and attachment paths.

### R5: Minor, the new skeleton preflight fails its literal strict-mypy requirement

Handle: global constraint 21 and Task 8a’s `blob_id` signature at line 334.
Failure scenario: a builder follows the required signatures with `...` bodies and must make strict mypy green before writing tests.
The scratch `def blob_id(raw: bytes) -> str: ...` fails with `Missing return statement [empty-body]`, reproduced with the project’s mypy.
Protocol declarations can use ellipses, but the concrete `str`-returning function cannot satisfy that preflight as specified.
Fix: permit `raise NotImplementedError` in concrete skeletons and retain ellipses only where mypy permits them.

## Verification and limits

All scratch repositories and databases were created under `/var/tmp/lodge-recheck-feasibility-performance/`, and the existing synthetic `s90000` benchmark store was read without alteration.
`df -T` confirms native ext4 for both scratch and benchmark data.
The timed citation scan used the native virtual environment’s Python 3.13.16, SQLite 3.53.1, and PyYAML 6.0.3 with libyaml available, and its installed Python source files were verified byte-identical to the worktree’s source.
The project environment used for correctness probes and the baseline tests runs Python 3.13.5, so no timing comparison assumes identical interpreters.
The citation command is `/var/tmp/lodge-bench/venv/bin/python /var/tmp/lodge-recheck-feasibility-performance/citer_cost.py`, with all parsing completed outside the timed region and three sequential scans per query.
The timings describe a straightforward implementation of the specified citation predicate, rather than a lower bound on every possible scanner.
The existing benchmark store has 159,716 files, including 157,466 decision and entry records, and predates Task 1’s proposed extra families and citers.

`yaml_guard.py` is a scratch implementation of the stated line grammar and C-error fallback, using seed 391 and 20,000 generated and mutated headers.
It admitted 8,914 headers with zero differences after fallback, providing supporting evidence for the F14 fix without proving the future guard implementation.
Its result and examples are saved in `yaml-guard.txt`.
The Git command, identity, path-kind, indexed-attributes, viewer-depth, and SQLite transaction probes and their text output are saved alongside it.
R1 models the proposed split using SQLite primitives, and R4 applies the written overlay recipe to the existing disk reader, rather than claiming to execute index code that has not been built.

The targeted baseline command passed 145 tests in 4.35 s, covering structure, YAML, snapshots, ordering, change checks, checkout, checkout gates, and checkout safety.
It used `pytest -q -p no:cacheprovider --basetemp=/var/tmp/lodge-recheck-feasibility-performance/pytest` with those eight test files, and its output is saved in `pytest.txt`.
The strict-mypy skeleton failure is saved in `skeleton-mypy.txt`.
`lodge waiting`, `lodge spec`, and the seventeen named decision reads ran offline with bytecode writes disabled, and the latter two outputs are saved in scratch.
The source remains unimplemented, so these checks establish current behaviour and contract counterexamples, not a passing future index, a 0.3 s seen-state read, or a 3 s changed-state read.
The revised changed-read estimates still sum to 3.31 s before startup and identity work, so their acceptance remains dependent on the final measured phase table.
No network operation, `lodge add`, commit, or push was run, and this recheck wrote only its requested output file in the worktree.

## Counts

Original Blocking and Important findings: 13 fixed, 4 partly fixed, and 0 not fixed.
The original Blocking finding F2 is fixed, and the four remaining Important findings are F1, F3, F5, and F6.
The original Minor finding F18 is also fixed.
Newly identified findings: 0 Blocking, 4 Important, and 1 Minor.
Outstanding total, with each issue counted once: 0 Blocking, 8 Important, and 1 Minor.
The most important finding is R1: separate state and word publication can leave a valid state hit that silently omits matching search results after an interrupted or failed word write.
