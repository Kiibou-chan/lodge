---
id: d-ryss91
kind: decision
title: "The importer reads stored bytes through plan 2's codec and refuses no file for its bytes"
scope: process
decided_by: planner
date: 2026-11-02T19:07:50+01:00
replaces: [d-m31e0d]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, Task 7"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, Task 7"}
  - {value: "1", handle: "src/lodge/core/snapshot.py, load"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
---

The importer decodes every file it reads from git, attachments included, with `decodeUtf8` of `core/text.ts`, which plan 2's Task 7 builds for d-0q54zn, and refuses no file for its bytes: an attachment that is not UTF-8 round-trips byte for byte, and a record that is not UTF-8 is problem 1, which refuses the import.

## Reasoning

Plan 2 takes d-0q54zn (plan 2, Task 7: `encodeUtf8` and `decodeUtf8` in `text.ts`, `contentHash` through `encodeUtf8`) and keeps each file's bytes in a `blob` through those two functions, so an escaped byte reaches the events store and comes back as the byte; d-m31e0d's codec of its own and its refusal of a non-UTF-8 attachment rested on a `text` column, which plan 2 does not use.
lodge 0.2's `load` reports a record with an undecodable byte as problem 1 (`src/lodge/core/snapshot.py`, `load`), and the import refuses a store its check refuses (d-ag8p8h).
Cost if wrong: none for a store lodge 0.2 wrote, whose attachments are text (`src/lodge/cli/commands.py:121`).
