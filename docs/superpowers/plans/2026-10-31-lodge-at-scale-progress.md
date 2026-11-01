# Ledger: lodge at scale, plan docs/superpowers/plans/2026-10-31-lodge-at-scale.md

Branch `read-speed`, based on `search-brief` (d-fqymzm); the brief is `2026-10-31-lodge-at-scale/brief.md`.
Briefs, reports, and reviews: `docs/superpowers/plans/2026-10-31-lodge-at-scale/`.

The coordinator's rulings for this plan, recorded: correctness first (d-1bww1r), the speed order (d-1ftgg3), the index and its targets (d-232gxs), leaner reads (d-3g6ard), benchmarks (d-542m5g).
The planner's calls, recorded: d-5xhxh1, d-5zqvxb, d-8kq2nk, d-atsx8n, d-c400w8, d-c4w7xy, d-eby5pb, d-f3r5aq, d-hf2fms, d-kj554d, d-m0g9tx, d-n9w4by, d-p60ka9, d-s2ypth, d-zyqzkg; d-5xhxh1 and d-hf2fms were edited before publishing, through `lodge draft` and `lodge add`, to name decision IDs where their first text named draft labels.
The coordinator's final-review rulings, recorded in 84e8cd3: d-cqr414 narrows d-a8gkrh so every write checks the cap, d-3ck8km replaces d-gvz66f and d-4n5tr6 with one file per build in WAL mode with `synchronous=NORMAL`, and d-bbhak7 narrows d-jwpwe7 to name stat-preserving writes unseen by indexed reads.
The coordinator's constraint on unwritable and locked indexes is d-kj554d and Task 9's failure-mode tests.
SCALE-1 and DISK-1 are answered by the author through d-j51qmy: 1,900 bytes per file, about 305 MB at 160,000 files, and four kept states.
Plan written; probes and their output in `plan-report.md` and `probes/`.
Plan reviewed: `plan-review-opus.md` (2 Blocking, 8 Important, 8 Minor) and `plan-review-codex.md` (1 Blocking, 16 Important, 1 Minor).
Fix round 1 (`plan-fix-1.md`): every finding taken, none parked; Task 8 split into 8a and 8b, Task 10 into 10a, 10b, and 10c.
The coordinator's rulings for fix round 1, recorded: d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, d-ytf272.
The planner's calls for fix round 1, recorded: d-7e8zhd, d-ana6c0, d-c5a1y4, d-dqpf59, d-dxqxsn (narrowed by d-k194gk to published statuses only), d-emtwbs, d-faakge (replacing d-f3r5aq), d-her016, d-me8vm3, d-26e6zj.
Plan rechecked: `plan-recheck-opus.md` (all 18 fixed; N1 to N4 Important, N5 to N9 Minor) and `plan-recheck-codex.md` (13 fixed, 4 partly; R1 to R4 Important, R5 Minor).
Fix round 2 (`plan-fix-2.md`): every finding taken, none parked; the index's invariants in the Global Constraints, tested by fault injection.
The coordinator's ruling for fix round 2, recorded: d-6hb3yd.
The planner's calls for fix round 2, recorded: d-c0q20c, d-aej8rs, d-9r24jc, d-4n5tr6, d-gd00c6.
The coordinator's ruling on broad searches, recorded: d-hxmdkz (narrows d-gd00c6), their own stop at 1.0 s warm; the 0.3 s stop covers the point reads and searches with at most 5,000 candidates.
SCALE-1 and DISK-1 are settled by d-j51qmy, retaining four states as the one constant `KEPT_STATES` (d-ytf272).
Rechecked again: `plan-recheck-2.md` (V1 to V3 Important, V4 to V8 Minor).
Fix round 3 (`plan-fix-3.md`): every finding taken, none parked; the index's consistency rewritten so nothing a kept state depends on is ever deleted.
The coordinator's ruling for fix round 3, recorded: d-t3afj1 (replaces d-6hb3yd).
The planner's calls for fix round 3, recorded: d-4j98ph (replaces d-aej8rs), d-gvz66f, d-n6tqzq.
The index's size cap follows DISK-1 (d-j51qmy): `INDEX_BYTES_PER_FILE = 1_900`, about 305 MB at 160,000 files, keeping four states, replacing d-4pbeax's byte allowance and narrowing d-a8gkrh without changing its formula.
Rechecked a third time: `plan-recheck-3.md` (R1 Blocking, R2 and R4 Important, R3 and R5 Minor).
Fix round 4 (`plan-fix-4.md`): every finding taken, none parked; generations dropped for one file per build, cleared in place.
The coordinator's ruling for fix round 4, recorded: d-e3stjn (replaces the generations of d-gvz66f).
The planner's call for fix round 4, recorded: d-c6cegr.
SCALE-1 and DISK-1 answered by the author: A, with the byte allowance in d-j51qmy.
Rechecked a fourth time: `plan-recheck-4.md` (W1, W3, W4 Important; seven Minor).
Fix round 5 (`plan-fix-5.md`): W1 to W5 and W7 to W10 taken, W6 taken as measurements.
The planner's calls for fix round 5, recorded: d-a8gkrh, d-bzp30x.
Parked: W6's eviction of facts rows no remaining state names, until Task 10c's and Task 12's measurements say how often clears come.
Plan accepted for build by the coordinator after fix round 5.
Tasks 1 and 2 are built from 2dffc85 on branch `read-speed-build`; their plan text is unchanged since 2dffc85 (`diff` of the two sections, empty).

