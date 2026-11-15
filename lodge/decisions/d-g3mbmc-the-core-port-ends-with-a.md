---
id: d-g3mbmc
kind: decision
title: "The core port ends with a differential run against lodge 0.2 on this repository's records"
scope: process
decided_by: planner
date: 2026-11-02T14:10:41+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "16", handle: "JavaScript strings are UTF-16"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
  - {value: "175", handle: "ls lodge/decisions | wc -l"}
  - {value: "155", handle: "ls lodge/spec/*/ | wc -l"}
---

The first plan's last task runs the TypeScript core and lodge 0.2 on this repository's own records and compares what they derive: the rendered specification, the check's problems, every record's three levels, and search results; any difference is a finding.

## Reasoning

The carried tests prove the behaviour they test; the port also crosses differences no test names, such as Python's Unicode-aware `\w` and `\b` against JavaScript's ASCII ones, sorting by code point against UTF-16 code units, and PyYAML against the `yaml` package, which differs on tags, control characters, document count, and nesting (probe 7).
This repository holds 175 decisions and 155 files under `lodge/spec/` (`ls lodge/decisions | wc -l`, `ls lodge/spec/*/ | wc -l`), written by many sessions, a wider sample than the made-up fixtures.
The run reads the records in place and commits only a count, so no record becomes a test fixture (`CLAUDE.md`, "Hard rules").
Cost if wrong: one task of the coordinator's time and a script that is not shipped.
