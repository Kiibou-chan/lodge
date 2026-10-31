---
id: d-rs76ks
kind: decision
title: "Index reads equal in-memory reads, by a property test, or take the in-memory path"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A read through the index prints what the in-memory read prints, shown by a property test over the bench stores with random edits (create, edit, delete, untracked, touched only, CRLF attributes, assume-unchanged and skip-worktree).
Where the index cannot prove equality, such as a phrase or code made only of function words, the read takes the in-memory path.

## Reasoning

The correctness review's I3 and I5 found index answers that differ from memory: published check problems absent from a stored state, and search candidates missing for function-word phrases and codes.
The coordinator's ruling 3 for the fix round.
Cost if wrong: some reads stay at the in-memory cost.
