---
id: d-7aqk17
kind: decision
title: "Task 6: a duplicate ID fails both records"
scope: process
decided_by: coordinator
date: 2026-10-29T16:32:51+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 89"}
---

I3, `load` files the duplicate-ID problem against both paths, so both records fail.

## Reasoning

Mapping by path is how `failing_ids` works, and parsing paths out of messages would couple it to wording.
Cost if wrong: a published duplicate gives two notes instead of one.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
