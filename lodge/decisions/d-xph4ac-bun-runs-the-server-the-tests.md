---
id: d-xph4ac
kind: decision
title: "Bun runs the server, the tests, the gate's tools, and the binaries"
scope: process
decided_by: planner
date: 2026-11-02T14:51:03+01:00
replaces: [d-03xx0a]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1.3.14", handle: "bun --version"}
  - {value: "2", handle: "lodge show ARCH-2"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 4"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 1"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 3"}
  - {value: "20", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 20"}
---

Bun (1.3.14 here) runs the server, the tests (`bun test`), and the gate's tools (`bun --bun run check`), and builds the command and the runner with `bun build --compile`; Node is used nowhere.

## Reasoning

The command and the runner ship through `bun build --compile` (ARCH-2; design, "Constraints"), and a compiled program runs on Bun's runtime, so tests on Bun test the runtime that ships.
SQLite ties the server to one runtime: Bun cannot import `node:sqlite` and Node cannot import `bun:sqlite` (probe 4), and `bun:sqlite` works through Kysely and inside a compiled binary (probes 1 and 3).
`tsc`, dependency-cruiser, and knip start with a `node` shebang, so `bun run check` runs them on Node wherever Node is installed and on Bun elsewhere (`plan-review-practice.md`, P-M3); under `bun --bun run` the name `node` is Bun's own, and all three run on Bun as under Node (probe 20).
One runtime for everything means a tool that breaks under one runtime breaks on every machine, not on some.
Cost if wrong: moving to Node means a second SQLite binding behind the storage port, and the tests' `expect` calls rewritten to `node:assert`; a tool that fails on Bun drops the flag for that tool alone.
