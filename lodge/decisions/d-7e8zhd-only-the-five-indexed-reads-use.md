---
id: d-7e8zhd
kind: decision
title: "Only the five indexed reads use git's fast identity; every other command reads exact trees"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "2 s", handle: "probes/walk.py, read every file"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

`show`, `search`, `waiting`, `threads`, and `thread` find their state through git's fast identity; the gate, `add`, the thread writes, the confirmation, `id`, `draft`, `spec`, `timeline`, `check`, and the viewer read exact trees, every working-tree file read and hashed by lodge, as today, with the parse cache keyed by those hashes.
`Store.trees()` stays, and each `Tree` gains the blob ID of every file.

## Reasoning

The coordinator's ruling 2 of the fix round (the gate and add never trust git for working-tree files) and the feasibility review's F10 (writes need text trees: `src/lodge/app/writes.py`, `src/lodge/core/apply.py`, `src/lodge/gitstore/plumbing.py` take a `Tree`).
Keeping `trees()` leaves every write path unchanged and gives the fast identity an exact oracle in tests.
Cost if wrong: `spec`, `timeline`, and the viewer stay near 2 s at 160,000 files after the parse cache.
