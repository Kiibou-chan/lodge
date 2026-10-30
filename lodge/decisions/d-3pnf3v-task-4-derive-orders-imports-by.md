---
id: d-3pnf3v
kind: decision
title: "Task 4: derive orders imports by date, and the add-time check refuses an import over a live edit"
scope: process
decided_by: coordinator
date: 2026-10-29T16:01:05+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 60"}
---

I2, `derive` orders imports by date like live decisions, and Task 5's check refuses an imported decision that changes an entry a published non-imported decision already changed.

## Reasoning

One snapshot cannot tell an import added after her live edit from one added before it, and flagging both flags her own imports whenever she later edits the entry (task-4-recheck-1.md, N1, probes R1 and R2), while the add-time check sees the published snapshot.
Cost if wrong: an old record that changes an entry she already edited live goes in as a live decision with its quote, not as an import.
Line handles such as spec:N refer to the files at this ruling's date.
