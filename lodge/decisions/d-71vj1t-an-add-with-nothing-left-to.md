---
id: d-71vj1t
kind: decision
title: "An add with nothing left to write publishes nothing and reports that nothing changed"
scope: process
decided_by: coordinator
date: 2026-10-30T02:05:24+01:00
replaces: [d-ddcjgs]
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
---

Writes equal to the current file are dropped, and an add with nothing left publishes nothing and reports the outcome `UNCHANGED`, printed `nothing changed`, not `PUBLISHED` with a note.

## Reasoning

Final wave B1 item 4 (A1 and D3) replaced the note with an outcome of its own, `AddOutcome.UNCHANGED` (done ledger line 201; `docs/superpowers/plans/done/2026-10-29-lodge/final-wave-b1-report.md`, item 4; `src/lodge/app/results.py`).
The test `test_unchanged_draft_publishes_nothing` in `tests/app/test_writes.py` pins it.
The reason in d-ddcjgs still holds: an empty commit in branch mode is noise in the history.
