---
id: d-tnpe08
kind: decision
title: "Export to git is a one-way copy of server records"
scope: product
decided_by: coordinator
date: 2026-11-15T04:46:23+01:00
changes:
  - {entry: s-f6eaj1, action: create}
  - {entry: s-20dnpp, action: create}
  - {entry: s-b4dtqk, action: create}
  - {entry: s-b6jxhr, action: create}
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 2"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 3"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 4"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 5"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 6"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 7"}
  - {value: "300", handle: "ts/tests/structure/, module-size rule"}
  - {value: "0.2", handle: "pyproject.toml, project.version"}
  - {value: "3.12", handle: "pyproject.toml, project.requires-python"}
  - {value: "1.3.14", handle: "ts/package.json, packageManager"}
---

The server exports its records to a dedicated git branch in the project's repository or a separate repository.
The export preserves the server's named people and batches writes within each server run.

## Reasoning

d-khew4n settles one-way export and a separate repository; d-b61590 settles named people with no requirement for lodge 0.2 to read the result cleanly.
The design marks the exported object boundary and batching as [my call].
d-pv341r protects code and checked-out work trees by requiring a branch holding only lodge files, a temporary index, and no force push.
d-sj6hmf and d-j5s0h0 supply batching, retries, startup flushing, all project files, and event-backed targets; the implementation bounds batching within one run rather than persisting the last commit time across restarts.
The source of truth remains the events; an export is never an alternate input to the database.
No: d-khew4n is the author's export ruling and remains untouched; d-sk1r7r defines the event source of truth that this copy depends on; d-sj6hmf supplies the batching that these entries describe.
None is replaced or narrowed.
