---
id: d-bh93bn
kind: decision
title: "The importer maps only decided_by, through the writer, and keeps thread messages"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "78", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:78"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1'"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 4's paragraph"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "354", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md, the Task 5a review line"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core-progress.md, the Task 5a review line"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 6"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 2's paragraph"}
---

The importer rewrites a decision whose `decided_by` is `author` through the record writer with the first owner in its place, and refuses a decision whose file the writer would not give back byte for byte; a thread message keeps `by: author`.

## Reasoning

Design line 78 maps `decided_by` and names nothing else, and this plan's end is a store that survives import and export "unchanged apart from the people in `decided_by`" (plan 1, "The rest of build step 1", plan 4's paragraph).
Going through the writer quotes the person's name as every other value is quoted, and requiring the untouched decision to read back byte for byte makes the mapped file differ in that one line; the TypeScript writer gives lodge 0.2's text byte for byte on all 354 records under `lodge/` (plan 1's ledger, Task 5a review).
lodge 0.2 writes an author's thread message as `by: author` with `where` and `when` (probe 6 of the plan's `probes.md`), and how a thread names a person on the server is plan 2's model, which plan 1's paragraph names for `decided_by` only.
Cost if wrong: a later import maps thread messages too; no project has moved (d-2jk0mw), so nothing imported needs changing.
