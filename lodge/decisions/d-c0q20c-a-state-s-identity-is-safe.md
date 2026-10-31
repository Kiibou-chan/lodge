---
id: d-c0q20c
kind: decision
title: "A state's identity is safe one way; the build compares listings for the identical-state shortcut"
scope: process
decided_by: planner
date: 2026-10-31T23:07:56+01:00
narrows: [d-ana6c0]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Equal identities imply equal exact trees; unequal identities may still hold equal trees (an edit later committed, an attachment's bytes committed, a working tree reverted to the published contents while `HEAD` differs), which costs a rebuild, never a wrong read.
When a state is built, the identical-state shortcut (d-zyqzkg) compares the two listings' blob mappings and attachment sets, not their identities.

## Reasoning

The correctness recheck's N2 and the feasibility recheck's F1: an overlay hash and the tree ID a commit later gives are different strings for the same files, and a canonical identity would need a `git mktree` of the applied overlay on every read.
Every consumer of the identity (the state key, the facts key, the shortcut) needs only the one direction.
Cost if wrong: a rebuild after a commit of an edit already read.
