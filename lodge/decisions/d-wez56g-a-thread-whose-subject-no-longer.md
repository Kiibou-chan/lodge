---
id: d-wez56g
kind: decision
title: "A thread whose subject no longer resolves is shown, not refused"
scope: process
decided_by: coordinator
date: 2026-10-31T02:21:31+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-viewer.md"
---

`ThreadShown.about` becomes `Level1 | None`: a thread whose `about` names no record is shown with its messages and the line "about ID, not found", and `lodge thread` and the viewer never fail on it.

## Reasoning

Task 4's `Lodge.thread` raised `KeyError` for such a thread (`src/lodge/app/threads.py:122` at a64c88e), so `lodge thread` would print a traceback (Task 4 review, I1, `docs/superpowers/plans/2026-10-31-lodge-viewer/task-4-review.md`).
The design names this state, and check 2 already fails it (design, Doubts and questions), so reads must still show the thread, as they show any record failing a check (LODGE-9).
It changes a Produces line of Task 4 that Task 5's `thread_head` consumes, so both are fixed in one round.
Cost if wrong: one optional field the later viewer tasks must handle; no record format changes.
