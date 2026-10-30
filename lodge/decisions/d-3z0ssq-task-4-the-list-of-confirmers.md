---
id: d-3z0ssq
kind: decision
title: "Task 4: the list of confirmers keeps every author confirmer, imported or earlier-dated"
scope: process
decided_by: coordinator
date: 2026-10-29T15:56:49+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 65"}
---

`Derived.confirmed_by` keeps listing every author confirmer, imported or earlier-dated ones included.

## Reasoning

It records who confirmed, and the flag, not that list, says whether her review is outstanding (spec, Review flag).
Cost if wrong: a reader sees a confirmer beside a decision still flagged, and Task 9's reader filters the list.
Line handles such as spec:N refer to the files at this ruling's date.
