# Ledger: lodge at scale, plan docs/superpowers/plans/2026-10-31-lodge-at-scale.md

Branch `read-speed`, based on `search-brief` (d-fqymzm); the brief is `2026-10-31-lodge-at-scale/brief.md`.
Briefs, reports, and reviews: `docs/superpowers/plans/2026-10-31-lodge-at-scale/`.

The coordinator's rulings for this plan, recorded: correctness first (d-1bww1r), the speed order (d-1ftgg3), the index and its targets (d-232gxs), leaner reads (d-3g6ard), benchmarks (d-542m5g).
The planner's calls, recorded: d-5xhxh1, d-5zqvxb, d-8kq2nk, d-atsx8n, d-c400w8, d-c4w7xy, d-eby5pb, d-f3r5aq, d-hf2fms, d-kj554d, d-m0g9tx, d-n9w4by, d-p60ka9, d-s2ypth, d-zyqzkg; d-5xhxh1 and d-hf2fms were edited before publishing, through `lodge draft` and `lodge add`, to name decision IDs where their first text named draft labels.
The coordinator's constraint on unwritable and locked indexes is d-kj554d and Task 9's failure-mode tests.
For the author: SCALE-1 in `questions.md`, the index's disk space.
Plan written; probes and their output in `plan-report.md` and `probes/`.
Plan reviewed: `plan-review-opus.md` (2 Blocking, 8 Important, 8 Minor) and `plan-review-codex.md` (1 Blocking, 16 Important, 1 Minor).
Fix round 1 (`plan-fix-1.md`): every finding taken, none parked; Task 8 split into 8a and 8b, Task 10 into 10a, 10b, and 10c.
The coordinator's rulings for fix round 1, recorded: d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, d-ytf272.
The planner's calls for fix round 1, recorded: d-7e8zhd, d-ana6c0, d-c5a1y4, d-dqpf59, d-dxqxsn, d-emtwbs, d-faakge (replacing d-f3r5aq), d-her016, d-me8vm3, d-26e6zj.
Plan rechecked: `plan-recheck-opus.md` (all 18 fixed; N1 to N4 Important, N5 to N9 Minor) and `plan-recheck-codex.md` (13 fixed, 4 partly; R1 to R4 Important, R5 Minor).
Fix round 2 (`plan-fix-2.md`): every finding taken, none parked; the index's invariants in the Global Constraints, tested by fault injection.
The coordinator's ruling for fix round 2, recorded: d-6hb3yd.
The planner's calls for fix round 2, recorded: d-c0q20c, d-aej8rs, d-9r24jc, d-4n5tr6, d-gd00c6.
The coordinator's ruling on broad searches, recorded: d-hxmdkz (narrows d-gd00c6), their own stop at 1.0 s warm; the 0.3 s stop covers the point reads and searches with at most 5,000 candidates.
Open with the author: SCALE-1; the plan keeps four states as the one constant `KEPT_STATES` until she answers (d-ytf272).
Rechecked again: `plan-recheck-2.md` (V1 to V3 Important, V4 to V8 Minor).
Fix round 3 (`plan-fix-3.md`): every finding taken, none parked; the index's consistency rewritten so nothing a kept state depends on is ever deleted.
The coordinator's ruling for fix round 3, recorded: d-t3afj1 (replaces d-6hb3yd).
The planner's calls for fix round 3, recorded: d-4j98ph (replaces d-aej8rs), d-gvz66f, d-n6tqzq.
The index's size cap follows SCALE-1's option A through `INDEX_BYTES_PER_FILE`; her answer changes that one constant.
Rechecked a third time: `plan-recheck-3.md` (R1 Blocking, R2 and R4 Important, R3 and R5 Minor).
Fix round 4 (`plan-fix-4.md`): every finding taken, none parked; generations dropped for one file per build, cleared in place.
The coordinator's ruling for fix round 4, recorded: d-e3stjn (replaces the generations of d-gvz66f).
The planner's call for fix round 4, recorded: d-c6cegr.
SCALE-1 answered by the author: A (d-4pbeax).
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
Decisions to record before building: R11-A or R11-B (STALE-1, with the author) and CONV-1 before Task 8c; FOLD-1 before Task 11 (the task records it); SECOND-1 before Task 10a; none before Task 9c, 10b, 10c, or 12.

## Task 8c

