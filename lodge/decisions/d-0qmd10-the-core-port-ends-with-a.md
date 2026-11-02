---
id: d-0qmd10
kind: decision
title: "The core port ends with a differential run against lodge 0.2 on this repository's records"
scope: process
decided_by: planner
date: 2026-11-02T14:51:04+01:00
replaces: [d-g3mbmc]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "16", handle: "UTF-16, the name of the encoding"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
  - {value: "192", handle: "ls lodge/decisions | wc -l, at c3320a4"}
  - {value: "137", handle: "find lodge/spec -type f | wc -l, at c3320a4"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-practice.md, finding P-I10"}
---

The first plan's last task runs the TypeScript core and lodge 0.2 on this repository's own records and compares what they derive and write: the rendered specification, the check's problems, every record's three levels, search results, and, for every record and area file, the text each core's writer gives for the parsed file; any difference is a finding.

## Reasoning

The carried tests prove the behaviour they test; the port also crosses differences no test names, such as Python's Unicode-aware `\w` and `\b` against JavaScript's, sorting by code point against UTF-16 code units, and PyYAML against the `yaml` package (probe 7).
The server stores a record as the text `writeRecord` gives (d-smx3xf) and the export writes it out (design, "Export to git"), so a writer that differs from lodge 0.2's in quoting, key order, or line ends changes every exported file, while the carried tests compare written text for a handful of made-up records only (`plan-review-practice.md`, P-I10).
This repository holds 192 decisions and 137 files under `lodge/spec/` (`ls lodge/decisions | wc -l`, `find lodge/spec -type f | wc -l`, at `c3320a4`), written by many sessions, a wider sample than the made-up fixtures; it holds no threads, so the thread code rests on the carried tests alone.
The run reads the records in place and commits only counts, so no record becomes a test fixture (`CLAUDE.md`, "Hard rules").
Cost if wrong: one task of the coordinator's time and a script that is not shipped.
