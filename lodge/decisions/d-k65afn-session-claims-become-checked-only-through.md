---
id: d-k65afn
kind: decision
title: "Session claims become checked only through lodge confirmation"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:29+01:00
changes:
  - {entry: s-4na883, action: create}
  - {entry: s-ecj6se, action: create}
  - {entry: s-j1bvy2, action: create}
  - {entry: s-4p2vsz, action: create}
  - {entry: s-7aqvsh, action: create}
  - {entry: s-gnn2ha, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
---

Session claims become checked only through lodge confirmation.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:234-243.
The interface keeps reported and checked evidence apart, following must-not 5 in s-jqh7hf.
Repository facts and rerunning the gate are independent checks, rather than trust in the session's report.

No other looks-related decision is replaced or narrowed.
