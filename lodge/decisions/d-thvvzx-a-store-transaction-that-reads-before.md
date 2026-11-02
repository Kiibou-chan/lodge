---
id: d-thvvzx
kind: decision
title: "A store transaction that reads before it writes opens with a write, and a hold settles once"
scope: process
decided_by: planner
date: 2026-11-02T19:36:03+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 4"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 8"}
  - {value: "409", handle: "git show origin/server-api:docs/superpowers/plans/2026-11-02-lodge-server-api.md | sed -n 360p"}
---

Every SQLite store transaction that reads before it writes opens with a write on the project's `heads` row: in `create` an insert doing nothing on an existing name, in `addMember`, `decline`, and an approving `publish` an update keeping the revision; inside it, an approving `publish` answers `REJECTED` and `decline` throws `NotFound` unless the hold is open, and `applyEvent` throws on approving or declining a hold that is not open.

## Reasoning

A deferred transaction that reads, lets another connection commit, and then writes fails with `database is locked`, while one whose first statement is a write fails nothing (probe 4 of `docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md`), so a racing `create` answers `Conflict`, which plan 3 maps to 409, instead of an untyped SQLite error (correctness review M-8).
`approve` reads the holds and the tree in two reads, and the compare-and-set protects only what the tree's revision covers, so a decline, or a second approval, landing between them let both land (correctness review I-1); checking the hold's state inside the transaction that writes closes it whatever the order of the reads, and `applyEvent`'s refusal keeps `rebuild` from replaying a history the store could not have written.
An update that leaves the revision as it is still tells a project that exists from one that does not (probe 8).
Cost if wrong: an approval that loses the race answers `NotFound` after its check ran, and the person approves nothing twice.
