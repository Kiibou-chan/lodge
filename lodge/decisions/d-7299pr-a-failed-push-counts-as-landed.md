---
id: d-7299pr
kind: decision
title: "A failed push counts as landed when the moved branch contains the pushed commit"
scope: process
decided_by: coordinator
date: 2026-10-30T02:19:05+01:00
narrows: [d-fx4xv3]
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
---

After a failed push the store asks the remote and reports the push as rejected when the branch moved without containing the pushed commit; a branch at the commit, or at a commit built on it, counts as landed.

## Reasoning

Final wave B1 item 2 (G3; done ledger line 201; `docs/superpowers/plans/done/2026-10-29-lodge/final-wave-b1-report.md`, item 2) stops a lost push report that another clone built on from being retried as a second decision.
The code is `src/lodge/gitstore/plumbing.py:80-81` and `_landed_below`.
