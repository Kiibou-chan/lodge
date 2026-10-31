---
id: d-dxqxsn
kind: decision
title: "Each state's own facts are stored by its identity alone"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Whenever a fast read runs `derive` and `check_state` on a state, the index stores that state's statuses and `check_state` problems under its identity alone; a later state's change check takes the published state's facts from there and computes them when they are absent.

## Reasoning

The correctness review's I3 and the feasibility review's F8: a stored read state is keyed by both identities and holds combined results, so the published state's own `check_state` problems cannot be recovered from it, and `check_state` and `derive` depend on the snapshot alone (`src/lodge/core/check_state.py`, `check_state`).
Cost if wrong: one more table, small next to the rows.
