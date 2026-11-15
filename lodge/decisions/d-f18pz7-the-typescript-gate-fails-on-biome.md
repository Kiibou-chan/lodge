---
id: d-f18pz7
kind: decision
title: "The TypeScript gate fails on Biome warnings"
scope: process
decided_by: coordinator
date: 2026-11-02T17:48:43+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "16", handle: "cd ts && bun x biome check . (at 7c3ab8b)"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 5b"}
---

`ts/package.json`'s `check` runs `biome check --error-on-warnings .`, so a recommended rule's warning fails the gate as Ruff's findings fail lodge 0.2's.

## Reasoning

At 7c3ab8b Biome reports 16 warnings (`noNonNullAssertion`, `useTemplate`) and the gate passes, so they accumulate unseen with every task; Ruff fails on every finding in lodge 0.2's gate (`scripts/check.sh`).
A rule that does not fit the code is turned off by name in `biome.json`, with a reason, rather than left warning.
Cost if wrong: a fix round spends time on style warnings; one flag to remove.
