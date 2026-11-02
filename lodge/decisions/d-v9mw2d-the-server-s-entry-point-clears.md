---
id: d-v9mw2d
kind: decision
title: "The server's entry point clears the yaml package's logging variables"
scope: process
decided_by: coordinator
date: 2026-11-02T17:37:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, The rest of build step 1"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md, C-6"}
---

The `yaml` package reads `LOG_TOKENS` and `LOG_STREAM` from the environment and then prints header text; it is the one known way the environment reaches `core`, and plan 3's entry point deletes both variables before it serves, with a test.

## Reasoning

The review ran `LOG_TOKENS=1 LOG_STREAM=1` over `loadYaml` and saw every token printed (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md`, C-6; `ts/node_modules/yaml/dist/parse/parser.js:178`, `compose/composer.js:139`), and no option of the package turns the reads off.
The structure test scans `ts/src` only, so it cannot see this; the entry point is the one place that owns the process's environment (d-k5swcq, `main`).
Cost if wrong: a server started with either variable set logs decisions' text until the entry point clears them.
