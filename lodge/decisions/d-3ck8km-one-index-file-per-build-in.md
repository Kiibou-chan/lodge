---
id: d-3ck8km
kind: decision
title: "One index file per build in WAL mode with synchronous NORMAL; pruning takes the WAL files with it"
scope: process
decided_by: coordinator
date: 2026-11-01T16:52:13+01:00
replaces: [d-gvz66f, d-4n5tr6]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The index is one file per build in WAL mode with `synchronous=NORMAL`; writes run in `BEGIN IMMEDIATE` transactions and reads in one explicit read transaction; deleting another build's file deletes its `-wal` and `-shm` with it, under the exclusive lock d-e3stjn names.

## Reasoning

d-gvz66f's numbered generations, built under a temporary name and renamed in, were replaced by d-e3stjn's single file per build cleared in place, and its cap of twice the bytes per file by d-a8gkrh; what remains of it is WAL mode, `synchronous=NORMAL`, and `BEGIN IMMEDIATE` writes, which this record states.
d-4n5tr6 chose `synchronous=FULL` because the index then used a rollback journal; the built index uses WAL (`src/lodge/gitstore/index_db.py`, the `journal_mode` and `synchronous` pragmas), where `NORMAL` keeps the database consistent after a crash and loses at most the last transactions, which an index rebuilds as cold reads.
The pruning in `src/lodge/gitstore/index_space.py` (`prune`) deletes the file with its `-wal` and `-shm`, and skips a build whose lock it cannot take exclusively.
