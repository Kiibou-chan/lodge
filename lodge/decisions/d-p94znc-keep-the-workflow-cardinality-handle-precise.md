---
id: d-p94znc
kind: decision
title: "Keep the workflow cardinality handle precise"
scope: product
decided_by: coordinator
date: 2026-11-15T05:27:39+01:00
changes:
  - {entry: s-c0k9hx, action: edit}
narrows: [d-tx7e0m]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:98, one workflow per kind of task"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, Build order, item 5"}
---

A project has a workflow per task kind, retaining the recorded workflow statement and its precise cardinality evidence.

## Reasoning

The one-workflow claim in s-c0k9hx still holds unchanged against design line 98.
The number handle in d-tx7e0m correctly cites line 98 but also mistakenly calls line 109 a waiting-list claim; line 109 instead describes review findings.
Narrow that decision only for this extraneous citation, using line 98 alone for workflow cardinality.
The [my call] designation and existing workflow dependency remain.
No author decision or other related decision is narrowed or replaced; looks-related feedback is answered no.
