---
id: d-sj6hmf
kind: decision
title: "The export batches in app through the clock's sleep, reading every file of the project"
scope: process
decided_by: planner
date: 2026-11-02T19:07:50+01:00
replaces: [d-srfxj8]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "285", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:285"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, \"Interfaces for plans 3 and 4\""}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 4"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
---

`app`'s `Exporter` exports at once after a write when the last commit is a minute old, otherwise after sleeping on the clock until that minute ends, so writes in between share one commit; it retries a minute after a failure, and the server flushes it on start.
The export holds every file of the project, attachments included, read through a function `store` adds, and the two `.gitkeep` files of `lodge init`.

## Reasoning

The design batches the export to at most one commit a minute after writes (design line 285).
`core` and `app` take the time through ports, and plan 1's call rules refuse `setTimeout` there (plan 1, Task 3); plan 2's `Clock` has `now()` and `sleep(seconds)` (plan 2, "Interfaces for plans 3 and 4"), so the exporter waits on that port and needs no timer port of its own, which d-srfxj8 named, and the tests drive plan 2's `FixedClock`, whose `slept` records each wait.
Plan 2's `Store.trees()` lists attachments without their text, so the export reads the project's files, attachments included, through a function `store` gains.
An unchanged tree makes no commit (probe 4 of the plan's `probes.md`), so a flush on start is safe; lodge 0.2's store has `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep` from `init` (`src/lodge/gitstore/trees.py:10`), which `load` skips (`src/lodge/core/snapshot.py:68`), so the importer drops them and the export writes them back.
Cost if wrong: a write waits up to a minute to reach git; a ticking export instead is a change inside one class.
