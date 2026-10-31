---
id: d-dqpf59
kind: decision
title: "Conversion sources come from git itself, and autocrlf is read in git's boolean spellings"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The conversion check of d-atsx8n takes the attributes files from `git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM`, `core.attributesFile`, `info/attributes`, and every `.gitattributes`; `core.autocrlf` in any spelling of true, or `input`, reads every path from disk; the result is cached by the bytes of those files and the configuration values.
Test helpers set `HOME` and `XDG_CONFIG_HOME` to the test's folder.

## Reasoning

The correctness review's I1 and the feasibility review's F3: a global attributes file in `~/.config/git/attributes` converted a file while the planned check saw nothing, and `core.autocrlf=yes` is true to git but not to a string comparison.
Cost if wrong: a read slower where conversions apply, never a wrong one.
