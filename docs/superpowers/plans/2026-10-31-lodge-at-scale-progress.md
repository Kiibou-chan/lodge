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