## Preflight scan

Each task's Produces against the later tasks' Consumes and their use in the task text; mismatches fixed in the plan in this commit:

| Task | Consumes, as now written | Finding | Fix |
|---|---|---|---|
| 4 | Task 2's `facts` | matches `check_change(..., facts=)` and `ChangeFacts` | none |
| 5 | Task 4's `read_checked` | matches | none |
| 6 | Task 5's `is_code_token`, `family`, `cites`, `citers` | `rank` takes `citing`, which `citers` gives; `citers` was not named | named |
| 7 | Tasks 5 and 6 | matches (`show_many`, `--phrase`, `search_many`) | none |
| 8a | nothing beyond Task 4 | matches | none |
| 8b | Task 8a's `Listing`, `blob_id`, exact trees | matches | none |
| 9 | Task 8a's `parse_file`, `assemble`, `Parsed`, `Tree.blobs` | `Index.parses` returns `Parsed`, which was not named | named |
| 10a | Task 8b's `identities`, `listings`, `texts`; Task 9's `Index` (with `epoch`), codec, failure modes; Task 4's shortcut; Task 5's `family`, `code_tokens`, `show_many`, `Shown` fields | indexed `show` prints through Task 5's `ShownMany`, not named | named |
| 10b | Task 6's `rank`, `Candidate`, `parse_query`, `needs_memory`, `Filters`, `search_many`; Task 5's `family`; Task 9's `keep_parses`; Task 10a's states, `rows`, `all_rows`, `codes`, `citing`, `keep_state` | words passed to `keep_parses` and `keep_state` changed both signatures, breaking the Task 9 and 10a tests that call them, which the Files list omitted | `gitstore` computes words with `core.parse_words` (an allowed `gitstore` to `core` import, `tests/structure_tables.py`), so both signatures stay; consumed names completed |
| 10c | Task 2's `ChangeFacts`, `check_change(..., facts=)`; Task 10a's `StateFacts`, `facts`, `keep_state` | `facts=` keyword not named | named |
| 11 | Task 8b's identity and walk; Task 9's `open_index`, settings, failure modes | matches; `main.py` hands the store the index | named |
| 12 | every task | the clears per hundred changed reads need runs without restoring the saved index, which Task 1's `changed` mode does | Task 12 adds `--mode chained` to `scripts/bench_reads.py` |

No mismatch is left open.


