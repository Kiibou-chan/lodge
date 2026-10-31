---
id: d-mzgrxb
kind: decision
title: "Task 11: an unknown record reference is a 404 in the viewer and exit 2 in the command line"
scope: process
decided_by: coordinator
date: 2026-10-29T18:34:25+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 161"}
---

M4, "no record named x" is a 404: `Lodge` raises a `NotFound(LodgeError)` subclass for an unknown reference, still exit 2 in the CLI.

## Reasoning

A viewer link to a missing record is not a bad request.
Cost if wrong: one subclass.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
