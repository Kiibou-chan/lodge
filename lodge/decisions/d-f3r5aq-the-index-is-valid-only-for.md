---
id: d-f3r5aq
kind: decision
title: "The index is valid only for the same lodge code, settings, and time window"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Every stored result is keyed by the index's schema number and a digest of lodge's own package files (name, size, and mtime of each), and a state's result also by a digest of the core settings; a state whose result holds a new decision dated after the time it was built expires at that date.

## Reasoning

An editable install keeps its version while its code changes, so the version alone would serve a result an older parser or check computed.
`check_change` reads the clock in one place, `_dates`, which fails a new decision dated after now (`src/lodge/core/check_change.py`), so that problem disappears once its date has passed; nothing else in the checks or in `derive` reads the time.
Check 4 reads the import sources from the settings (`src/lodge/core/check_entries.py`, `_unlisted_sources`).
Cost if wrong: a stale result after an upgrade, which the digest rules out.
