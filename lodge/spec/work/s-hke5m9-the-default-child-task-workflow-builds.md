---
id: s-hke5m9
kind: spec
title: "The default child task workflow builds reviews and rechecks"
rests_on: [s-tprwhs, s-d1dd20, s-pks1qn]
---

From build step 5, child tasks run in order on the plan's branch.
At `build`, lodge starts a builder who takes a brief, plan, and mock, and gives a report; the checklist is failing test seen, tests pass, committed, and pushed.
A reviewer gives a review, advancing with no findings above Minor or returning to a builder's `fix`.
Fix continues to `recheck`, where a rechecker supplies a review, advancing with no findings above Minor or returning to fix.
