---
id: d-x6f9za
kind: decision
title: "The structure rules bind the source, and each adapter keeps its lodge 0.2 package's permissions"
scope: process
decided_by: planner
date: 2026-11-02T14:51:00+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-5"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-practice.md, finding P-I2"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-practice.md, finding P-M8"}
  - {value: "3", handle: "lodge show ARCH-3"}
---

The allowed-import, `core`, `app`, and confinement rules and the call checks bind `ts/src` only; tests and scripts may read and write files.
Each adapter keeps the permissions of the lodge 0.2 package it replaces: `git` those of `gitstore` (processes, reading and writing files), `cli` those of `cli` (reading the drafts it is given), `api` the viewer's place as the HTTP adapter (sockets), and `hook` those of `hook`.
`store` may import `bun:sqlite` and has no file access.

## Reasoning

The structure test plants trees, the parity test reads lodge 0.2's `tests`, and the differential script reads the records, all through `node:fs` (`plan-review-practice.md`, P-I2; `plan-review-correctness.md`, M-5); lodge 0.2's rules likewise walk `src/lodge` only (`tests/structure_tables.py`, `modules`).
In lodge 0.2 only `gitstore` spawns processes and writes files, and only `gitstore` and `cli` read them (LODGE-5, her decision d-ar0ker; `tests/structure_imports.py:92-98`, `tests/structure_calls.py:109-140`), and the table names `gitstore`, `cli`, `viewer`, and `hook` as the adapters (`tests/structure_tables.py:5-13`); keeping those permissions makes the TypeScript table a renaming of lodge 0.2's, which `CLAUDE.md` ("Structure checks") leaves to the planner, rather than a new edge, which it gives to the author (`plan-review-practice.md`, P-M8).
`gitstore` was both the store and the git user (d-k5swcq); the git work keeps its permissions in `git`, and the store's one new need, SQLite, follows from ARCH-3, her decision that records live in one SQLite file.
Cost if wrong: if the second plan's store needs a file of its own beyond the database, such as a folder to create, that edge goes to the author as a decision.
