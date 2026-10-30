---
id: d-b576zz
kind: decision
title: "An add waits for the next second only when the newest decision is at most three seconds ahead"
scope: process
decided_by: coordinator
date: 2026-10-30T02:19:05+01:00
narrows: [d-g2p3ng]
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
---

`add` waits through the clock's `sleep` until its date is after the newest decision in the current tree, at most three times, and not at all when the newest decision is more than three seconds ahead of the clock.

## Reasoning

Final wave B2 item 17 (done ledger line 205; `docs/superpowers/plans/done/2026-10-29-lodge/final-wave-b2-report.md`, item 17) bounded the wait.
The code is `_after_newest` and `_WAITS` in `src/lodge/app/writes.py:30` and `:141-157`.
A decision dated further ahead is left to check 1, which refuses a change related to it.
