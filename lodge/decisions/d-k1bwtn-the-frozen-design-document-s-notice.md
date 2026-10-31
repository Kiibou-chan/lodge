---
id: d-k1bwtn
kind: decision
title: "The frozen design document's notice goes at its end, not its top"
scope: process
decided_by: coordinator
date: 2026-10-31T01:02:12+01:00
work_item: "docs/superpowers/plans/2026-10-30-lodge-on-itself.md"
numbers:
  - {value: "25", handle: "docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-review.md, I1"}
  - {value: "15", handle: "docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-review.md, I1"}
---

The notice that the design document is frozen and that the specification lives in lodge stands at the end of the document, not at its top as the plan's Task 5 said.

## Reasoning

A notice at the top shifted every line of the document two lines down, so 25 handles of the form `lodge-design.md:N` in 15 records pointed two lines early, and `lodge check` cannot notice that (Task 5 review, I1, `docs/superpowers/plans/2026-10-30-lodge-on-itself/task-5-review.md`).
At the end, every line keeps its number, and a reader who opens the document still sees the notice in the first screen of `git log` and at the hook's advice.
Cost if wrong: a reader who opens the document without lodge reads it as current until the end; the hook and `CLAUDE.md` both say it is frozen.
