---
id: d-0hg1mf
kind: decision
title: "Task 1: the clock ban covers datetime class attributes only, so the Clock port passes"
scope: process
decided_by: coordinator
date: 2026-10-29T15:04:11+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 34"}
---

The builder's ruling, adopted: `now`, `today`, `utcnow`, `fromtimestamp` are banned in `core` and `app` only as attributes of `datetime.datetime` or `datetime.date` resolved through imports, so the Clock port's `clock.now()` passes.

## Reasoning

The plan's literal ban on the name would reject its own port.
Cost if wrong: an aliased class (`d = datetime; d.now()`) slips past, while the module allow-list still keeps `time`, `os`, and `secrets` out.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