Built with the dispatch's interim R11-A full-file rule; STALE-1 remains with the author, and no R11 decision is inferred.
CONV-1 is recorded as d-egknpk.
The report is `2026-10-31-lodge-at-scale/task-8c-report.md`.
The R11-B scratch alternative's new-store, one-edit identity at `s90000` measured 0.485094 s best of three in the initial diagnostic, above Task 8c's 0.45 s reporting threshold; the final rerun measured 0.448099 s, just below it.
The report gives every stage's share and all final samples.
The production R11-A and the `core.autocrlf=input` rows are reported separately, with the targets and Task 12 stop unchanged.


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
SECOND-1 is built to d-n65rhr, with Task 8c's interim R11 identity port unchanged.
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
Production retains interim R11-A and now skips the candidate git group entirely; the alternative remains one function body away.
The final gate passes 2,081 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
Red evidence, the proof, diagnostic timing, and concerns are in `2026-10-31-lodge-at-scale/task-10b-report.md`.
Task 10b is NEEDS_CONTEXT before its skeleton: may its file scope include `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` to wire search and complete Task 10a's extracted-module hand-offs?
No Task 10b implementation or search timing is claimed while that question is pending.

## Task 10b

The coordinator resolved the Task 10b file-scope question: `app/lodge.py`, `gitstore/index_schema.py`, `gitstore/index_space.py`, and `tests/app/fake_index.py` are authorised for their named hand-offs.
The dispatch's general hand-off rule also covers the search output flush in `cli/commands.py` and the extracted property-test helper; Task 10b's Files list is amended with the code.
Schema 4 adds immutable FTS5 words rows sharing parse rowids, including transactional recovery across clears, and indexed search uses core's existing ranking and phrase rules.
The indexed search filters historical units by the current state's parse key, includes code families and citers, and falls back for function-word queries, unavailable FTS5, and incomplete cached data.
Search honours SECOND-1 after its successful output flush, and Task 8c's interim identity port is unchanged.
The report is `2026-10-31-lodge-at-scale/task-10b-report.md`, including each new test's red evidence, the gate, the search replay timings, and concerns.
The final gate passes 2,105 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
All 108 timed search replay samples match the exact reader's stdout, stderr, and exit status, across all three sizes and both modes.
The larger stores' kept working sets exceed the production cap with FTS, so their changed samples clear and are reported as cold; the seen targets remain missed at `s90000` with interim R11-A.
The cap, targets, and Task 12 stop are unchanged; Task 6 M1's kept-state candidate word-set rebuild is replaced by FTS.


## Task 10a fix round before Task 10c

The dispatched review is copied to `2026-10-31-lodge-at-scale/task-10a-review.md`.
The coordinator's I-1 ruling is built: states share immutable content-addressed bucket blobs through per-state pointers; replacement and eviction collect only blobs with no remaining pointer, transactionally.
M-1 to M-4 and M-6 are fixed; M-5's termination window remains documented, as the review permits.
Marker and parse-only clears retain the complete used parse set, and unknown refs use proven absence while damaged buckets fall back.
The final gate passes 2,135 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
With FTS, the second s90000 state's added space falls from 59.59 MB to 8.39 MB, but zero complete states fit under the current cap at s9000 or s90000.
Both layouts clear ten times in ten edit/read/read/read cycles at both sizes; the cap stays unchanged pending DISK-1.
The larger stores' kept working sets exceed the production cap with FTS, so their clearing changed reads are cold, following Task 10b's wording.
The red evidence, gate, space measurements, and concerns are in `2026-10-31-lodge-at-scale/task-10c-report.md`.


## Task 10c

Changed indexed reads take the published snapshot's own immutable facts by ident, while still assembling both snapshots and running the full change check.
Only current `derive` and `check_state` run on a facts hit; missing, invalid, or incomplete facts are computed in full.
First-sighting markers store current and published facts, including used hits for epoch recovery; later state evictions leave facts intact.
The exact readers and gate still use only the parse cache.
The required `Checked`, facts-conversion type, and unencodable-key adapter hand-offs are included in the amended Files list.
The final gate passes 2,149 tests, with six skipped, plus formatting, Ruff, strict mypy, Vulture, and `lodge check --gate`.
All 48 s90000 changed-mode replay samples match the exact reader's stdout, stderr, and exit status; all clear the over-cap baseline and are reported as cold.
The no-clear `show A` phase probe measures 8.415025 s with published facts and 9.672830 s without, best of three, under interim R11-A.
A new current ident adds 3,329,571 JSON value bytes of facts on that store; a published-facts miss adds 6,659,142 in all.
DISK-1, the unchanged cap's inability to fit one complete state with words, W6's deferred facts policy, and the Task 12 stop remain as reported.
The complete implementation, red evidence, gate, phase table, replay table, and concerns are in `2026-10-31-lodge-at-scale/task-10c-report.md`.
