---
id: d-srfxj8
kind: decision
title: "The export batches its writes in app, at most one commit a minute"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "285", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:285"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 4"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
---

`app`'s `Exporter` is told of each write and runs the export at once when the last commit is a minute old or more, otherwise when that minute ends, so writes in between go out in one commit; after a refused push or a failure it tries again a minute later, and the server flushes it once on start.
The export holds every record, area, thread, and attachment, and the two `.gitkeep` files that `lodge init` lays down.

## Reasoning

The design batches the export to at most one commit a minute after writes (design line 285).
`core` and `app` take the time through ports (`CLAUDE.md`, "Structure checks"), and plan 1's call rules refuse `setTimeout` there (plan 1, Task 3), so the waiting is a timer port the composition root fills, and the tests drive a fake clock and timer.
An unchanged tree makes no commit (probe 4 of the plan's `probes.md`), so a flush on start is safe and exports what a stopped server left pending.
lodge 0.2's store has `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep` from `init` (`src/lodge/gitstore/trees.py:10`), and `load` skips them (`src/lodge/core/snapshot.py:68`), so the importer drops them and the export writes them back, giving the layout of a fresh 0.2 store.
Cost if wrong: a write waits up to a minute to reach git; a ticking export instead is a change inside one class.
