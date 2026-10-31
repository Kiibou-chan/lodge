---
id: d-n6tqzq
kind: decision
title: "Flag and conversion results are cached in the process only, keyed before and after the git call"
scope: process
decided_by: planner
date: 2026-10-31T23:27:20+01:00
narrows: [d-9r24jc, d-dqpf59]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "0.02 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-2.md, V6, 0.020 s at s90000"}
---

Flag and conversion results are cached in the store object only, never in the index, so a read of a seen state still writes nothing after a `git status`.
Their key (the stat of git's index file as inode, size, `mtime_ns`, and `ctime_ns`, the configuration values, the source bytes) is taken before the git call and again after it; the result is kept only when the two are equal.

## Reasoning

The recheck's V4 (a key taken after the call can file an old answer under a new key) and V6 (`git status` replaces git's index file, so an index-kept cache turns a seen read into a write).
Cost if wrong: about 0.02 s per indexed read for the flags call.
