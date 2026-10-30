---
id: d-8j1502
kind: decision
title: "Task 6: search and related handle an empty query, no searchable words, and pure digits"
scope: process
decided_by: coordinator
date: 2026-10-29T16:32:51+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 91"}
---

I5 and the review's conditions, search lists by filters alone only when `query.strip()` is empty, a query with no searchable words returns only the exact ID or code match, and `related` drops pure-digit words.

## Reasoning

See task-6-review.md, I5 and the ruling section.
Cost if wrong: a bare number finds nothing except by ID.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
