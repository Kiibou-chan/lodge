---
id: d-g2p3ng
kind: decision
title: "Task 10: add waits through the clock so that no two adds share a second"
scope: process
decided_by: coordinator
date: 2026-10-29T18:10:10+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
numbers:
  - {value: "5", handle: "docs/superpowers/plans/done/2026-10-29-lodge/task-10-review.md, I1"}
  - {value: "7", handle: "docs/superpowers/plans/done/2026-10-29-lodge/task-10-review.md, I1"}
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 151"}
---

I1, the `Clock` port gains `sleep(seconds: float) -> None`, and `add` waits through it until its date is after the newest decision in the current tree, so no two adds share a second; check 1 also compares a new decision with the decisions of the current state, not only the published one.

## Reasoning

Two adds in one second credited an agent's edit of her entry to her and passed the gate in 5 of 7 runs (task-10-review.md, I1, `same_second.sh`), a breach of must-nots 1 and 2.
Cost if wrong: an add waits up to one second.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
