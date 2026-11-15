---
id: d-v92j1d
kind: decision
title: "Preserve the Python structure rules beside TypeScript"
scope: product
decided_by: coordinator
date: 2026-11-15T05:00:48+01:00
changes:
  - {entry: s-165qfh, action: edit}
  - {entry: s-a4jfp1, action: edit}
narrows: [d-7s8k61]
numbers:
  - {value: "0.2", handle: "pyproject.toml, project.version"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 4"}
  - {value: "300", handle: "tests/structure_tables.py MAX_LINES; ts/tests/structure/table.ts MAX_LINES"}
---

Python and TypeScript each retain explicit structure rules.
The server language claim names its settling decision.

## Reasoning

I1 restores the Python rules carried by d-jxwj8m and the pre-import s-165qfh, rather than treating ast as their whole meaning.
The Python allowed-imports table, cycles, front doors, size, and forbidden calls remain; tests/structure_rules.py, tests/structure_calls.py, and tests/structure_imports.py enforce them.
The TypeScript sentence names its own graph, parser, size, and purity checks.
M9 identifies d-b1yjpp for the TypeScript language choice.
This narrows d-7s8k61 only to correct these entry descriptions; its other constraints, source rulings, and earlier narrowings remain.
No: d-jxwj8m and d-b1yjpp remain the sources, and no author decision is narrowed or replaced.
