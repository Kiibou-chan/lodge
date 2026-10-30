---
id: d-23sqbg
kind: decision
title: "Task 3: a given date means a new decision; none means an existing record keeps its date"
scope: process
decided_by: coordinator
date: 2026-10-29T15:31:44+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 47"}
---

`record_from_draft(date=...)` given means a new decision and a draft carrying `date` is refused unless imported; `date=None` means an existing record whose draft keeps its own date; Task 8 calls it that way.

## Reasoning

Matches the plan's calls on dates and edits.
Cost if wrong: Task 8 rewires one call.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
