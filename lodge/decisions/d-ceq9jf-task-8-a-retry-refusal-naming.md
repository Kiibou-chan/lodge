---
id: d-ceq9jf
kind: decision
title: "Task 8: a retry refusal naming something absent from the first snapshot is a conflict"
scope: process
decided_by: coordinator
date: 2026-10-29T17:06:19+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 113"}
---

M4, a refusal on a retry that names an area or entry absent from the first attempt's snapshot becomes `Conflict`.

## Reasoning

It is a race, and exit 1 tells the caller to retry (task-8-review.md, M4, probe).
Cost if wrong: a genuine usage error that only shows on a retry exits 1.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