Tasks 1 and 2 fix round: I1 centralises change-check facts using `sort_key`, replaces the self-comparison by a pre-Task-2 oracle, and tests the already-published gate note even when the key changes.
M1 reuses published snapshot facts when the gate returns the same tree; M2 adds per-run timeouts, SIGTERM cleanup, and a clean-store requirement for every benchmark mode; M4 exercises flagged decisions in the shape probe and uses `datetime.UTC`; M5 moves the app call-budget test into the app suite.
M6 is closed: the earlier concern in `task-1-2-report.md` compared combined derivation and state checks with an estimate for state checks alone; the measured 0.424 s state check meets the plan's separate estimate, alongside 0.950 s derivation (review M6, Expected cost).
M3 has two deferred halves: `written_order` can group entries once per render using existing imports, to be taken by the next round touching `order.py` or `render.py`; `derived_order` needs a separate large-area rewrite, whose standard priority queue would require `heapq`, outside the fixed core import rules.


Task 7 and the earlier Task 5 fix round are reported in `2026-10-31-lodge-at-scale/task-7-report.md`.
Tasks 6 and 7 fix round: d-t2dsd3's phrase groups and all review minors addressed, except Task 6 M1 measured only by the coordinator's instruction, pending Task 10b.
The report and failing-test evidence are in `2026-10-31-lodge-at-scale/task-8b-report.md`.
Task 6 already resolved the deferred `written_order` grouping; Task 8a's report verifies the area-local inputs, and this round preserves them.


Task 9 fix round 2 addresses recheck N1 and N3 to N7; evidence and delivery are in `2026-10-31-lodge-at-scale/task-9-fix-2-report.md`.
N1 shares decoded units in the gate's extra snapshots, and N3 to N6 cover private module imports, the remaining codec guards, POST release, and index-opening failure; unused settings threading is removed.
N7 is now an explicit Task 10a Step 3a: parse-only writers clear too, `meta.kept` means a state kept, the tree's file count is the caller's, and invariant 1's unit growth is bounded by the end of Task 10a.
M9's batching remains deferred because the recheck measured about 0.05 s saved, superseding the previous report's per-key error-isolation rationale.
N2 remains report-only here: the recheck measured 1.40 to 1.42 s for lookup and decode of 160,800 units, giving about 4.3 s against the changed-read target of 3 s on the plan's arithmetic.
The planner is reworking that path; this fix round changes neither lookup nor codec design, and the stop remains after Task 11 (d-26e6zj).

## Plan fixes 6, 6b, 7, and 7b

Files: `2026-10-31-lodge-at-scale/plan-fix-6/` (plan fix 6 with `tasks.md`, 6b, 7b, and Codex's reviews; 7 is kept only in the reviews' citations).
Plan fix 6 (Task 8c, a private stat cache RAW-1 with Task 11b, LAZY-1): reviewed by Codex (`review-codex.md`, R1 and R4 Blocking), rejected; withdrawn whole.
Plan fix 6b (Task 8c without RAW-1 or LAZY-1, Task 11 with FOLD-1, Task 12 with the conversion row, R11 written as two branches): reviewed by Codex with 7 (`review-codex-67.md`, accept with fixes: F10, the empty-text gitlink key, the absent submodule folder, both R11 branches with regression tests), fixed in place, then accepted (`review-codex-7b.md`).
Plan fix 7 (delta rows and citers, a diff-scoped `check_change`, joined decoding, TGT-7): reviewed by Codex (`review-codex-67.md`, F1 Blocking, F2 to F9 Important), rejected; withdrawn whole.
Plan fix 7b (Task 9c's ordered scan with each row decoded and admitted on its own, full checks, the keep on a state's second sighting after the output, 3 s kept): reviewed by Codex (`review-codex-7b.md`, accept with fixes B1 to B6), fixed in place; the changed read measures 4.713 s as a sum of stages (floor 3.214 s), so Task 12 is expected to record a miss.
Pasted into the plan from `tasks-6b.md` and `tasks-7b.md`: calls 22 to 25, the cost table's rows, the build order line, Task 8c and Task 9c after Task 9, Task 10a and Task 10c amended, Task 11 and Task 12 replaced.
Task 9's hand-offs now in the plan: I4 in Task 10a's Step 3a with the cap's new condition (a working set inserted since the last clear, or a state kept); M9 answered by Task 9c; `sha1(repr(settings).encode()).hexdigest()` added for the stored state's key in Step 3a; the stale `marshal` mentions replaced by JSON, as built.
Build order from here: Task 8c, Task 9c, Task 10a, Task 10b, Task 10c, Task 11, Task 12.
STALE-1 is ruled by d-jwpwe7 for production R11-B; CONV-1 is d-egknpk, FOLD-1 is d-eg5nra, and SECOND-1 was required before Task 10a; no further record is needed for this fix round.

