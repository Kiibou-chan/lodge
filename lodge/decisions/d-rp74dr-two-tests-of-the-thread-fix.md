---
id: d-rp74dr
kind: decision
title: "Two tests of the thread fix paths wait for the command's port"
scope: process
decided_by: planner
date: 2026-11-02T19:05:32+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, the plan's own number"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 3"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, the plan's own number"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'Task 6: Thread files and snapshots'"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'Task 7a: Doubts and derived statuses'"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'Task 8c: The other check tests'"}
  - {value: "9", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'Task 9a: Levels'"}
---

Plan 2 carries `waiting_reads_one_snapshot` of `tests/app/test_thread_fix_paths.py`, and `orphaned_thread_outputs` and `run_thread_outcomes` stay `test.todo`s, since they call the command's code; the file's row of `ts/tests/parity.json` becomes plan 3's, which turns them into tests.

## Reasoning

The file imports `thread_head`, `thread_text`, `waiting_text`, `Ask`, `ThreadCommand`, `Threads`, and `run_thread` from `lodge.cli` (its import lines), and plan 2 builds no `cli` package, which plan 3 ports (d-26dx04; d-k5swcq).
Plan 1 left calls into later code as `test.todo`s that a later task turned into tests (its Tasks 6, 7a, and 8c, turned in 9a), and the parity test refuses a `test.todo` only in a `ported` row (`ported_files_hold_no_todo` in `ts/tests/parity.test.ts`).
Cost if wrong: plan 3 could miss the row, which stays `planned` and so shows in the closing count of planned rows.
