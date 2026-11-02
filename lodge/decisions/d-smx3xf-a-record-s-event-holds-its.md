---
id: d-smx3xf
kind: decision
title: "A record's event holds its path and its file text as lodge 0.2 writes it"
scope: process
decided_by: planner
date: 2026-11-02T14:10:34+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "446", handle: "grep -h '^def test_' tests/core/test_*.py | wc -l"}
  - {value: "30-49", handle: "src/lodge/core/snapshot.py:30-49"}
---

On the server an event that writes a record holds the record's path and its whole file text, exactly as lodge 0.2 writes it; the core keeps checking states given as files (`Tree`), and the tables built from the events parse those texts.

## Reasoning

lodge 0.2's core loads and checks a state given as path and text (`Tree`, `load`, `src/lodge/core/snapshot.py:30-49`), and its 446 core tests build their states that way, so the core and its tests carry over without a second form of record.
The export writes "what a lodge 0.2 store holds ... in today's file layout" (design, "Export to git"), and the importer reads a 0.2 store (design, "Moving from lodge 0.2"); with the file text as the event, both move texts unchanged and need no conversion that could drift.
Structured events would need a schema per record kind, a second serialisation, and a conversion both ways, each one more place to differ from 0.2.
The tables built from the events can still hold parsed fields for queries, since every other table "can be rebuilt" (design, "The model").
Cost if wrong: moving to structured events later is a new event kind and a rebuild of the tables from the old events, the append-only table kept.
