---
id: d-gmtkw4
kind: decision
title: "Task 10: --attach is given once per file, add waits at most three times, attachments stay UTF-8"
scope: process
decided_by: coordinator
date: 2026-10-29T18:16:37+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 154"}
---

`--attach` is given once per file, `add` waits at most three times, and attachments keep their bytes as UTF-8.

## Reasoning

A greedy list would swallow the draft files, and a decision dated further ahead is check 1's to refuse (task-10-report.md, Fix round 1, concerns 1, 3, and 4).
Cost if wrong: one more flag per attachment.
Line handles such as spec:N refer to the files at this ruling's date.
