---
id: d-gxbbnf
kind: decision
title: "An event's commit message is stored as bytes through the same codec as a file"
scope: process
decided_by: coordinator
date: 2026-11-14T21:56:37+01:00
narrows: [d-wje1cn]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/task-7b-review.md, title (Task 7b)"}
  - {value: "1", handle: "task-7b-review.md, finding C-1 and the table's `U+FEFF`/`d-1` rows"}
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "3", handle: "plans 3 and 4 of docs/superpowers/plans/2026-11-02-lodge-server-store.md, line 190 onward"}
  - {value: "4", handle: "plans 3 and 4 of docs/superpowers/plans/2026-11-02-lodge-server-store.md, line 190 onward"}
---

The `events` table's `message` column is a `blob` holding the commit message through `encodeUtf8` of the core's `text.ts`, read back through `decodeUtf8`; the `Store` port keeps `message: string`.

## Reasoning

The Task 7b review (`docs/superpowers/plans/2026-11-02-lodge-server-store/task-7b-review.md`, C-1) ran `store.publish` with message `"t\uDC80 tail"` and read `"t\u{30020}tail"` back, with `"lodge: add d-1 t\uDC80"` giving `""` and a leading U+FEFF dropped.
`Lodge.add` builds the message from a record's title (`ts/src/app/writes.ts:224-229`), and a title may hold U+DC80 to U+DCFF, which `encodeUtf8` accepts for the file itself, so the title and the file would round-trip differently.
Events are append-only, so a corrupted message can never be corrected.
d-wje1cn weighed the `text` corruption for file text only; the message column was not considered.
Refusing such a message in `publish` would fail an `add` that lodge 0.2 commits.
No database exists yet, so `MIGRATIONS[0]` changes in place; plans 3 and 4 read the message through the `Store` port, not the column.
Cost if wrong: a later migration to `text` loses the bytes of any message holding an escaped byte.