## Task 8c

Production follows the author's STALE-1 answer A (d-jwpwe7), R11-B with stat-clean files at git's index blob and the stated conversion-history exception, while the gate and `add` read every file exactly.
CONV-1 is recorded as d-egknpk.
The report is `2026-10-31-lodge-at-scale/task-8c-report.md`.
The R11-B scratch alternative's new-store, one-edit identity at `s90000` measured 0.485094 s best of three in the initial diagnostic, above Task 8c's 0.45 s reporting threshold; the final rerun measured 0.448099 s, just below it.
The report gives every stage's share and all final samples.
Production runs R11-B; the `core.autocrlf=input` rows are reported separately, with the targets and Task 12 stop unchanged.


## Task 9c fix round and Task 10a dispatch

Task 9c review: `2026-10-31-lodge-at-scale/task-9c-review.md`, copied from the dispatched review.
M1 to M5 are addressed: pair-membership mutation coverage, a table-size scan threshold, partial scan hits on SQL failure, the settings digest hand-off, and the test/report clean-up.
The 1,000-key lookup against a full 278,177-row table measured 0.229595 s before and 0.004688 s after, best of three; the compiled repeat gave 0.005364 s after.
Evidence and the gate are in `2026-10-31-lodge-at-scale/task-10a-report.md`.
Task 10a is NEEDS_CONTEXT before its interface skeleton: Step 3a requires the caller's tree file count, but the specified writer signatures do not carry it and Task 10b preserves them.
The report gives the exact interface question; no Task 10a implementation or timing claim is made.

## Task 10a

The coordinator resolved the earlier NEEDS_CONTEXT interface question: every writer requires keyword-only `files: int`, the caller's tree file count.
The plan's interfaces and Task 10b hand-off are amended with the implementation.
SECOND-1 is built to d-n65rhr, with the identity port used by production R11-B unchanged.
Task 10a adds stored reads for `show`, `waiting`, `threads`, and `thread`, a marker on first sight, and the complete keep after successful output flush on second sight.
Immutable units, transactional state replacement and eviction, epoch recovery, and cap checks for every writer are covered by fault and concurrency tests.
The final gate passes 2,076 tests, with six skipped, plus Ruff, strict mypy, Vulture, and `lodge check --gate`.
All 216 indexed CLI replay samples match the exact reader's stdout, stderr, and exit status.
The report is `2026-10-31-lodge-at-scale/task-10a-report.md`, with the red output, the gate, provisional timings, complete-keep phases, cap occupancy, and ten-cycle clears.
The eventual seen and changed targets are still missed at s90000; d-26e6zj leaves the stop to Task 12.


## Task 8c fix round before Task 10b

The review is copied to `2026-10-31-lodge-at-scale/task-8c-review.md`.
A1 preserves all files at depth 1,100 through an iterative walk and constant descriptor use, including under a 128-descriptor soft limit.
B1 fixes the property sequence's removed-source CRLF history and makes F10 edit its target before swapping it for a FIFO.
The final scratch R11-B source passes the property and FIFO tests twenty times each; all four property mutants fail independently.
M1 to M6 are addressed; `unlistable` stays because the plan's walk interface requires it, rather than being removed as the review suggested.
Production runs R11-B and takes stat candidates through the grouped git commands; the R11-A branch is removed.
The final gate passes 2,081 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
Red evidence, the proof, diagnostic timing, and concerns are in `2026-10-31-lodge-at-scale/task-10b-report.md`.
Task 10b is NEEDS_CONTEXT before its skeleton: may its file scope include `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` to wire search and complete Task 10a's extracted-module hand-offs?
No Task 10b implementation or search timing is claimed while that question is pending.

