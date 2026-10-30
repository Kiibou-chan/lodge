---
id: d-2984wn
kind: decision
title: "Task 3: a record's file-name slug is capped at a word boundary"
scope: process
decided_by: coordinator
date: 2026-10-29T15:31:44+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
numbers:
  - {value: "60", handle: "src/lodge/core/fileformat.py, _SLUG_CHARS"}
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 48"}
---

`slug` gets a 60-character cap, cut at a word boundary.

## Reasoning

Six long words can pass a file-name limit, and the slug is the plan's call, not the spec's.
Cost if wrong: none; taken in this task's fix round or the final wave.
Line handles such as spec:N refer to the files at this ruling's date.
