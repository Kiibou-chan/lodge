---
id: d-4wrzdf
kind: decision
title: "People join by invitation and sessions have scoped credentials"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:16+01:00
changes:
  - {entry: s-sezq1z, action: create}
  - {entry: s-x7sw4r, action: create}
  - {entry: s-pjnxhg, action: create}
  - {entry: s-t7wqxn, action: create}
  - {entry: s-bk3f8p, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
---

People join by invitation and sessions have scoped credentials.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:258-263.
Passkeys already live in s-c0bd0b, with the library choice in d-yayhct.
The owner/member role split is [my call].
Local session tokens differ from the shared environment token of cloud sessions; machine registration issues a runner credential.

No other looks-related decision is replaced or narrowed.
