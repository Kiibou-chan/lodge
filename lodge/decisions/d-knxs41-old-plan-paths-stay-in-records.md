---
id: d-knxs41
kind: decision
title: "Old plan paths stay in records and frozen files after the move to done"
scope: process
decided_by: coordinator
date: 2026-10-31T09:40:36+01:00
work_item: "docs/superpowers/plans/done/2026-10-31-lodge-viewer.md"
numbers:
  - {value: "0", handle: "CLAUDE.md, the rule on moving a plan to done"}
  - {value: "7", handle: "git grep -l 'plans/2026-10-31-lodge-viewer' -- lodge/decisions | wc -l"}
  - {value: "5", handle: "git grep -n 'plans/2026-10-31-lodge-viewer' -- docs/superpowers/specs"}
---

When a plan moves to `docs/superpowers/plans/done/`, links to its old path are fixed in editable files only; decisions and files matching a `frozen` glob in `.lodge.toml` keep the path they were written with.

## Reasoning

`CLAUDE.md` asks that `git grep 'plans/<file>'` give 0 outside `done/`, but after the lodge-viewer move it gives 7 decisions (for example d-azeks4 and d-na1eg7) and the frozen viewer design (line 5), none of which may be edited (decisions only through `lodge add`, the design by its `frozen` entry).
A path in those files names where the plan was when they were written, and `git log --follow` on the new path finds it.
Cost if wrong: a reader of an old decision follows a dead path once and finds the plan by its file name under `done/`.
