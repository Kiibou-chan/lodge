---
id: s-0tn1e8
kind: spec
title: "The default plan workflow runs from mock to authorised merge"
rests_on: [s-tprwhs, s-h4x7bx]
---

From build step 5, the default `plan` workflow follows lodge's build process with mocking before planning.
At `mock`, the owner supplies a mock and a go; at `plan`, the planner takes the mock and supplies a plan.
At `plan-review`, a reviewer supplies a review, advancing with no findings above Minor or returning on failure to `plan-fix`, where the planner moves on by `next` and continues to `plan-review`.
The `build` step waits until every child is done.
At `review`, a reviewer supplies the whole-branch review, advancing with no findings above Minor or returning on failure to a builder's `fix`, which continues to `review`.
At `merge`, the owner gives the go.
