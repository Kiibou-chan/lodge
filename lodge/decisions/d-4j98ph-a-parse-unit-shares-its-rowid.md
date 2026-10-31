---
id: d-4j98ph
kind: decision
title: "A parse unit shares its rowid with its words; a state stores citers for every code and family root"
scope: process
decided_by: planner
date: 2026-10-31T23:27:17+01:00
replaces: [d-aej8rs]
narrows: [d-dxqxsn, d-eby5pb]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A parse unit is a parse row and the FTS words row with the same rowid, inserted together once and never deleted outside a rebuild; the FTS table has no key column.
Facts are keyed by ident and are immutable likewise.
Each state stores a citer row for every code and every prefix of one ending before a `.`, newest first; `cites` is defined through `core.code_tokens`.

## Reasoning

The coordinator's ruling d-t3afj1 of the third fix round, and the recheck's V5 (a family root with no record of its own had no citer row) and V7 (an indexed key column matches path words).
Cost if wrong: more citer rows per state.
