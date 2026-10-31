---
id: d-t3afj1
kind: decision
title: "Index units are immutable, states own only their rows, a cap rebuilds, transactions are explicit"
scope: process
decided_by: coordinator
date: 2026-10-31T23:27:15+01:00
replaces: [d-6hb3yd]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "0.5 to 0.8 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-2.md, V2"}
---

Parse units and their words rows are content-addressed and immutable: written once, never deleted by an eviction.
Evicting a state deletes only its own rows.
Past a size cap derived from SCALE-1, the next writer rebuilds the index into a new file swapped in by rename.
Connections use `isolation_level=None` and WAL; every read runs inside one explicit transaction; a state is re-kept under its key only by replacing it in one write transaction.
Readers treat anything incomplete as a miss and read in memory.

## Reasoning

The third recheck of the index's consistency (V1 to V3) found eviction by reference still able to drop a unit a kept state needs, its mechanism costing 0.5 to 0.8 s per changed read, and reads that were not one transaction under Python's default `sqlite3` behaviour; removing deletion of shared rows removes the class.
FTS rows, if any are ever deleted, go by rowid only; with immutable units none are.
The coordinator's ruling for the third fix round; it replaces d-6hb3yd, whose fault-injection tests stay.
Cost if wrong: the index grows to its cap between rebuilds.
