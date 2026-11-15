---
id: s-0tn1e8
kind: spec
title: "The default plan workflow runs from mock to authorised merge"
rests_on: [s-tprwhs, s-h4x7bx]
---

From build step 5, the default `plan` workflow follows lodge's build process with mocking before planning.
The owner supplies a mock and a go; the planner takes the mock and supplies a plan.
A reviewer supplies a plan review, advancing with no findings above Minor or returning to `plan-fix`, where the planner returns it to `plan-review`.
The build step waits until every child is done.
A reviewer supplies the whole-branch review, advancing with no findings above Minor or returning to a builder's `fix`, which returns to review.
The owner gives the go at merge.
