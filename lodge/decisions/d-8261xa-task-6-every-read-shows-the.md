---
id: d-8261xa
kind: decision
title: "Task 6: every read shows the files lodge cannot read above its output"
scope: process
decided_by: coordinator
date: 2026-10-29T16:32:51+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 90"}
---

I4, no Task 6 change; every CLI read (Task 10) and every viewer page (Task 11) shows `unrecorded_problems` above its output, naming the files lodge cannot read.

## Reasoning

A file that does not parse cannot be attributed to any record, and the check refuses publishing a new one, so only a hand-edited checkout reaches this.
Cost if wrong: reads that are right but carry a warning line.
Line handles such as spec:N refer to the files at this ruling's date.
