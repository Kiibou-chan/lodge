---
id: d-vmpspc
kind: decision
title: "Tasks 8 and 10 are split so each part builds and reviews on its own"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The plan splits Task 8 and Task 10 as both reviews suggest, each part buildable and reviewable on its own.

## Reasoning

The correctness review's I8 and the feasibility review's findings on Tasks 8 and 10: a port change and the identity's correctness surface in one diff hide defects in renaming noise.
The coordinator's ruling 6 for the fix round.
Cost if wrong: more task boundaries, each with its own review.
