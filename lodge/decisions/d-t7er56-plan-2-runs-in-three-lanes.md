---
id: d-t7er56
kind: decision
title: "Plan 2 runs in three lanes, and Lodge is ported a method at a time"
scope: process
decided_by: planner
date: 2026-11-02T19:05:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, the plan's own number"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, the plan's own number"}
---

Plan 2's tasks are those of the plan; `lodge.ts` is written with the constructor, `mint`, and `add` in the task that ports `writes.py`, and the later tasks add the methods that delegate to the modules they port, departing for this one file from d-tha8st's rule that a module is ported whole; the app tasks, the store tasks, and the core tasks for people run as three lanes in parallel.

## Reasoning

Every app test reaches the operations through `Lodge` (`wired` in `tests/app/support.py`), and `lodge.py` imports all four operation modules (`from lodge.app import confirm, reads, threads, writes` in `src/lodge/app/lodge.py`), so porting it whole would put all of `app` in one task, against d-mfayy5's rule of one review's worth a task.
The store needs only the ports and `Lodge.add`, and the people of the core touch only `ts/src/core`, so both can run beside the app's port, as d-xdqsmf lets plan 1's lanes run.
Cost if wrong: a merge conflict between lanes, resolved when the lane merges.
