---
id: d-wje1cn
kind: decision
title: "Events hold file bytes, and a write is a compare-and-set on the project's newest event"
scope: process
decided_by: planner
date: 2026-11-02T19:05:29+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 1"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 2"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 3"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 4"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 8"}
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
---

The store keeps one append-only `events` table; a write is one `file` event per path holding the file's bytes in a `blob`, through `encodeUtf8` and `decodeUtf8` of the core's `text.ts`, which follow `surrogateescape`, d-0q54zn's codec becoming this plan's.
A project's revision is the `seq` of its newest event, and `publish` opens its transaction with a compare-and-set on it, rejecting a stale base; one function fills the derived tables on a write and in `rebuild`.

## Reasoning

A `text` column drops a leading U+FEFF and corrupts a lone surrogate with the character after it, while a `blob` gives the bytes back exactly (the plan's probes 1 and 2), so a file's text survives only as bytes.
d-smx3xf has a record's event hold its path and its file text as lodge 0.2 writes it; the bytes are what a git blob of lodge 0.2 holds (`encode` in `src/lodge/gitstore/trees.py`), so the export writes them unchanged.
Two connections on one file fail a transaction that reads and then writes after the other commits, and a compare-and-set as the first statement fails nothing (probe 4); an update that leaves the revision as it is still counts the row it matched (probe 8).
Triggers refuse an update and a delete of an event with their message (probe 3).
One function for a write and for `rebuild` keeps the derived tables equal to a replay of the events, the design's rule that every other table "can be rebuilt" (design, "The model").
Cost if wrong: another event shape is a new event kind and a rebuild of the derived tables, the old events kept.
