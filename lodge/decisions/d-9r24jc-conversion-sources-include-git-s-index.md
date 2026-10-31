---
id: d-9r24jc
kind: decision
title: "Conversion sources include git's index, are asked for one at a time, and the crlf attribute counts"
scope: process
decided_by: planner
date: 2026-10-31T23:07:58+01:00
narrows: [d-dqpf59]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "129", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-codex.md, R3"}
  - {value: "2 ms", handle: "the planner's probe of git rev-parse at 1.6 ms, plan-report.md"}
---

The conversion check asks `git var GIT_ATTR_GLOBAL` and `git var GIT_ATTR_SYSTEM` one at a time, and treats a failure as every path converting; a `.gitattributes` at the root or under `lodge/` in git's index counts as a source even when absent from disk; `check-attr` also asks for `crlf`.
The result is cached by the bytes of the source files, the configuration values, and the stat of git's index file.

## Reasoning

The feasibility recheck's R3 (git var takes one variable and exits 129 for two) and F3 (git reads a root attributes file from its index when it is gone from disk), and the correctness recheck's N5 (the old `crlf` attribute still converts).
Cost if wrong: two more git calls of under 2 ms each per indexed read.
