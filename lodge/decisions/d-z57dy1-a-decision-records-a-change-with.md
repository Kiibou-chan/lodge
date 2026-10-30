---
id: d-z57dy1
kind: decision
title: "A decision records a change, with fields for who, what, and the evidence"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:17+01:00
changes:
  - {entry: s-s3z6ea, action: create}
  - {entry: s-aq3a5k, action: create}
  - {entry: s-0yzshh, action: create}
  - {entry: s-f859z1, action: create}
  - {entry: s-fmwe04, action: create}
numbers:
  - {value: "2011", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:93"}
---

A decision records a change, close to an architecture decision record, with a scope, who decided, the entries it changes, and the decisions it replaces or narrows. Its status, current or replaced, is derived.

## Reasoning

The decision follows the architecture decision record (Nygard 2011), with a title and statement at Level 1 and the reasoning as the body.

Scope is one field on one record kind, which was agreed, so the first user's decisions and rulings become one kind; a process ruling is a decision with scope `process` and nothing else distinguishes it.

Number handles exist so that every number a decision states can be traced to a record and key or a runnable command.

Attachments hold expanded evidence such as logs where it matters for evaluation, outside the default read path so that it costs nothing to ordinary reads.

`imported_from` records where a converted record came from, which the importer needs.

A replaced decision's file does not change and does not move: a stored status or an archive folder would be a second copy of what the links already say, and would mean editing an immutable record.

Reads and the viewer therefore show current records by default and the rest by filter, and a narrowed decision stays current.
