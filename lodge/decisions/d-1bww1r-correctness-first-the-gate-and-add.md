---
id: d-1bww1r
kind: decision
title: "Correctness first: the gate and add keep their full semantics on every store"
scope: process
decided_by: coordinator
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The gate (`lodge check --gate`) and `lodge add` keep their full semantics on every store.
No speed or scale change alters a check's result, a problem's wording, or a published state's comparison, except where a task says so and records it as a product decision with a spec edit.

## Reasoning

The brief for lodge at scale, ruling 1, binding on the plan.
s-q4s548 forbids showing wrong information, and s-edgt71 has reads run every check, so a faster read that changed a check's result would break both.
Cost if wrong: none to correctness; some speed-ups are given up where their equivalence cannot be shown.
