---
id: d-hpds8j
kind: decision
title: "Each server plan builds in its own Sonnet task session"
scope: process
decided_by: author
date: 2026-11-14T20:31:40+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
quote: {text: "A", where: "lodge build session", when: "2026-11-14T20:31:11+01:00"}
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"}
  - {value: "200", handle: "gloss docs/design/decisions.md, CTXWIN-1"}
  - {value: "3", handle: "gloss docs/design/decisions.md, COORD-1"}
---

Plans 2 to 4 each build in a background Sonnet task session, started by the build session with Remote Control on and compacting at 200k tokens; it steers Codex, runs the gates, dispatches reviews at each step's model, and keeps the ledger; it escalates questions for the author, conflicts with a plan or decision, another plan's interface, fix round 3, and anything touching `main`; each task's cost is logged.

## Reasoning

Asked as SUBCO-1 in the lodge build session, after the author asked for gloss's subcoordinator rulings; she answered "A".
It follows gloss's COORD-1, CTXWIN-1, and CR-277, with lodge's own launcher and rules file in place of gloss's, whose rules carry gloss's lock and Codex wrapper.
Why: cost is calls times context; gloss's single coordinator on another machine spent almost all of a $119 day re-reading a context of about 243k tokens on each of 823 calls (gloss COORD-1), and this build session's context is long.
Gloss's trial of COORD-1 made no cost comparison, so lodge logs cost per task to make one.
Cost if wrong: a task session misses context this session holds and asks or rules wrongly; its milestone reports list every ruling, so this session can overturn one before the plan's branch merges.
