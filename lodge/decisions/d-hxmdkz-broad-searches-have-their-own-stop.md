---
id: d-hxmdkz
kind: decision
title: "Broad searches have their own stop at 1.0 s warm"
scope: process
decided_by: coordinator
date: 2026-10-31T23:12:39+01:00
narrows: [d-gd00c6]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "5,000", handle: "d-me8vm3"}
  - {value: "1.0 s", handle: "the coordinator's ruling"}
  - {value: "160,000", handle: "the brief's ruling 3"}
  - {value: "0.3 s", handle: "d-232gxs"}
  - {value: "0.723 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-codex.md, F6"}
---

Searches with more than 5,000 candidates are measured and reported apart, with their own stop at 1.0 s warm on the 160,000-file store; the 0.3 s stop covers `show`, `waiting`, `threads`, `thread`, and searches with at most 5,000 candidates.

## Reasoning

The feasibility review's F6 measured scoring alone at 0.723 s for a broad query, before any other phase; an agent's broad search is rarer than its `show`, and `--brief` with a limit keeps the output small.
The coordinator's ruling on d-gd00c6.
Cost if wrong: broad searches stay near 1 s.
