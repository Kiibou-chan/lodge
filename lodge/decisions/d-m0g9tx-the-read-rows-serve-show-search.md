---
id: d-m0g9tx
kind: decision
title: "The read rows serve show, search, waiting, threads, and thread; everything else reads in memory"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "2 s", handle: "the estimate in the plan's table, from probes/phases.py and probes/gc_derive.py"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

The stored read rows serve `show`, `search`, `waiting`, `threads`, and `thread`; `spec`, `timeline`, `draft`, `check`, `mint`, `add`, the gate, and the viewer build the snapshot in memory from the parse cache.

## Reasoning

These five are what agents read with (the brief, evidence item 5, and `src/lodge/cli/guide.md`, Reading), and they need one record or a short list; `spec` and `timeline` print whole stores, and the viewer needs each record's threads, rests-on tree, and supports (`src/lodge/app/results.py`, `Shown`), which rows would have to duplicate.
Cost if wrong: the viewer and `spec` stay at the in-memory cost, about 2 s at 160,000 files after the speed tasks.
