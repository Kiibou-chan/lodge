---
id: d-xdqsmf
kind: decision
title: "The server build runs in parallel lanes, and plans 2 to 4 are planned during plan 1's build"
scope: process
decided_by: author
date: 2026-11-02T18:41:50+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
quote: {text: "Yes, parallelise", where: "lodge build session", when: "2026-11-02 18:40"}
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, The rest of build step 1"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, The rest of build step 1"}
---

Plan 1's remaining tasks run in parallel lanes, each in its own worktree and merged into the build branch, where the import graph of `src/lodge/core` lets them; plans 2 to 4 are planned at the same time as plan 1's build, each on its own branch.

## Reasoning

Yes, parallelise
