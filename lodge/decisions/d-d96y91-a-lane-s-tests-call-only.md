---
id: d-d96y91
kind: decision
title: "A lane's tests call only what its waits provide, and a ported function's new parameter has a default"
scope: process
decided_by: planner
date: 2026-11-02T19:36:01+01:00
narrows: [d-t7er56]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, the plan's own number"}
  - {value: "7b", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "9", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "12a", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "12b", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "13", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, Tasks and lanes"}
  - {value: "83-87", handle: "sed -n 83,87p src/lodge/core/feedback.py"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 10"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, the plan's own number"}
---

In plan 2, a task's tests call only what its lane and its declared waits provide, so Task 7b reads the store through `load`, Task 9 waits for Task 6 and Task 11 for Task 9, and Task 11 asserts a flag's feedback by its first words; a parameter a later task adds to a function another lane calls is trailing and defaulted; Task 12 splits into 12a, the port and both stores, and 12b, the operations.

## Reasoning

Task 7b's test called `show`, which Task 4 ports, while lane B waits only for Task 3 (practice review P-I1, correctness review I-2); Task 9's test confirms, which Task 6 ports (P-I2); Task 11 rewrites the store tests that Task 9 writes, and both build a `Lodge` (correctness review M-10); in each case a builder meets a name that does not exist yet and stops or invents it, as plan 1's Task 11 did with `checkChange`.
Reading the store through `load` keeps lane B parallel to lane A, which waiting for Task 4 would not.
Task 13 changes the feedback's words from `this decision will wait for the author:` to name the person (`src/lodge/core/feedback.py:83-87`), and Tasks 11 and 13 run in parallel, so a test asserting the whole line fails after whichever merges second (P-I6, correctness review M-3); the first words are the same in both.
Plan 1's carried tests call the one-argument forms of `isAuthor`, `parseThread`, and `writeThread` (P-I3), so a required parameter breaks a lane that never touched them.
Task 12 carried the port, the operations, the fakes, the schema, and the store at once (P-I7), against d-mfayy5's one review's worth; the port comes first, since a method added to `Store` fails `tsc` until every class implementing it has it (probe 10 of `docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md`, TS2420), so the port and its two implementations are one task and the operations the next.
Cost if wrong: a task waits for one it did not need, which costs parallel time only.
