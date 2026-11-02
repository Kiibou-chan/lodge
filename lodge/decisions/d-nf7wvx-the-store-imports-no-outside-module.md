---
id: d-nf7wvx
kind: decision
title: "The store imports no outside module but Kysely and bun:sqlite, which a rule checks"
scope: process
decided_by: planner
date: 2026-11-02T19:36:02+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "579fb11", handle: "git log -1 --format=%h origin/server-core"}
  - {value: "9", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 9"}
---

A dependency-cruiser rule `store-imports` refuses any built-in module but `bun:sqlite` and any npm package but those of `STORE_NPM` in `ts/tests/structure/table.ts`, which holds `kysely` alone, in an import from `ts/src/store`; it tightens the structure rules and loosens none.

## Reasoning

The plan says the store imports only `#app`, `#core`, `kysely`, and `bun:sqlite`, but plan 1's rules hold only the confinements there (`core-imports` and `app-imports` in `ts/.dependency-cruiser.cjs` on `server-core`, practice review P-M9), so a builder could import another package and the gate would stay green.
The rule, planted in a copy of `ts/` at `server-core` 579fb11, passes `bun:sqlite`, `#core`, and `#app` and finds `node:fs` and `yaml` (probe 9 of `docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md`), and it reads its list from `table.ts` as `core-imports` reads `CORE_NPM`.
Cost if wrong: a later plan that needs another package in the store adds it to `STORE_NPM`, which is the author's call, as adding an allowed edge is (`CLAUDE.md`, "Structure checks").
