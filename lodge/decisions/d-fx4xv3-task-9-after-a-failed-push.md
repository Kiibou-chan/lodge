---
id: d-fx4xv3
kind: decision
title: "Task 9: after a failed push the store asks the remote and reports a moved branch as rejected"
scope: process
decided_by: coordinator
date: 2026-10-29T17:34:38+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
numbers:
  - {value: "20", handle: "docs/superpowers/plans/done/2026-10-29-lodge/task-9-review.md, I1"}
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 134"}
---

I1, after any failed push the store asks the remote (`ls-remote`) and returns `REJECTED` when the branch moved, so `add` retries.

## Reasoning

Two clones pushing at once lose with "incorrect old value provided", 20 of 20 rounds (task-9-review.md, I1).
Cost if wrong: one extra remote call on a failed push.
Line handles such as spec:N refer to the files at this ruling's date.
