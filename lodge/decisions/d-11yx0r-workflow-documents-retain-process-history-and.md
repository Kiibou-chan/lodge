---
id: d-11yx0r
kind: decision
title: "Workflow documents retain process history and explicit transitions"
scope: product
decided_by: coordinator
date: 2026-11-15T05:12:23+01:00
changes:
  - {entry: s-c0k9hx, action: create}
  - {entry: s-xqza9k, action: create}
  - {entry: s-hmj4mc, action: create}
  - {entry: s-krdpxq, action: create}
  - {entry: s-68mfam, action: create}
  - {entry: s-an745k, action: create}
  - {entry: s-pttahq, action: create}
  - {entry: s-h48a8n, action: create}
  - {entry: s-0tn1e8, action: create}
  - {entry: s-hke5m9, action: create}
  - {entry: s-73ee5k, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:21-25, 98, 111, 175"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 5"}
  - {value: "third", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:111"}
---

Project workflow documents describe actors, transitions, session starts, execution locations, artefacts, failure routes, and reporting checklists.

## Reasoning

Workflow as data, lines 98 to 170, keeps adaptable process history and makes progression inspectable. The default plan and task kinds, event history of changes, and named failure back-edges are [my call], as explicitly marked at lines 98 and 106. The remaining fields and default process are approved by d-5ps72w; d-8kasej settles workflows on the server. Findings drive thresholds rather than an opaque verdict, and a session-driven review remains reported to preserve the claim/check boundary. The exact syntax remains open at line 168; these entries specify content, not a new syntax. Build order assigns workflow as data to step 5. s-tprwhs and s-azfcx4 already define workflow and step occupancy; s-h4x7bx already defines the parent waiting for children.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
