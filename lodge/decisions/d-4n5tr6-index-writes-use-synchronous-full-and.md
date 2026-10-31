---
id: d-4n5tr6
kind: decision
title: "Index writes use synchronous FULL, and pruning takes journals with their files"
scope: process
decided_by: planner
date: 2026-10-31T23:07:59+01:00
narrows: [d-her016]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Index write transactions run with `synchronous=FULL`, since the index uses the rollback journal; deleting another build's file deletes its journal with it, and a file whose journal is locked is skipped.
Error codes and transactions stay as d-her016 says.

## Reasoning

The correctness recheck's N7 (`NORMAL` is corruption-safe only in WAL mode) and N9 (a stale journal rolls into a new file of the same name).
A read of a seen state writes nothing, so the extra sync falls only on reads that already build.
Cost if wrong: one more fsync per write transaction.
