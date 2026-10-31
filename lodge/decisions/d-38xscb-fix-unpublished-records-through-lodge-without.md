---
id: d-38xscb
kind: decision
title: "Fix unpublished records through lodge without resetting"
scope: process
decided_by: coordinator
date: 2026-10-31T00:51:13+01:00
work_item: "docs/superpowers/plans/2026-10-30-lodge-on-itself.md"
---

The fix round edits the unpublished Task 1 and 2 records through `lodge draft` and `lodge add` (with `--import` for the four Task 1 decisions that become imports dated from done ledger lines 210 to 215), never by resetting the branch.

## Reasoning

The published state is 47dcfa7, so check 5 does not yet hold these records, and a reset would force-push the work branch.
Cost if wrong: if lodge refuses changing a record's origin, those four stay live and get a replacing import, one more record each.
