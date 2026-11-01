---
id: d-k194gk
kind: decision
title: "The index stores a published state's statuses only, under its published identity"
scope: process
decided_by: coordinator
date: 2026-11-01T14:58:11+01:00
narrows: [d-dxqxsn]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "3.33 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-10c-review.md:45"}
  - {value: "0.448 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-10c-review.md:50"}
---

The index stores a state's statuses under its identity only when that identity is a published tree, and stores no `check_state` problems; a read's change check takes the published statuses from there, and the gate computes its own facts in full.

## Reasoning

A stored fact is looked up only by the published identity, a git tree ID, so facts stored under a working-tree identity with changes are never read again (`src/lodge/app/indexed.py:72`).
The stored published problems never change a read's output: `finish_checked` in `src/lodge/app/state.py` re-adds every standing problem and drops the notes, and reads with every stored problem list emptied matched the exact reader (task-10c-review.md, I-2).
Writing both cost about 3.33 MB of index per changed read and 0.448 s of `check_state` on a miss at 160,000 files, for nothing a read uses.
d-dxqxsn keeps its rule that facts are immutable and keyed by identity alone; it narrows to statuses, and to published identities.
The gate and `add` are unaffected: they derive and check in full and never take facts from the index.
