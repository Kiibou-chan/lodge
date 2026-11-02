---
id: d-83kt6y
kind: decision
title: "The importer maps decided_by and thread messages by author to the owner, through the writers"
scope: process
decided_by: planner
date: 2026-11-02T19:07:50+01:00
replaces: [d-bh93bn]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "78", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:78"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, Task 10"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, Task 10"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 7"}
  - {value: "354", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md, the Task 5a review line"}
  - {value: "1,207", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md, the Task 6 review line"}
---

The importer rewrites each decision whose `decided_by` is `author`, and each thread message whose `by` is `author`, with the project's owner in its place, through the record writer and the thread writer; a file that its writer would not give back byte for byte unchanged is refused, so nothing else in it changes.

## Reasoning

Design line 78 maps the author to the project's first owner.
Plan 2's core reads a thread message as a person's only when its `by` is one of the project's people, a person's `when` being a minute and an agent's a stamp (plan 2, Task 10), so an author's message left as `by: author` has a minute where a stamp is required and fails the server's check, as lodge 0.2 fails the mirror case (probe 7 of the plan's `probes.md`); the thread messages are therefore mapped too, which d-bh93bn left out.
The writers give lodge 0.2's text byte for byte on 354 records and 1,207 threads (plan 1's ledger, the Task 5a and Task 6 reviews), so requiring the untouched file to come back unchanged makes the mapped file differ only in the mapped lines.
Cost if wrong: if plan 2's model changes how a thread names a person, this mapping follows it; no project has moved (d-2jk0mw), so nothing imported needs changing.
