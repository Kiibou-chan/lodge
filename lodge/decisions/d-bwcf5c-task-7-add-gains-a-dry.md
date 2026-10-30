---
id: d-bwcf5c
kind: decision
title: "Task 7: add gains a dry run that applies, checks, and prints feedback without publishing"
scope: process
decided_by: coordinator
date: 2026-10-29T16:50:13+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 103"}
---

I2, `add` gains `dry_run: bool` (Task 8's operation, `lodge add --dry-run` in Task 10), which applies, checks, and prints feedback without publishing, and the guide (Task 13) says to dry-run before adding; the feedback messages name the remedy as a change to the draft; check 5 keeps the plan's "every header key" rule.

## Reasoning

Feedback prints after publishing, and in branch mode check 5 then refuses the edit the feedback asks for (task-7-review.md, I2, probe2), while a dry run keeps feedback advice and never a refusal (spec, Writing).
Cost if wrong: one flag through Tasks 8, 10, and 13.
Line handles such as spec:N refer to the files at this ruling's date.
