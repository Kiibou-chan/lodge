---
id: d-cqr414
kind: decision
title: "Every index write checks the cap, and clears only after a state or a whole working set was written"
scope: process
decided_by: coordinator
date: 2026-11-01T16:52:12+01:00
narrows: [d-a8gkrh]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "7", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md, Task 10a, the cap paragraph headed \"the review of 7b, B2\""}
---

Every index write transaction, a marker's, a parse-only writer's, or a keep, first compares the used pages with the cap, and clears when over it provided a state was kept since the last clear or the units inserted since the last clear number at least the tree's file count.

## Reasoning

d-a8gkrh checked the cap only before a keep, and only when a state had been kept since the last clear.
Under the keep on second sight (d-n65rhr) a first read writes a marker and its parse units without keeping a state, so that rule let parse-only writes grow the file without bound; the plan's 7b review (B2) replaced it with the rule above, which the build implements (`src/lodge/gitstore/index_space.py`, `prepare_keep`).
The working-set clause keeps a read that wrote a whole working set after a clear from being cleared away by the next writer, so the file stays within the cap plus one working set whether or not a state is ever kept.
d-a8gkrh keeps its formula, its bytes per file as d-j51qmy set them, and its connection settings.
