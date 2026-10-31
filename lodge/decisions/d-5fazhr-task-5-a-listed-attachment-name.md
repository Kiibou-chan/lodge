---
id: d-5fazhr
kind: decision
title: "Task 5: a listed attachment name resolves to one path under the decision's folder"
scope: process
decided_by: coordinator
date: 2026-10-29T16:16:12+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 76"}
---

M3, a listed attachment name resolves to `lodge/attachments/<decision id>/<name>`, one form only.

## Reasoning

The spec's Storage layout places attachments at `lodge/attachments/<id>/` (spec:212, Storage, the `lodge/attachments/<id>/` line).
Cost if wrong: Task 9 and the guide (Task 13) follow this form and change together.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
