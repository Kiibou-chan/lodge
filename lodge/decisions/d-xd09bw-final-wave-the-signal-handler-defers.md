---
id: d-xd09bw
kind: decision
title: "Final wave: the signal handler defers its exit while a git child runs"
scope: process
decided_by: coordinator
date: 2026-10-29T19:50:32+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 196"}
---

N1, the signal handler defers the exit while a git child runs and exits when it returns.

## Reasoning

Killing git mid-write leaves index.lock, which blocks the user's own git.
Cost if wrong: a SIGTERM waits for at most one git call.
Line handles such as spec:N refer to the files at this ruling's date.
