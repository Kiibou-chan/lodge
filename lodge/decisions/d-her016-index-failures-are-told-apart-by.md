---
id: d-her016
kind: decision
title: "Index failures are told apart by error code; states are written and read in one transaction"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Only `SQLITE_CORRUPT` and `SQLITE_NOTADB` make lodge delete and rebuild an index file; busy, locked, read-only, and other errors fall back to memory without deleting.
A state is written in one transaction with its eviction, and a read takes its state and every row it needs in one read transaction, falling back to memory if any is missing; writes use `synchronous=NORMAL`.

## Reasoning

The feasibility review's F11: a locked database raises `OperationalError`, a subclass of `DatabaseError`, so the plan's detector could delete a healthy locked index; F12: a reader whose state is evicted between two lookups would see missing records; the correctness review's M6: `synchronous=OFF` can corrupt on a crash.
Cost if wrong: a read slowed by a writer's lock, never a wrong one.
