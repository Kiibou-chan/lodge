---
id: d-26e6zj
kind: decision
title: "The stop on the targets comes after the folder cache"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "81 ms", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-codex.md, Verification"}
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
---

The stop for missed targets applies after Task 11, when every planned optimisation has landed; the measurements of Tasks 10a to 10c are provisional.

## Reasoning

The feasibility review's F17: Task 10's warm read would still list every folder, about 81 ms at 159,716 files, which Task 11 removes, so a stop there would come before the step that passes it.
Cost if wrong: a later stop.
