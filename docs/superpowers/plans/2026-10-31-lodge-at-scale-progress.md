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
