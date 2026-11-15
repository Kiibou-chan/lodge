---
id: d-hg9qq9
kind: decision
title: "The import changes only the author lines of a thread, every other byte stays"
scope: process
decided_by: coordinator
date: 2026-11-15T03:19:27+01:00
narrows: [d-83kt6y]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "289", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md:289"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Review Focus 2"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Task 5"}
---

Task 5's mapping takes only the `by: author` lines of a thread from the server's writer and leaves every other byte of the file as lodge 0.2 wrote it, so a message of another role keeps its bytes whatever the server's people are called.

## Reasoning

The plan's Task 5 step 2 says the mapped thread is written whole by `writeThread` with the server's people, and its Review Focus 2 and the design say nothing but the author's lines change.
The two conflict on a mixed thread where an owner name or agent role equals another message's `by`: Codex's review probe `role_collision_preserves_every_non_author_line` (`ts/tests/app/importing.test.ts`) showed an unchanged message's `when` rewritten from unquoted to quoted, which is a change to an author-unrelated byte.
Byte preservation governs because the import is a copy, and a copy that rewrites other messages cannot be checked by comparing the files (`docs/superpowers/plans/2026-11-02-lodge-server-import-progress.md`, Task 5 lines).
The failure of the server's writer on the mapped lines is reported at stage `server` with its own sentence, since the source's writer sentence would blame lodge 0.2 for a server refusal.
Cost if wrong: if the server's writer later quotes or orders a field differently from lodge 0.2 for the author's own message, the author's mapped lines differ from a whole-file rewrite by that formatting only, a change confined to the lines that changed anyway; the fix is in `ts/src/app/importing.ts`, one function.
