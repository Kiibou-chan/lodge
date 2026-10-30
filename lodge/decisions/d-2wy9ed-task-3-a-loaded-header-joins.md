---
id: d-2wy9ed
kind: decision
title: "Task 3: a loaded header joins UTF-16 surrogate pairs into one character"
scope: process
decided_by: coordinator
date: 2026-10-29T15:39:27+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 51"}
---

A loaded header joins UTF-16 surrogate pairs (as `json.dumps` writes emoji by default) into the character they encode; a lone surrogate stays problem 1.

## Reasoning

An agent writing drafts with `json.dumps` defaults would otherwise be refused for any emoji in her words.
Cost if wrong: none.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
