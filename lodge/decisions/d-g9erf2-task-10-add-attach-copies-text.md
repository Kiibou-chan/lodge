---
id: d-g9erf2
kind: decision
title: "Task 10: add --attach copies text files beside the one new decision"
scope: process
decided_by: coordinator
date: 2026-10-29T18:10:10+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 152"}
---

I2, `lodge add --attach PATH...` copies each file into `lodge/attachments/<id>/<file name>` of the one new decision the add creates (refused when the add creates none or several), in the same publish; the decision's `attachments` must list exactly those names; files are read by `cli` (LODGE-5 lets it read files it is given) and must be UTF-8 text in 0.1, any other file refused with one sentence.

## Reasoning

The spec promises attachments ("expanded evidence like logs or anything else attached", Her decisions), the guide describes them, and no route existed, none at all in branch mode (task-10-review.md, I2).
Cost if wrong: binary evidence waits for a later version.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
