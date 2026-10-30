---
id: d-fz6gnk
kind: decision
title: "Task 10: the builder's command-line choices stand"
scope: process
decided_by: coordinator
date: 2026-10-29T18:02:23+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 149"}
---

The builder's choices stand: `test_add_non_string_scalar_exits_2` uses a list, since every YAML scalar is text (tests/core/test_yamlio.py:6-10); `problem:` lines add `:<line>` when known; `search` takes an optional query; output streams replace undecodable characters; a failed dry run prints both lines; any `hook` argv skips parsing and exits 0.

## Reasoning

Each is within the brief or makes its output more exact (task-10-report.md, concerns 1 to 4 and 6).
Cost if wrong: one line of output text.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
