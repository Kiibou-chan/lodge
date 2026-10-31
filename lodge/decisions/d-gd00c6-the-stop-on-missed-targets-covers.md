---
id: d-gd00c6
kind: decision
title: "The stop on missed targets covers broad searches until the coordinator rules otherwise"
scope: process
decided_by: planner
date: 2026-10-31T23:08:00+01:00
narrows: [d-me8vm3]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "5,000", handle: "d-me8vm3"}
  - {value: "0.3 s", handle: "d-232gxs"}
---

Searches with more than 5,000 candidates are still reported apart with their counts, and the stop after Task 11 applies to them too: above 0.3 s, the phase table and the server question go to the coordinator.

## Reasoning

The feasibility recheck's F6: leaving coverage open lets the build finish with broad searches over the target and the stop met; keeping the original target until the coordinator narrows it closes that.
Cost if wrong: the stop fires on broad searches alone, and the coordinator decides then.
