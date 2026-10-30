---
id: d-02htqk
kind: decision
title: "Task 10: the wheel test may use uv's cache and the network, and skips offline"
scope: process
decided_by: coordinator
date: 2026-10-29T14:58:44+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 25"}
---

`test_wheel` may use uv's cache and network, and skips with a stated reason when offline.

## Reasoning

Packaging is otherwise first tested in a cloud child (T14).
Cost if wrong: one slow test that needs the network.
Line handles such as spec:N refer to the files at this ruling's date.
