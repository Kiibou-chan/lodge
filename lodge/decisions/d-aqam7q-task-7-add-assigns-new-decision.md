---
id: d-aqam7q
kind: decision
title: "Task 7: add assigns new decision IDs in ascending order, in draft order"
scope: process
decided_by: coordinator
date: 2026-10-29T16:35:48+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 95"}
---

Task 4 M2 and N2 are taken in Task 7: `apply_drafts` assigns new IDs in ascending order to the decision drafts in draft order.

## Reasoning

Dates are shared within one add and `derive` breaks ties by ID, so draft order becomes decision order without faking seconds.
Cost if wrong: two adds in the same second still tie by random ID, which check 1 refuses for linked decisions.
Line handles such as spec:N refer to the files at this ruling's date.
