---
id: d-m31e0d
kind: decision
title: "Stored bytes decode in text.ts, and the importer refuses an attachment that is not UTF-8"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "8", handle: "src/lodge/gitstore/trees.py:16, the codec name"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 1"}
  - {value: "40", handle: "wc -l docs/superpowers/plans/2026-11-02-lodge-server-import/probes/decode.ts"}
  - {value: "20,020", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 1"}
  - {value: "19,004", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 1"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 2"}
---

`decodeStored` and `encodeStored` of `text.ts` read and write bytes as Python's `surrogateescape` does (d-0q54zn); the importer refuses an attachment that is not UTF-8 with lodge 0.2's message for `--attach`, and a record that is not UTF-8 is problem 1, which refuses the import.

## Reasoning

`contentHash` in `core` must encode the escapes back (d-0q54zn), and `text.ts` holds Python's string semantics and may add names to `#core` (d-hshapm), so both directions sit there, beside each other.
A 40-line decoder agrees with Python's `surrogateescape` on 20,020 byte strings, where `TextDecoder` differs on 19,004 (probe 1 of the plan's `probes.md`).
A lone surrogate stored in `bun:sqlite` reads back as another character (probe 2), so no escaped byte may reach the events store; a record holding one fails lodge 0.2's check as problem 1 and so refuses the import before anything is written, and an attachment is refused as lodge 0.2 refuses one, "not UTF-8 text; attachments are text in this version" (`src/lodge/cli/commands.py:121`).
Cost if wrong: a store with a binary attachment cannot move until attachments may hold bytes, which the events store would then need as its own column.
