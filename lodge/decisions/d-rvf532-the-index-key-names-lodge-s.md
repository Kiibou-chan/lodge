---
id: d-rvf532
kind: decision
title: "The index key names lodge's build and its dependencies, and builds keep separate files"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The index key includes lodge's build, the Python, PyYAML (and whether libyaml is used), and SQLite versions.
Different builds keep separate index files instead of wiping each other, with a pruning rule bounded by size.

## Reasoning

The correctness review's I6: worktrees share the git common dir, and two builds alternating would empty one shared index at every switch; the parse also depends on Python's Unicode tables, PyYAML, and libyaml, and FTS on SQLite.
The coordinator's ruling 4 for the fix round.
Cost if wrong: disk space for a second build's index.
