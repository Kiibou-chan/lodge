---
id: d-pfdqpp
kind: decision
title: "Task views show work state and permit reasoned movement"
scope: product
decided_by: coordinator
date: 2026-11-15T05:12:32+01:00
changes:
  - {entry: s-h1e6jc, action: create}
  - {entry: s-bxws89, action: create}
  - {entry: s-pyr5rx, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:21-25, 98, 111, 175"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 3"}
---

Task pages and boards expose work state, and a person can move a task on or send it back with a recorded reason.

## Reasoning

Tasks, lines 174 to 176, makes task state visible at a glance and retains reasons for backwards movement in a thread. The board layout and nesting child cards inside a plan are [my call] at line 175. d-5ps72w approves these claims. Build order assigns task pages and the board to step 3, but assigns no step specifically to the person's go and return-with-reason claim; the coordinator approves leaving that claim unnumbered rather than guessing. Code links already exist as a model claim in s-1csktg; the task-page entry specifies their presentation, not code-view implementation.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
