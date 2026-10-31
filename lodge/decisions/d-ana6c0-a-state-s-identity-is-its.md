---
id: d-ana6c0
kind: decision
title: "A state's identity is its tree ID when nothing differs on disk"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A checkout state's identity is the `HEAD` tree ID of `lodge/` when its overlay is empty, and otherwise a hash of that tree ID and the sorted overlay; an overlay entry whose bytes hash to the base's blob at that path, or a deletion of a path the base lacks, is dropped, and an attachment counts by presence only.
The published identity is the merge base's tree ID, and in branch mode the tip's.

## Reasoning

The correctness review's B2 and the feasibility review's F1: `git diff-files` names a touched file whose bytes did not change, and a hash over an empty overlay is never a tree ID, so a clean checkout would never equal its published state.
Cost if wrong: an identical-state read compared in full, never a wrong one.
