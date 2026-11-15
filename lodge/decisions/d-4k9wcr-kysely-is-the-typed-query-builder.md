---
id: d-4k9wcr
kind: decision
title: "Kysely is the typed query builder"
scope: process
decided_by: planner
date: 2026-11-02T14:10:42+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.29.7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 11"}
  - {value: "3", handle: "ARCH-3, docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md"}
  - {value: "15", handle: "wc -l probes/src/server/db.ts, the adapter in open()"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 1"}
  - {value: "40-52", handle: "node_modules/kysely/dist/dialect/sqlite/sqlite-dialect-config.d.ts:40-52, after bun install"}
---

The storage adapter queries SQLite through Kysely (0.29.7 here), over `bun:sqlite` through an adapter to Kysely's `SqliteDatabase` interface.

## Reasoning

The design asks for a typed query builder that also speaks Postgres and leaves Drizzle or Kysely to the builder (design, "Constraints" and "Left to the builder"; ARCH-3).
Kysely is a query builder only: its schema is a TypeScript interface and its migrations are code, so it adds no schema tool or generated files to the gate, where Drizzle's migrations come from drizzle-kit.
Its SQLite dialect takes any object with `prepare` and `close` (`SqliteDatabase`, `kysely/dist/dialect/sqlite/sqlite-dialect-config.d.ts:40-52`), and a 15-line adapter over `bun:sqlite` passed an insert and a select (probe 1); a Postgres dialect ships with it.
Cost if wrong: the queries of one adapter package rewritten, behind the storage port.
