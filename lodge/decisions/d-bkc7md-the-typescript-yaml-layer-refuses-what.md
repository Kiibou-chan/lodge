---
id: d-bkc7md
kind: decision
title: "The TypeScript YAML layer refuses what PyYAML refuses and keeps the text's key order"
scope: process
decided_by: planner
date: 2026-11-02T14:50:58+01:00
replaces: [d-458jhp]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "100", handle: "this decision's statement, a chosen bound"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "0001", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7 (U+0001)"}
  - {value: "5,000", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 7"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding I-3"}
  - {value: "13", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-13"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-1"}
  - {value: "101", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-1"}
  - {value: "400", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-1"}
  - {value: "500", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-1"}
  - {value: "450", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-1"}
---

The TypeScript core reads headers with the `yaml` package's failsafe schema, walking its nodes into a `Map` per mapping in the text's key order.
It refuses as a `YamlError` with its line two documents, a tag other than `!`, `!!str`, `!!seq`, and `!!map` or one on another kind of node, a non-scalar key (`found unhashable key`), and a character PyYAML's reader refuses.
Nesting beyond 100 levels gets Python's message and no line, a fixed bound narrowing lodge 0.2.

## Reasoning

The `yaml` package reports `!!int` and `!!python/name` tags only as warnings, passes U+0001, parses two documents, and parses 5,000 nested brackets without error (probe 7), where lodge 0.2 refuses each (`tests/core/test_yamlio.py`).
It also loads `[title]: x` and `{a: b}: c` with no error, as the keys `"[ title ]"` and `"{ a: b }"`, writing a warning through `console` from inside `core`, and its `toJS()` puts the key `1` before `zz` where Python's dict keeps the text's order (`plan-review-correctness.md`, I-3); walking the nodes avoids both, and a `Map` keeps the order in which `check_keys` and `read_map` meet the keys (`src/lodge/core/fields.py:27-33` and `:76-80`).
PyYAML reads the non-specific tag `!` as an untagged node (`lodge.core.load_yaml("a: ! b\n")` gives `{'a': 'b'}`, M-13 of that review), so refusing it would refuse headers lodge 0.2 reads.
A header must not be read by the server that lodge 0.2 refuses, or the importer and the export would hold records 0.2 cannot read back.
lodge 0.2 loads a header nested 101 to 400 levels and refuses one of 500 with no line (`src/lodge/core/yamlio.py:61-62`; M-1 of that review); its threshold follows the recursion limit, so a fixed bound is the only one TypeScript can match, and 100 is far beyond any record's header, whose deepest value is a list of maps such as `changes`.
Cost if wrong: a header nested between 101 and about 450 levels, which no record has, is refused after import, and the importer reports it.
