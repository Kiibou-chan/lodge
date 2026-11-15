---
id: d-458jhp
kind: decision
title: "The TypeScript YAML layer refuses what PyYAML refuses"
scope: process
decided_by: planner
date: 2026-11-02T14:22:41+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
  - {value: "100", handle: "this decision's statement, a chosen limit"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "5,000", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
---

The TypeScript core reads headers with the `yaml` package's failsafe schema and refuses on top of it what PyYAML refuses and the package lets through: more than one document, an explicit tag other than `!!str`, `!!seq`, and `!!map`, a character PyYAML's reader refuses, and nesting deeper than 100, each as a `YamlError` with its line.

## Reasoning

The `yaml` package reports `!!int` and `!!python/name` tags only as warnings, passes U+0001, parses two documents, and parses 5,000 nested brackets without error (probe 7), where lodge 0.2 refuses each (`tests/core/test_yamlio.py`).
A header that lodge 0.2 refuses must not be read by the server, or the importer and the export would hold records 0.2 cannot read back.
PyYAML refuses deep nesting through Python's recursion limit, which has no fixed depth; 100 is far beyond any record's header, whose deepest value is a list of maps such as `changes`.
Cost if wrong: a header nested deeper than 100 levels, which no record has, is refused.
