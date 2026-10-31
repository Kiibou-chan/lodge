---
id: d-n7whwk
kind: decision
title: "Plans are reviewed before building, and each task gets two maintainability views"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:23+01:00
changes:
  - {entry: s-e55e3t, action: create}
---

A plan is reviewed before building, and each task ends with a maintainability review from a practice view and a design view.
Multi-agent builds follow the plan, review, and implement rounds of an existing project.

## Reasoning

The specification gives this as the practice for the build rather than with a separate reason.

The review at each task's end splits into practice, which looks at duplication, complexity, naming, and documentation against behaviour, and design, which looks at boundaries, coupling, and plan rules no test enforces.
