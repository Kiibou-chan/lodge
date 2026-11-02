---
id: d-snrhjs
kind: decision
title: "checkResult is a constructor of #core's front door"
scope: process
decided_by: coordinator
date: 2026-11-02T20:19:33+01:00
narrows: [d-qe513h, d-ca6wbw]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "91", handle: "src/lodge/core/__init__.py:91"}
  - {value: "39", handle: "ts/tests/core/front-door.test.ts:39"}
  - {value: "2", handle: "ts/tests/core/check-state-order.test.ts:2"}
  - {value: "4", handle: "ts/tests/core/views.test.ts:4"}
---

`checkResult(problems, notes)` is exported through `#core` and listed among the front door's constructors beside the type `CheckResult`, so code outside `core`, plan 2's included, builds a check result through it rather than as a literal.

## Reasoning

d-qe513h made `checkResult` the one way to build a check result but left where it is read unsaid, and d-ca6wbw lists the constructors `#core` exports for types in `__all__`; `CheckResult` is in lodge 0.2's `__all__` (`src/lodge/core/__init__.py:91`).
The 8a fix round's tests build check results and may import only through `#core` (`ts/tests/core/check-state-order.test.ts:2`, `ts/tests/core/views.test.ts:4`), so the coordinator exported it there and the front-door test lists it (`ts/tests/core/front-door.test.ts:39`); the review of that round found no decision recording it (`task-10-12-8afix-review.md`, 8afix-D-1).
Cost if wrong: one more name on `#core`'s front door, which the front-door test already pins.
