---
id: d-5kskm3
kind: decision
title: "The page, its script, and the guide are text imports"
scope: process
decided_by: planner
date: 2026-11-02T19:16:35+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 3"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "25", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, probe 25"}
---

The page and its script are text imports into `api`, the page cast to a string and the script typed by a declaration of its own, and the guide is a text import into `cli`; all are embedded in the compiled binary.

## Reasoning

`api` reads no file (d-x6f9za; `Bun.file` outside `git` and `cli` is refused by `ts/tests/structure/calls.ts`), and a compiled binary has no folder beside it to read from.
`bun-types` types an HTML import as `HTMLBundle`, so `tsc` refuses it as a string until it is cast, and a declaration of `*.html` collides with Bun's; `*/page.js` declared alone type-checks; Biome lints both files, the gate passes, and the compiled binary prints both texts with the files moved away (the plan's probe 3; plan 1, probe 25).
As `.html` and `.js` files rather than strings in TypeScript, Biome checks them.
Cost if wrong: the assets become strings in TypeScript modules.
