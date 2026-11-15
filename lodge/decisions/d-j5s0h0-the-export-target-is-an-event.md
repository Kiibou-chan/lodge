---
id: d-j5s0h0
kind: decision
title: "The export target is an event, a wrapped store tells the exporter, and main reads a 0.2 store"
scope: process
decided_by: planner
date: 2026-11-02T19:15:14+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at 7204ad3, \"Interfaces for plans 3 and 4\""}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at f2dcc72, Task 4"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at f2dcc72, Task 4"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
---

A project's export target is an event of a new kind, `export-target`, read back from the events by an `ExportTargets` port that `store` implements.
The composition root wraps each project's store, for `Lodge` and the import alike, in one that tells the exporter after every published write.
The server reads a lodge 0.2 store with `git`'s reader and `cli`'s reading of its `.lodge.toml`, joined in the composition root and given to `api` as a function.

## Reasoning

Plan 2 adds an event kind by a case in `applyEvent` and keeps every change an event (plan 2 at 7204ad3, "Interfaces for plans 3 and 4"), and plan 3 builds its accounts' reads from the events without a derived table (plan 3 at f2dcc72, Task 4); a target changes rarely and is read once per export, so a derived table would add a schema version for nothing.
Every write of a record goes through `Store.publish`, the agent's add, the person's approval, and the import alike (plan 2, "Interfaces for plans 3 and 4"), so one wrapper sees them all, where a call in each operation of `api` would miss the next one added.
`api` may import only `app` and `core` (plan 1, Task 3), and smol-toml is `cli`'s (plan 3, RULE-TOML), so only the composition root can join `git`'s reading of the repository with `cli`'s reading of the TOML.
Cost if wrong: a target kept in a table instead is one migration, and a missed write leaves the export a minute behind until the next one.
