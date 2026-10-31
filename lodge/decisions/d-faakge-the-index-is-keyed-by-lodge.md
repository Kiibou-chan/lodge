---
id: d-faakge
kind: decision
title: "The index is keyed by lodge's source bytes and dependencies, valid over a time interval"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
replaces: [d-f3r5aq]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "273,039", handle: "python -c over the installed lodge package's .py and .md files, in the plan report"}
  - {value: "2.3 ms", handle: "the same command"}
---

Every stored result is keyed by the index's schema number and a digest of lodge's own source bytes, the Python version, the PyYAML version and whether libyaml is used, and the SQLite version, one index file per digest; a state's result is also keyed by a digest of the core settings and is valid while the time lies in the interval between the latest new decision dated before its build and the earliest dated after it.

## Reasoning

The feasibility review's F16: a same-size file with its mtime restored kept a name, size, and mtime digest; hashing the 273,039 bytes of lodge's sources took 2.3 ms.
The feasibility review's F13 and the correctness review's M1: a reader whose clock is behind the build's would miss a future-date problem, which only an interval with both ends rules out.
Coordinator ruling 4 of the fix round.
Cost if wrong: a rebuild when a dependency changes.
