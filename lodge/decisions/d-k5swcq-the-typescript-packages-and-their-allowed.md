---
id: d-k5swcq
kind: decision
title: "The TypeScript packages and their allowed imports carry lodge 0.2's table over"
scope: process
decided_by: planner
date: 2026-11-02T14:10:32+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 6"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 8"}
  - {value: "5-13", handle: "tests/structure_tables.py:5-13"}
  - {value: "93-96", handle: "src/lodge/core/fileformat.py:93-96"}
---

The TypeScript packages and their allowed imports are `core` (none), `app` (`core`), and the adapters `store` (SQLite), `git` (the importer's reads and the export's commits), `api` (the HTTP server and sign-in), `cli`, and `hook`, each importing `app` and `core` only, with `main` the composition root that imports all.
Another package is imported only through its alias `#name`, which resolves to its `index.ts`, and a relative import never leaves its package.
`core` imports only its own modules, `yaml`, and `@noble/hashes`.

## Reasoning

The design carries today's structure rules over (design, "Constraints"), and lodge 0.2's table is `core` none, `app` `core`, each adapter `app` and `core`, `main` all (`tests/structure_tables.py:5-13`, s-ctywm6).
`gitstore` was both the store and the only package touching git (s-nzhyh3); on the server those are two jobs, the SQLite store and the git work of the importer and the export, so each gets an adapter row of its own; `api` takes the viewer's row, since it is the HTTP adapter.
A `#name` alias makes a front-door import one rule for dependency-cruiser to check, and tsc, Bun, and dependency-cruiser all resolve it (probe 6); Python's ban on relative imports (`pyproject.toml`, `ban-relative-imports = "all"`) becomes a ban on relative imports that leave the package.
`core` needs YAML, as Python's core needs PyYAML (`CORE_MODULES`), and SHA-256 for `content_hash` (`src/lodge/core/fileformat.py:93-96`), as it uses `hashlib`; `@noble/hashes` gives the same digest (probe 8) and holds no randomness, where `node:crypto` would bring randomness into `core`.
Cost if wrong: a later plan that needs another edge records it as the author's call (`CLAUDE.md`, "Structure checks").
