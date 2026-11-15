---
id: d-g1hrmn
kind: decision
title: "A bare day orders as midnight UTC of that day"
scope: process
decided_by: coordinator
date: 2026-11-02T17:37:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md, D-1"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 7a"}
  - {value: "14", handle: "the widest offsets, -12:00 and +14:00"}
---

Where lodge orders decisions by date, a bare day, which only an imported decision may carry, orders as `T00:00:00+00:00` of that day, ties broken by ID; `stamps.ts` gains the function, and Task 7a orders through it.

## Reasoning

lodge 0.2 orders by `datetime.fromisoformat(d.date)` (`src/lodge/core/derive.py:101-102`), so bare days order among themselves as naive midnights, and a bare day against a stamp raises `TypeError` (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md`, D-1); `instant` throws on a day, so Task 7a would throw where lodge 0.2 orders.
Midnight UTC keeps the order among days that lodge 0.2 gives, and replaces the crash against a stamp with an order.
Cost if wrong: an imported day sorts at most 14 hours away from the stamps of its own day; one function to change.
