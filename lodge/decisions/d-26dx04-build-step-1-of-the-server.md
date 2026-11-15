---
id: d-26dx04
kind: decision
title: "Build step 1 of the server is four plans, the first the toolchain and the core"
scope: process
decided_by: planner
date: 2026-11-02T14:10:28+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1", handle: "design, Build order, item 1"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "3,429", handle: "wc -l src/lodge/core/*.py | tail -1"}
  - {value: "1,052", handle: "wc -l src/lodge/app/*.py | tail -1"}
  - {value: "627", handle: "wc -l src/lodge/cli/*.py | tail -1"}
  - {value: "35", handle: "ls tests/core/test_*.py | wc -l"}
  - {value: "446", handle: "grep -h '^def test_' tests/core/test_*.py | wc -l"}
  - {value: "12", handle: "ls tests/app/*.py | wc -l"}
  - {value: "118", handle: "grep -h '^def test_' tests/app/test_*.py | wc -l"}
  - {value: "34", handle: "ls tests/e2e/test_*.py | wc -l"}
  - {value: "109", handle: "grep -h '^def test_' tests/e2e/test_*.py | wc -l"}
  - {value: "14", handle: "docs/superpowers/plans/done/2026-10-31-lodge-viewer.md, Call 22"}
  - {value: "22", handle: "docs/superpowers/plans/done/2026-10-31-lodge-viewer.md, Calls made"}
---

Build step 1 of the server design is cut into four plans, each ending in tested software: the toolchain, the gate, and lodge 0.2's core in TypeScript; the events store, the operations, and the design's model changes; the API, sign-in, and the `lodge` command; the importer, export to git, and the design's records.
The first plan is written in full, the other three as a paragraph each.

## Reasoning

Step 1 rewrites all of lodge 0.2 outside the viewer and the hook: `src/lodge/core` (3,429 lines), `src/lodge/app` (1,052), and `src/lodge/cli` (627), carrying over 35 core test files with 446 tests, 12 app test files with 118, and 34 command test files with 109 (`wc -l`, `grep -c '^def test_'`), and adds the events store, the API, passkeys, the importer, and the export (design, "Build order", item 1).
The viewer plan, the largest so far, had 14 tasks (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md`, Call 22); one plan for step 1 would hold about 35, too many for one plan review to hold in view.
Each cut ends where a test suite passes on its own: the core passes the carried core tests with no store; the operations pass the carried app tests over SQLite in process; the command passes the carried command tests against the server; and the importer and export round-trip a 0.2 store.
The core comes first because every other part calls it, and porting it alone lets its 446 carried tests prove the port before anything is built on it.
Cost if wrong: three more rounds of plan review than one plan would need; a later plan that finds the cut wrong moves tasks between plans that are not yet written.