## Task 10b

The coordinator resolved the Task 10b file-scope question: `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` are authorised for their named hand-offs.
The dispatch's general hand-off rule also covers the search output flush in `cli/commands.py` and the extracted property-test helper; Task 10b's Files list is amended with the code.
Schema 4 adds immutable FTS5 words rows sharing parse rowids, including transactional recovery across clears, and indexed search uses core's existing ranking and phrase rules.
The indexed search filters historical units by the current state's parse key, includes code families and citers, and falls back for function-word queries, unavailable FTS5, and incomplete cached data.
Search honours SECOND-1 after its successful output flush, and the identity port used by production R11-B is unchanged.
The report is `2026-10-31-lodge-at-scale/task-10b-report.md`, including each new test's red evidence, the gate, the search replay timings, and concerns.
The final gate passes 2,105 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
All 108 timed search replay samples match the exact reader's stdout, stderr, and exit status, across all three sizes and both modes.
Production R11-B with the 1,900-byte cap holds four complete states at s90000; the 1,500-byte comparison clears are reported as cold, and the production seen targets remain missed.
The cap, targets, and Task 12 stop are unchanged; Task 6 M1's kept-state candidate word-set rebuild is replaced by FTS.


## Task 10a fix round before Task 10c

The dispatched review is copied to `2026-10-31-lodge-at-scale/task-10a-review.md`.
The coordinator's I-1 ruling is built: states share immutable content-addressed bucket blobs through per-state pointers; replacement and eviction collect only blobs with no remaining pointer, transactionally.
M-1 to M-4 and M-6 are fixed; M-5's termination window remains documented, as the review permits.
Marker and parse-only clears retain the complete used parse set, and unknown refs use proven absence while damaged buckets fall back.
The final gate passes 2,135 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
With shared buckets and FTS, the second s90000 state adds about 8.39 MB; four complete states fit under the production 1,900-byte cap.
DISK-1 is settled by d-j51qmy, and production R11-B / 1,900 clears zero times in the ten edit/read/read/read cycles.
The 1,500-byte comparison's clearing reads remain cold, following Task 10b's wording; production uses 1,900 bytes per file.
The red evidence, gate, space measurements, and concerns are in `2026-10-31-lodge-at-scale/task-10c-report.md`.


## Task 10c

Changed indexed reads take the published snapshot's own immutable facts by ident, while still assembling both snapshots and running the full change check.
Only current `derive` and `check_state` run on a facts hit; missing published statuses are derived without running published `check_state`.
First-sighting markers store published statuses only (d-k194gk narrows d-dxqxsn), including used hits for epoch recovery; later state evictions leave facts intact.
The exact readers and gate still use only the parse cache.
The required `Checked`, facts-conversion type, and unencodable-key adapter hand-offs are included in the amended Files list.
The final gate passes 2,149 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
All 48 s90000 changed-mode replay samples match the exact reader's stdout, stderr, and exit status; all clear the over-cap baseline and are reported as cold.
The no-clear `show A` phase probe measures 8.415025 s with published facts and 9.672830 s without, best of three, under the R11-A comparison.
Only the published ident stores facts, a 3,329,566-byte status map on the s90000 fixture, with no dirty-ident growth (d-k194gk).
DISK-1 is answered by d-j51qmy, the facts policy by d-k194gk, and the Task 12 stop remains in effect.
The complete implementation, red evidence, gate, phase table, replay table, and concerns are in `2026-10-31-lodge-at-scale/task-10c-report.md`.


## Task 10b fix round before Task 11

