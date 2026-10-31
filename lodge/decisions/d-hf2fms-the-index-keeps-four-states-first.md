---
id: d-hf2fms
kind: decision
title: "The index keeps four states, first in first out, and a read of a seen state writes nothing"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "four", handle: "this decision"}
  - {value: "3 s", handle: "the brief's ruling 3"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

The index keeps the four most recently built states and drops the oldest when a fifth is built; reading a seen state writes nothing to the index.

## Reasoning

A checkout read usually needs two states, the published one and the working one, and a commit adds a third; a least-recently-used order would write on every read, which a read-only sandbox cannot do (d-232gxs, d-kj554d, the coordinator's constraint on unwritable indexes).
Cost if wrong: a state rebuilt after four others, about 3 s at 160,000 files.
