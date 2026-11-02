---
id: d-442r2f
kind: decision
title: "Task 11's end-of-plan checks run after the lanes merge"
scope: process
decided_by: coordinator
date: 2026-11-02T18:44:05+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 11"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 7a"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 2"}
---

Task 11 runs in a lane once Task 7a is in: its lane ports `apply.py` with its carried tests; `front-door.test.ts`, the check that no plan 1 row of `parity.json` is `planned`, and `ts/knip.json`'s `entry` back to Task 2's two patterns form a closing step run on `server-core` after every lane has merged.

## Reasoning

`apply.py` imports only `derive`, `drafts`, `fileformat`, `ids`, `model`, and `snapshot` (`grep '^from' src/lodge/core/apply.py`), all ported by Task 7a, so its port need not wait for Tasks 7b to 10 (d-xdqsmf).
The three checks need every module of the core, so they hold only once all lanes are in.
Cost if wrong: the closing step finds a missing export or a stray `entry` late, after the lanes, and fixes it there.
