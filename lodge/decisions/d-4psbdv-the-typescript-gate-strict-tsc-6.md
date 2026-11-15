---
id: d-4psbdv
kind: decision
title: "The TypeScript gate: strict tsc 6, Biome, dependency-cruiser, knip, bun test, and a structure test"
scope: process
decided_by: planner
date: 2026-11-02T14:10:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "6.0.3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 11"}
  - {value: "7.0.2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 5"}
  - {value: "0", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 5"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 5"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 6"}
  - {value: "300", handle: "tests/structure_tables.py, MAX_LINES"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 10"}
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 11"}
---

The TypeScript gate, `scripts/check-ts.sh`, runs Biome's format and lint check, `tsc --noEmit` with TypeScript 6.0.3 in strict mode, dependency-cruiser over the import graph, knip for unused files, exports, and dependencies, and `bun test`, whose structure test checks sizes and calls.
Every dependency is pinned to an exact version published at least two weeks before it is added.

## Reasoning

These take the places of `scripts/check.sh`'s Ruff format, Ruff, mypy strict, Vulture, and pytest one for one.
TypeScript 7.0.2 has no JavaScript API (`createSourceFile` is `undefined`), and dependency-cruiser then cruises 0 modules; with 6.0.3 it finds every violation the probe planted (probe 5).
dependency-cruiser enforces the design's "dependency checker over the TypeScript import graph" (design, "Constraints"): allowed imports, front doors, cycles, and no `node:` or `bun:` module in `core` (probes 5 and 6).
Calls are not imports, so the clock, randomness, `process`, `fetch`, `console`, `eval`, and dynamic imports in `core` and `app`, and the 300-line limit, are checked by a test that walks each file with TypeScript's own parser, as `tests/structure_calls.py` walks Python with `ast`.
Biome is one program for formatting and linting, as Ruff is; knip reports unused files, exports, and dependencies, as Vulture reports unused names (probe 10).
A version two weeks old has had time for a bad release to be noticed and pulled; the dates are in probe 11.
Cost if wrong: one tool swapped in `scripts/check-ts.sh` and its configuration file.
