---
id: d-me8vm3
kind: decision
title: "Broad searches are measured apart; whether the target covers them is the coordinator's call"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "5,000", handle: "this decision"}
  - {value: "0.3 s", handle: "the brief's ruling 3"}
  - {value: "107,247", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-codex.md, F6"}
  - {value: "0.72 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-codex.md, F6"}
  - {value: "60", handle: "scripts/bench_store.py, WORDS"}
---

The timing table reports searches with more than 5,000 candidates apart, with their candidate counts, and the plan's stop rule applies to the other reads; whether the 0.3 s target covers broad searches goes to the coordinator.

## Reasoning

The feasibility review's F6: scoring and sorting 107,247 candidates of `berth crane` took 0.72 s in memory before any index work, and the synthetic stores' 60-word vocabulary makes most words match most records.
Ranking from the index's stored word sets removes the re-tokenising, but no exact ranking of a hundred thousand records fits 0.3 s in one Python process.
Cost if wrong: the target is read as covering what it cannot.
