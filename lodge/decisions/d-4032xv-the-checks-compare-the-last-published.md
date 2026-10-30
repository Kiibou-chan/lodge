---
id: d-4032xv
kind: decision
title: "The checks compare the last published state with the state about to be published"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:19+01:00
changes:
  - {entry: s-zv83s7, action: create}
  - {entry: s-edgt71, action: create}
---

The same change is the difference between the last published state and the state about to be published.
Reads and the viewer run all seven checks against the published state, and only the gate and add refuse.

## Reasoning

Three of the checks need a before and an after, so the check takes two snapshots, and the Store port gives the current and the published snapshot; a server can also give both, and no history beyond that is needed.

The published state is the remote tip of the shared branch, or the merge base with `main` where a project keeps records on its work branches.

'The same change' as the difference between two states, and the choice of published state, are the specification author's calls, marked in the design document for the author to check.

Reads run all seven against the published state (LODGE-9), so a hand edit of a published decision shows as failing everywhere, rather than only at the gate.

That is the author's choice over keeping the three comparing checks at the gate only.
