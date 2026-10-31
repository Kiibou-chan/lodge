---
id: d-jrsa66
kind: decision
title: "The signal handler defers its exit only while the main thread runs a git child"
scope: process
decided_by: coordinator
date: 2026-10-30T02:19:05+01:00
narrows: [d-xd09bw]
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
---

The signal handler defers the exit while the main thread has a git child running and exits when that call returns; a git call on another thread, such as a viewer request, does not defer it.

## Reasoning

Final wave B1 item 21 (done ledger lines 198 and 201; `docs/superpowers/plans/done/2026-10-29-lodge/final-wave-b1-report.md`, item 21) made the count per thread, because a request thread's git call deferred the exit and `lodge view` did not stop on SIGTERM.
The code is `src/lodge/gitstore/git.py:50`, where only the main thread raises the pending exit.
