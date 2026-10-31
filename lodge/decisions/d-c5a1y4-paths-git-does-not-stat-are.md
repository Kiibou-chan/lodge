---
id: d-c5a1y4
kind: decision
title: "Paths git does not stat are read from disk, and git's stat shortcuts are turned off"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

Index entries flagged assume-unchanged or skip-worktree (`git ls-files -t -v`) are read from disk on every fast identity, the list cached by the stat of git's index file; `git diff-files` and `git diff-index` run with `core.fsmonitor=false`, `core.checkStat=default`, and `core.trustctime=true`.

## Reasoning

The feasibility review's F2 and the correctness review's I2: both flags hide an edited file from `git diff-files`, and a sparse checkout marks files absent from disk.
An fsmonitor or a minimal stat check makes git trust less than lodge's equality needs.
Cost if wrong: one more git call when git's index file changed.
