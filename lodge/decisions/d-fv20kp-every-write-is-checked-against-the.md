---
id: d-fv20kp
kind: decision
title: "Every write is checked against the state it lands on, which plan 2 proves over the events store"
scope: process
decided_by: planner
date: 2026-11-02T19:05:43+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, the plan's own number"}
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 4"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 3"}
---

The design's check on every write needs no new write path: `add`, the thread writes, confirmations, and approvals check the state they read, and the events store's compare-and-set publishes only onto that state, so every write is checked against the state it lands on; plan 2 proves it with tests over the SQLite store and runs the two changed app test files there.

## Reasoning

lodge 0.2's `add` runs `check_change` before `publish` (`_attempt` in `src/lodge/app/writes.py`), the thread writes do too (`write` in `src/lodge/app/threads.py`), and a confirmation goes through `add` (`src/lodge/app/confirm.py`).
A rejected publish starts again from reading the store (`add` in `src/lodge/app/writes.py`), and the events store rejects every publish whose base is not the newest state (d-wje1cn), so no write lands on a state it was not checked against.
The ways a lodge 0.2 store escapes the check, a hand edit and a branch merge, do not exist on the server, and the importer goes through `add` (d-sry12f's `import` operation, plan 4).
Cost if wrong: a write path without the check, in plan 3 or 4, would need a check of its own at `publish`.
