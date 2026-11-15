---
id: d-s83a6e
kind: decision
title: "Plan 4's server task extends plan 3's code by names only"
scope: process
decided_by: planner
date: 2026-11-02T20:29:33+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, the plan's own number"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Task 8"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at 9ac93ac, the plan's own number"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at 9ac93ac, Task 6"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Task 10"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/preflight.md, M1"}
---

Plan 4's Task 8, built after plan 3 merges, adds names to plan 3's code and changes the shape of none: `tomlTable(text)` factored out of `readSettings`, `import` and `export-target` dispatched from `person.ts` as `approve` is, an optional `ApiOptions.moving`, and `world.ts`'s `exporters`, `targets`, `createProject`, and `asPerson`; exports start in `main.ts`'s `listen`, and Task 10 uses `world.ts`.

## Reasoning

The preflight scan found four gaps a builder cannot close from the plans (`docs/superpowers/plans/2026-11-02-lodge-server-import/preflight.md`, M1 to M3 and M16): plan 3 parses `.lodge.toml` only inside `readSettings(root)`, a function of a folder, so no function takes the text `readStore` gives; its test world and test server expose no exporter; its fix round 4 removed `asPerson`, so no test helper makes the signed-in person's request; and it names no table or 422 helper for the person's operations.
Each is closed by a name the task adds in plan 3's files, and the coordinator substitutes a merged name where plan 3 already has one, so plan 3's plan need not change.
`moving` is optional because a required member would fail `tsc` on every other `ApiOptions` literal, which only the merged code lists (M15).
The exports start in `listen`, not in `open`, because `open` also serves `setup`, which exits without serving (M10), and `ServerParts` has only `options`; a closure in `main.ts` needs no new member there.
`createProject` makes the test project directly, as the world makes `work`, since plan 3 states a token's rule for `project-create` and not a session's (M3), and Task 10 uses `world.ts`, whose person is `ada`, since the e2e server's person `author` would hide the mapping (M4).
Cost if wrong: if plan 3's merged code answers a person's operation differently from `approve`, or registers its operations elsewhere, Task 8's brief names that place instead, a brief edit; a plan 3 test that builds `ApiOptions` by spreading a world could see `moving`, which is optional and harmless.
