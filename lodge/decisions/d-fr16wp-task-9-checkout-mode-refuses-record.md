---
id: d-fr16wp
kind: decision
title: "Task 9: checkout mode refuses record paths that pass through a symbolic link"
scope: process
decided_by: coordinator
date: 2026-10-29T17:34:38+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 133"}
---

B1, checkout mode refuses any path under `lodge/` that passes through a symbolic link (checked with `lstat` per component, under the lock) and reads a link as its target text without following it, as branch mode already does.

## Reasoning

The probe overwrote a file outside the repository through a linked record (task-9-review.md, B1).
Cost if wrong: a deliberately linked record folder stops working in checkout mode.
Line handles such as spec:N refer to the files at this ruling's date.
