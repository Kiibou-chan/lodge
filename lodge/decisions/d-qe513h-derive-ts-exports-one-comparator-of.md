---
id: d-qe513h
kind: decision
title: "derive.ts exports one comparator of order keys, and confirmations and views reuse it"
scope: process
decided_by: coordinator
date: 2026-11-02T19:04:53+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-7a-review.md, D-2"}
  - {value: "223", handle: "src/lodge/core/views.py:223"}
  - {value: "31", handle: "src/lodge/core/confirmation.py:31"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-7b-8a-review.md, 8a-D-1"}
---

`derive.ts` exports `compareOrderKeys`, the instant through `orderInstant`, then the ID by code point, and `confirmation.ts` and `views.ts` sort with it rather than each writing its own; `check-state.ts` exports a `checkResult(problems, notes)` constructor that computes `ok`, and every place that builds a check result uses it.

## Reasoning

Python sorts by `order_key` tuples (`src/lodge/core/confirmation.py:31`, `src/lodge/core/views.py:223`), which JavaScript cannot compare, so each port would otherwise write its own comparator, and a second copy may break the tie the other way (Task 7a's review, D-2).
`ok` is a getter on one literal, so a spread copy keeps a stale `ok` (`{ ...checkState(clean), problems: [p] }.ok === true`; Task 7b and 8a's review, 8a-D-1), and `checkChange` and plan 2's app build results too.
Both are exports beyond Python's imports, against d-tha8st's rule that a name no other Python file imports is not exported, since the TypeScript needs the shared form where Python had a built-in one.
Cost if wrong: two more exports in `core`, read inside the package only.
