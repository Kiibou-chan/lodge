---
id: d-59q4jc
kind: decision
title: "The app's ports are asynchronous, and its clock gives milliseconds with an offset"
scope: process
decided_by: planner
date: 2026-11-02T19:05:27+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 3"}
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
---

Every method of the `Store` and `Projects` ports returns a promise, `Clock.sleep` returns a promise, and every operation of `Lodge` is asynchronous; `Clock.now()` gives `{ epochMs, offsetMinutes }`, which `app` turns into stamps, never a `Date`.

## Reasoning

Kysely's API is asynchronous throughout, and d-4k9wcr has the store query SQLite through it, so a synchronous port would need a second way into SQLite beside the one that decision chose.
Kysely's SQLite driver runs one transaction at a time on its connection (the plan's probe 3), so asynchrony costs the store no atomicity.
A `Date` carries no offset, while lodge 0.2 dates a decision in local time with its offset (s-aq3a5k; `src/lodge/app/writes.py`, `now.isoformat(timespec="seconds")`), and `app` may not read the local zone (d-mfskz3), so the clock hands the offset over.
Milliseconds keep lodge 0.2's wait to the next whole second (`_after_newest` in `src/lodge/app/writes.py`), which needs the fraction of the current second.
Cost if wrong: a synchronous port later removes the `await`s from `app` and its tests, a mechanical change.
