---
id: d-vfyex3
kind: decision
title: "lodge is one program: the command, and lodge server setup and serve"
scope: process
decided_by: planner
date: 2026-11-02T19:16:30+01:00
narrows: [d-yayhct]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "0.3.0", handle: "ts/package.json, version"}
---

There is one program, `lodge`: `src/main.ts` sends `lodge server setup` and `lodge server serve` to `api` and every other command to `cli`, which narrows d-yayhct's `lodge-server setup`; its version is that of `ts/package.json`, 0.3.0.

## Reasoning

The structure rules allow one file at the root of `src`, `src/main.ts` (`ts/tests/structure/calls.ts`, `layoutViolations`; d-k5swcq), and a second entry file is a new place in the table, which is the author's call (`CLAUDE.md`, "Structure checks").
`Bun.serve` is allowed only in `api` (`ts/tests/structure/calls.ts`, `sockets outside api`), so the server is `api`'s code whichever file starts it.
A compiled command binary is 94,582,912 bytes before any of the server's code (plan 1, probe 3), so one binary costs little more than two.
lodge 0.2 is 0.2.0 (`pyproject.toml`), and the server build changes where the records live (design line 72).
Cost if wrong: a second entry point, recorded with the author, and a second build line.
