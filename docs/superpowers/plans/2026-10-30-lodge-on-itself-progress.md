# Ledger: lodge on itself, plan docs/superpowers/plans/2026-10-30-lodge-on-itself.md

Branch `lodge-on-itself` from main 47dcfa7; the author's go (2026-10-30 01:02): "Start it now."
Briefs, reports, and reviews: `docs/superpowers/plans/2026-10-30-lodge-on-itself/`.
The author's standing rule: "Check usage limits after every task step and stop at 95%"; weekly usage 93% at the start.

Ruling: the plan is written by the coordinator and reviewed once by one reviewer covering both angles (correctness against the spec, then practice and design); why: the plan changes no code, every record it adds passes lodge's own gate, and the weekly budget has about 2% left before the author's stop; cost if wrong: a plan defect surfaces in a task review instead, one fix round later.
Plan review in `plan-review.md`: 1 Blocking, 9 Important, 10 Minor.
Fix round 1 by the coordinator: B1, I1, I2, I4 to I9, and M1 to M10 taken into the plan; I3 goes to the author as SPEC-1, since only she can confirm the entries or choose to leave them unprotected.
Ruling: M3, no LODGE-3 replacement; why: LODGE-4 (d-y8p15p) already narrows LODGE-3, and `lodge show LODGE-3` prints `narrowed by d-y8p15p`, which is what holds; cost if wrong: LODGE-3's "private" reads as narrowed, not replaced.
Ruling: M9, her decisions at done ledger lines 4, 217, and 220 are imported as author decisions; why: Rollout 2 puts lodge's own decisions into lodge, and a coordinator ruling that the tag waits for her go is incomplete without her go; cost if wrong: three more records.
Ruling: the coordinator makes fix round 1 itself, and Task 1 starts before a recheck; why: the fixes are plan text taken from the review's own fix lines, and Task 1 does not depend on SPEC-1; cost if wrong: a plan defect surfaces in Task 1's review.
Finding for the next code plan: the "looks related" feedback fires on a decision that changes entries (`src/lodge/core/feedback.py:144-158`), where spec:151 limits it to a decision that changes, replaces, and narrows nothing.
Task 1: complete (by the coordinator, no builder; small and mechanical): live author decisions LODGE-8 d-9vxkjw, LODGE-9 d-qbfdqt, LODGE-10 d-z8jm5y, and "Remove them completely" d-gqyp3n; imported author decisions d-3tq6cx (line 4), d-axaz9w (line 217), d-fw070q (line 220); 28 author records, reasoning equals quote for all, by script; dry-run feedback was related-decision questions (none replace or narrow) and labels read as numbers (no figures); gate ok.
