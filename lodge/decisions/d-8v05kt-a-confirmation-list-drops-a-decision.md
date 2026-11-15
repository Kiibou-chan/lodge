---
id: d-8v05kt
kind: decision
title: "A confirmation list drops a decision only when the reading person has confirmed it"
scope: process
decided_by: coordinator
date: 2026-11-14T23:41:33+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "13", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, heading `### Task 13`, case `touching_two_people_waits_for_both`"}
---

`confirmableIds` in `ts/src/core/confirmation.ts`, and so `behindArea`, `Shown.confirmable`, and the expected ids of `confirm`, take the person and drop a decision only when a confirmation by that person names it.
This is the per-person reading of d-4spcem applied to the confirm path, which lodge 0.2 kept at "confirmed by anyone".

## Reasoning

The final check (`task-final-check.md`, B-1) ran two probes over `MemoryStore` with people `ada` and `bo`: after `bo` confirms a decision awaiting `ada`, `ada`'s `confirm` throws `StaleList` (`ts/src/app/confirm.ts:40`), while the flag still awaits `ada` (`ts/src/core/derive-flags.ts:99-113`).
The core test `touching_two_people_waits_for_both` builds the second confirmation as a record, so it never met this path.
For one person the reading is unchanged, so the carried tests hold.
Cost if wrong: a rule where one owner's confirmation settles the list for all needs the person argument removed again, one parameter in three call sites.
