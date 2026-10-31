---
id: d-zyqzkg
kind: decision
title: "Identical states skip the change check, by a proof per sub-check"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

When the current and published states are identical, a read reuses the current snapshot for the published one and skips `check_change`; identical means equal file mappings and attachments, or later equal state identities.

## Reasoning

For identical states every problem `check_state` finds in the current state is also in the published one, so `read_checked` adds none of them (`src/lodge/app/state.py`, `read_checked`); `_missing` finds every ID present; `_dates`, `_imports_over_live`, `_unlisted_sources`, and the decision half of check 6 iterate over new decisions or new records, of which there are none; check 4 compares each entry with itself; check 5 compares each decision and thread with itself; check 6's entry half looks only at `rests_on` targets the published entry lacks.
A test runs `check_change(s, s)` over every sample snapshot and asserts no problems, so a future check that breaks the proof fails it.
Cost if wrong: a check 4, 5, or 6 problem missing from a read of an identical state, which the gate, unchanged, still finds.
