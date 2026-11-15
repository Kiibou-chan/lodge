---
id: d-xk6qtn
kind: decision
title: "scripts/check.sh runs the Python gate and the TypeScript gate"
scope: process
decided_by: planner
date: 2026-11-02T14:10:39+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
---

`scripts/check.sh` runs lodge 0.2's gate and then `scripts/check-ts.sh`, and stops with "bun is not installed" when Bun is missing, rather than skip the TypeScript half.

## Reasoning

`CLAUDE.md` calls `sh scripts/check.sh` "the whole gate", and the coordinator runs it after every task (viewer plan, "Global Constraints").
A gate that skips half of the code when a tool is missing would report green on code it never checked, against the first must-not, never show wrong information (design, "Must nots").
Cost if wrong: a session without Bun installs it before the gate runs, one command.
