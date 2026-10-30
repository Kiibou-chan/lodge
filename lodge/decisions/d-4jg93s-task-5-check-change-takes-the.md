---
id: d-4jg93s
kind: decision
title: "Task 5: check_change takes the current time, and check 1 fails a decision dated after it"
scope: process
decided_by: coordinator
date: 2026-10-29T16:16:12+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 75"}
---

I2, `check_change` gains a fourth parameter `now: datetime` (timezone-aware), and check 1 fails a new decision, imported or not, dated after `now`.

## Reasoning

One future-dated record otherwise blocks every later change to what it touches (task-5-review.md, I2, run), against "one bad record never blocks everyone", and the spec's Structure has core take the time as a parameter.
Cost if wrong: one parameter through Task 8, whose brief passes `clock.now()` (plan:380 omits `settings` too; Task 8's brief carries both).
Line handles such as spec:N refer to the files at this ruling's date.
