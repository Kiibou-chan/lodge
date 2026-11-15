---
id: d-03xx0a
kind: decision
title: "Bun runs the server, the tests, and the binaries"
scope: process
decided_by: planner
date: 2026-11-02T14:10:30+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1.3.14", handle: "bun --version"}
  - {value: "2", handle: "ARCH-2, docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 4"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 1"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 3"}
---

Bun (1.3.14 here) runs the server, the tests (`bun test`), and builds the command and the runner with `bun build --compile`; Node is not used.

## Reasoning

The command and the runner ship through `bun build --compile` (ARCH-2; design, "Constraints"), and a compiled program runs on Bun's runtime, so tests on Bun test the runtime that ships.
SQLite ties the server to one runtime: Bun cannot import `node:sqlite` (`error: Could not resolve: "node:sqlite"`) and Node cannot import `bun:sqlite` (`ERR_UNSUPPORTED_ESM_URL_SCHEME`) (probe 4, `docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md`).
`bun:sqlite` works through Kysely and inside a compiled binary (probes 1 and 3), and `bun test` runs TypeScript with no build step and needs no socket for a handler test (probe 1).
Node's own SQLite returns rows with a null prototype, so `deepStrictEqual` against a plain object fails (probe 4), one more difference a second runtime would bring.
Cost if wrong: moving to Node means a second SQLite binding behind the storage port and the test runner's `expect` calls rewritten to `node:assert`.
