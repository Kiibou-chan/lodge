---
id: d-2jk0mw
kind: decision
title: "No project moves to the server during build step 1"
scope: process
decided_by: planner
date: 2026-11-02T14:10:40+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1", handle: "design, Build order, item 1"}
  - {value: "2", handle: "SRV-2, design, The model"}
  - {value: "3", handle: "design, Build order, item 3"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
---

No project, lodge included, moves its records to the server during build step 1; the importer and the export are tested on made-up stores, and on a scratch copy of lodge's own records by the coordinator, never on the live store.

## Reasoning

After a move a person's decision becomes current only when that person approves it (SRV-2; design, "The model"), and how she approves one in the interface is open for later (design, "Open"); the interface comes in step 3 (design, "Build order").
Until then a moved project could not take her decisions, and she would lose the viewer's confirming, which she asked for (d-dyrpc6).
lodge 0.2 stays usable until a project has moved (design, "Moving from lodge 0.2"), so nothing waits on a move.
Cost if wrong: the first move waits for step 3, while lodge 0.2 keeps working.
