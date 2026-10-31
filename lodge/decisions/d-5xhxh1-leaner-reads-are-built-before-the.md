---
id: d-5xhxh1
kind: decision
title: "Leaner reads are built before the index"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The plan builds the leaner reads (multi-ref `show`, code families, phrases, multi-query `search`, brief lines, the reading guide) before the index, after the four speed tasks.

## Reasoning

The index's search only supplies candidates to core's ranking (d-eby5pb), so core's ranking must already be the final one when the index is built; building the index first would implement today's ranking and then change it.
Ruling 2 of the brief orders the speed work only, which the plan keeps.
Cost if wrong: the index lands three tasks later than it could.
