---
id: d-q0tb8r
kind: decision
title: "The gate and add take nothing derived from the index, and key parses by the bytes they read"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "2 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

The gate and `add` never take derived state, flags, or claims about a tree from the index.
The parse cache is keyed by the bytes actually read, hashed by lodge, never by a blob ID git reports for a working-tree file.

## Reasoning

The feasibility review's F2: git's index flags (assume-unchanged, skip-worktree) hide an edited file from `git diff-files`, so a key trusted from git would hand the gate a stale parse.
The coordinator's ruling 2 for the fix round.
Cost if wrong: the gate and `add` read every working-tree file, about 2 s at 160,000 files.
