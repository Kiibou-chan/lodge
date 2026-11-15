---
id: d-s2rdn2
kind: decision
title: "knip checks the exports behind the front doors, and a test checks #core against Python's names"
scope: process
decided_by: planner
date: 2026-11-02T14:50:59+01:00
narrows: [d-4psbdv]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-4"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-practice.md, finding P-I5"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "13", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-4"}
---

In the first plan knip checks every export of a module that its package's `index.ts` does not re-export, while the front doors, which knip takes as entries, are checked by a test that compares `#core`'s exports with the names of `src/lodge/core/__init__.py`'s `__all__`.
The third plan turns on knip's `includeEntryExports` once `main.ts` reads every front door.

## Reasoning

knip takes each target of `package.json`'s `imports` as an entry and does not report an entry's unused exports, so an unused name re-exported through `#core` passes; with `--include-entry-exports` it is reported (`plan-review-practice.md`, P-I5; `plan-review-correctness.md`, M-4).
Turning that on now fails the gate on the names lodge 0.2's core exports for `app` and `cli` alone: 13 names of `lodge.core.__all__`, among them `MINUTE_FORMAT`, `THREADS`, and `attachment_path`, are read by no carried core test (M-4 of the correctness review), and their readers arrive with the second and third plans.
The front door is the port's contract with those plans, so it is checked against Python's own list of names rather than against readers that do not exist yet.
Cost if wrong: an export of `#core` that nothing will ever read is found only when the third plan turns the option on, and removed then.
