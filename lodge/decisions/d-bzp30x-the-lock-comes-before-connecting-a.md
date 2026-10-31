---
id: d-bzp30x
kind: decision
title: "The lock comes before connecting, a refused upgrade gives up the index, age is the lock file's"
scope: process
decided_by: planner
date: 2026-10-31T23:54:16+01:00
narrows: [d-e3stjn]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "7 days", handle: "d-e3stjn"}
---

`open_index` takes `LOCK_SH`, blocking, before connecting and releases it after closing, opening an existing lock file read-only when it cannot create one, and touches it on each opening; a build's age is its lock file's modification time.
The corrupt-file rule applies in `open_index` only; a refused upgrade closes the lock and returns `None`, as does a corrupt file without `fcntl`.
Other builds beyond the four most recently touched also go, under the same lock.

## Reasoning

The fourth recheck's W5 (a refused upgrade on Linux drops the shared lock), W7 (the lock's order and lockless cases), and W8 (a build that only reads looked unwritten, and nothing bounded the count of builds' files).
Cost if wrong: a build idle for 7 days, or the fifth most recent, starts cold.
