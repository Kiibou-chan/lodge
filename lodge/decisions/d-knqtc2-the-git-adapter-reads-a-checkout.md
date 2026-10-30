---
id: d-knqtc2
kind: decision
title: "The git adapter reads a checkout or a branch, and the first user's records live on a branch"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:22+01:00
changes:
  - {entry: s-6bc10p, action: create}
  - {entry: s-hjf8cc, action: create}
  - {entry: s-sgprxs, action: create}
---

The git adapter reads and writes either the current checkout or a named branch kept in its own worktree. In the first user the records live on a branch that never merges, and lodge's own data lives on lodge's main.

## Reasoning

The first user's branch that never merges is the author's call (LODGE-1), chosen over records on `main` landing with merges.

A specification change therefore does not travel on the work branch that implements it, so the decision names that branch in `work_item`, as the first user's lines that record what was built, and on which branch, do today.

The adapter fetches before reads when stale and pushes after writes, retrying on a rejected push; the staleness bound and the retry policy are left to the builder.
