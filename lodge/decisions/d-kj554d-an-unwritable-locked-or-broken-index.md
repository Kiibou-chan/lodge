---
id: d-kj554d
kind: decision
title: "An unwritable, locked, or broken index never fails a read or changes its output"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

When the index cannot be written (a read-only sandbox, a locked database), lodge opens it read-only and answers from what it holds, and otherwise computes in memory without writing; a database error at any point drops to the in-memory path; a corrupt file or a version mismatch is deleted and rebuilt when it can be written.
The output is the same in every case.

## Reasoning

The coordinator's constraint: agents may read through lodge in a read-only sandbox where the git common dir cannot be written, so no read may fail or differ there.
The in-memory path is today's read, with the four speed tasks, so it is always available.
Cost if wrong: a read slower in a sandbox, never a failed one; each case has its own test in Task 9.
