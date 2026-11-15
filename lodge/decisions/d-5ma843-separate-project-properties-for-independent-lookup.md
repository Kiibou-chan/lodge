---
id: d-5ma843
kind: decision
title: "Separate project properties for independent lookup"
scope: product
decided_by: coordinator
date: 2026-11-15T05:39:24+01:00
changes:
  - {entry: s-g8m3qv, action: edit}
  - {entry: s-mn4xj9, action: create}
  - {entry: s-sge25h, action: create}
  - {entry: s-ts16f0, action: create}
  - {entry: s-3y79d0, action: create}
narrows: [d-sk1r7r]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
---

Separate project properties for independent lookup.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:85.
The project aggregate, export target, workflow, repository links, and membership deserve separate lookups.
This narrows only d-sk1r7r, preserving its other model claims.
All original event-store prerequisites remain.
Build steps follow the design's Build order, not an inferred implementation order.
No other looks-related decision is replaced or narrowed.