I1 separates query fallback from damaged state data, and I2 ignores historical candidates absent from current state rows.
The regression suite counts zero keeps and unchanged epochs over six repeated searches, including a real deleted record file.
M1 retains the CRLF property history and compares parsed texts; M2 fetches only shown parses for empty searches; M3 uses proven exact-ID absence; M5 repeats 300 queries against SQLite with non-ASCII and numeric words.
The Task 11 fix round settles M4 through DISK-1 (d-j51qmy), 1,900 bytes per file and four states, and M6 through STALE-1 (d-jwpwe7), production R11-B in every test run.
STALE-1 (d-jwpwe7): the four test_removed_attributes_agree parameters become the unskipped test_removed_attributes_follow_the_index; test_every_file_read_without_a_conversion_source is removed; test_r11a_does_not_compute_git_candidates becomes test_production_uses_stat_candidates; test_folders.py's R11-A-only base-name assertion becomes the production no-base-names assertion.
The Task 10b Files list includes the extracted lookup helper and review regressions.
The full gate passes 2,158 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
Evidence and validation are in `2026-10-31-lodge-at-scale/task-11-report.md`.

## Task 11

The author resolves STALE-1 through d-jwpwe7: no-base-names and no-mapping folder hits are the production R11-B rule, and the R11-A full-file branch is removed.
FOLD-1 is read as d-eg5nra, and no record operation is run.
The folder cache and construction hand-offs use production R11-B, with no test switch or STALE-1 skips; rows and their completeness counts are scoped to the checkout's absolute git dir, under schema 8.
The task's Files list includes its required schema, construction, committed-helper extraction, disk-listing, and test hand-offs.
The Task 11 fix-round frozen gate passes 2,228 tests, with two skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`; collection changes from 2,254 to 2,230 after removing obsolete and duplicate cases and adding thirteen regressions.
The production R11-B property runs pass, and supported FUSE cases agree with the exact reader.
All 96 native 160,800-file replay samples match the exact reader's stdout, stderr, and exit status; all 78 indexed samples retain a kept state and an unchanged epoch.
Production R11-B takes no base names or full mapping on a hit; the final isolated s90000 new-commit identity is 0.555728 s, and a cold index is 0.532518 s, best of three with fifteen git processes each, including store construction.
Production R11-B misses the seen target, and broad searches remain above their target; the refreshed s90000 measurements are in the Task 12 tables.
Production runs R11-B (d-jwpwe7), with 1,900 bytes per file and four kept states (d-j51qmy); the recorded Task 12 stop remains in effect.
The report records the red evidence, full timings including conversions, FUSE capability skips, and the incomplete construction-signature skeleton as a process deviation.
Initial evidence is in `2026-10-31-lodge-at-scale/task-11-report.md`, and the completed fix round, all red evidence, and the 1,500-level hit improvement from 2.929157 s to 0.123253 s are in `2026-10-31-lodge-at-scale/task-11-fix-report.md`; Task 11 is ready for recheck.


## Task 10c fix round before Task 12

B-2 restores the no-write path for empty parse misses, with over-cap exact-command regressions for spec, check, gate, and dry-run add.
B-1 resolves ID-shaped codes after proven ID absence, including ambiguity, at app and end-to-end levels.
I-1 kills the swapped-status mutant; I-2 follows the dispatch's status-only published-facts policy, removes dead dirty identities, and skips published state checks on indexed reads.
M-2 requires thread IDs, M-3 pins exact-reader independence from poisoned facts, and M-4 documents the facts-backed constructor.
M-1 is ruled not fixed: damage requires an edit of the index file, reads stay exact through memory fallback, and the index is safe to delete.
The amended Task 10c Files list covers the value-shape, lookup, schema, and fixture hand-offs.
Red evidence, gate results, and Task 12 measurements are in `2026-10-31-lodge-at-scale/task-12-report.md`.
The final frozen gate passes 2,208 tests, with 39 skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.


## Task 12

The replay adds chained distinct edits with epoch observations, isolated git configuration, and best-of-nine start-up measurements with the selected build's Python.
Seen and changed baselines prime both SECOND-1 sightings, and the README documents index removal and LODGE_INDEX=off.
The task's Files list includes the replay regression file and timeout-test hand-off.
The seven new regression tests run red before implementation, with failing output in `2026-10-31-lodge-at-scale/task-12-report.md`.

The completed matrix covers s900, s9000, and s90000, both R11 rules, and both 1,500-byte and 1,900-byte caps, with every targeted row under each combination.
All 1,602 timed replay samples match the exact reader's stdout, stderr, and exit status.
The initial audit checks 360 cycle reads, 216 phase samples, three in-place clears, and all 100 chained reads; the final production rerun independently checks 195 replay samples, 90 cycle reads, and 51 phase samples.
At 160,800 files, both 1,500-byte variants fit zero complete states within the cap and clear ten times in ten edit/read/read/read cycles; both 1,900-byte variants fit four states and clear zero times.
The R11-A / 1,500 hundred-read chained comparison clears once, since each edited state is read only once.
The initial R11-A / 1,500 full-state clear is 0.078891 s best of three, on SQLite 3.53.1, with unchanged inode and physical size.

R11-A/1,500: STOP; seen show-by-code is 2.002969 s and the second changed sighting is 12.010507 s.
R11-A/1,900: STOP; seen show-by-code is 2.008090 s, and the first and second changed sightings are 6.134215 s and 11.660802 s.
R11-B/1,500: STOP; seen show-by-code is 0.481090 s and the second changed sighting is 10.735255 s.
R11-B/1,900: STOP; refreshed final-code seen show-by-code is 0.318994 s, and the first and second changed sightings are 4.763202 s and 10.246784 s.
Cold clears are excluded; broad searches and CONV-1 conversion rows are reported separately.
The server question goes to the coordinator under every combination; Task 12 builds no server.

During measurement, d-jwpwe7 rules STALE-1 for R11-B, and d-j51qmy rules DISK-1 for 1,900 bytes per file.
The chosen combination is remeasured on final code with a refreshed index and still triggers the stop, with seen show at 0.318994 s.
The Task 11 fix round applies both rulings to production, and the Task 12 fix round replaces its s90000 rows in place with refreshed final-code measurements; the stop remains in effect.
The Task 1 base completes 210 of 288 bounded attempts, with 78 large-store timeouts and no unexpected completed differences.
Its CPython 3.13.5/SQLite 3.47.1 runtime differs from the completed-build native CPython 3.13.16/SQLite 3.53.1 runtime, so no code-only speed-up ratio is claimed.
The supplemental thread read covers a not-found answer; successful-thread timing and the optional FUSE timing are unavailable on these synthetic stores.
The refreshed phase table, candidate counts, occupancy, output audit, runtime verification, and limitations are in `2026-10-31-lodge-at-scale/timings.md` and `2026-10-31-lodge-at-scale/task-12-report.md`.
The final fix-round frozen whole gate exits 0: formatting, Ruff, strict mypy over 301 files, Vulture, 2,236 tests passed and two skipped in 211.06 s, and `lodge check --gate` prints `ok` with its existing area-order note.
Task 12 and the dispatched Task 11 recheck fixes are complete and ready for review, with the server question handed to the coordinator; the item-by-item evidence is in `2026-10-31-lodge-at-scale/task-12-fix-report.md`.


## Final review fix round

The scrubbed whole-branch review is `2026-10-31-lodge-at-scale/final-review.md`, committed first as cc282be.
PUB-1 is already fixed by e346776.
DEC-1, DEC-2, STAT-1, DOC-1, and DOC-2 align the current plan and README with d-cqr414, d-3ck8km, d-bbhak7, and the built task steps.
FIX-1 adds persisted-row codec coverage, and TEST-1 checks the WAL before truncation independently of the secure-delete default.
Both mutants fail and are reverted; the item evidence and final gate are in `2026-10-31-lodge-at-scale/final-fix-report.md`.
The final frozen gate exits 0: formatting, Ruff, strict mypy over 301 files, Vulture, 2,238 tests passed and two skipped in 212.54 s, and `lodge check --gate` prints `ok` with its existing area-order note.
