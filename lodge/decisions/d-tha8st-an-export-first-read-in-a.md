---
id: d-tha8st
kind: decision
title: "An export first read in a later task waits in knip's entry list"
scope: process
decided_by: planner
date: 2026-11-02T15:17:08+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "6.42.0", handle: "grep -n knip docs/superpowers/plans/2026-11-02-lodge-server-core.md (Tech stack)"}
  - {value: "11", handle: "grep -n '### Task 11' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "2", handle: "grep -n '### Task 2' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
---

In the first plan a module or test helper is ported whole, exporting what its Python counterpart gives other files, and a file with an export whose first reader comes in a later task goes into `ts/knip.json`'s `entry` list in the task that creates it.
The task in which the last of those names gets its reader takes the file out again, so knip checks every export of the file from then on.

## Reasoning

knip fails on an export that no other file reads, both in a module and in a test helper, and stops reporting a file's exports once the file is in `entry`; taking the file out restores the check, which fails again on a name still unread (`plan-fix-2-report.md`, probe of knip 6.42.0; `plan-recheck-1.md`, N1).
The splits of d-mfayy5 and the old task boundaries leave such names at eight files, among them `orderKey` in `derive.ts`, `newDecisions`, `problemAt`, and `sortKey` in `check-state.ts`, `LINE_BREAKS_AND_TABS` in `yamlio.ts`, and `treeOf` in the test helper `builders.ts` (`plan-recheck-1.md`, N1, from the import lines of `src/lodge/core/*.py` and `tests/core/*.py`).
The other option, leaving `export` off until the reading task adds it, fails `tsc` for a name its own file never reads (`TS6133`, probe in `plan-fix-2-report.md`), which holds for `new_decisions`, `read_stamp`, `LINE_BREAKS_AND_TABS`, `tree_of`, and `REMEDY_CHECK_4`; the earlier task would then port part of a module and a later one the rest, so no review sees a Python module against its port in one piece, and every reading task would modify an earlier task's source file.
The entry list changes only `ts/knip.json`, which the reading task lists under Modify; Task 11 checks that the list is back to Task 2's two patterns, so no file stays exempt past the plan.
Cost if wrong: while a file is in `entry`, an export of it that will never be read is not reported; it is found when the reading task takes the file out, at most a few tasks later, and removed then.
