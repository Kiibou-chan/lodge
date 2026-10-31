---
id: d-aej8rs
kind: decision
title: "A parse and its words are one unit; a state owns its rows, answers, facts, and citers"
scope: process
decided_by: planner
date: 2026-10-31T23:07:57+01:00
narrows: [d-n9w4by, d-dxqxsn]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "0.294 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-codex.md, R2"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

A parse row and its words row are written and dropped together.
A state is published in one transaction, behind its completeness marker, with its rows, answers, citers, facts, and every parse unit it references; its eviction drops, in one transaction, what no kept state still uses.
Each state stores every code's citers newest first, so `show` and code searches never scan texts; `cites` is defined through `core.code_tokens`, so stored and in-memory citers agree.

## Reasoning

The coordinator's ruling on the index's consistency, and the rechecks' N3, N4, R1, R2, and N6.
A full scan for citers took 0.294 s at 160,000 files in an advisor's measurement, before any other phase of a read.
Cost if wrong: parse units of states no longer kept are parsed again after a revert.
