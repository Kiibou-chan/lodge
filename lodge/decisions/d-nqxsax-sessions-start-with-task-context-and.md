---
id: d-nqxsax
kind: decision
title: "Sessions start with task context and report through lodge"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:19+01:00
changes:
  - {entry: s-nj99c5, action: create}
  - {entry: s-r2k5t2, action: create}
  - {entry: s-7zx39z, action: create}
  - {entry: s-awkdkw, action: create}
  - {entry: s-dazqbj, action: create}
  - {entry: s-myvb3j, action: create}
  - {entry: s-xe5bmq, action: create}
  - {entry: s-anc255, action: create}
  - {entry: s-25m983, action: create}
  - {entry: s-vg9y38, action: create}
  - {entry: s-68vtrb, action: create}
  - {entry: s-n242p0, action: create}
  - {entry: s-a62w0p, action: create}
  - {entry: s-c0zke5, action: create}
  - {entry: s-a2y9t3, action: create}
  - {entry: s-zjdzre, action: create}
  - {entry: s-p6n0x6, action: create}
  - {entry: s-pammwd, action: create}
  - {entry: s-n4pdfq, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:178-216, Build order and section content"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
---

Sessions start with task context and report through lodge.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:178-216.
A runner uses its registering person's subscription for that person's assigned tasks, avoiding serving another person's requests.
The brief reconstructs task context rather than chat summaries.
d-wc9wt2 settles Talking inside lodge, without a build step assigned to that claim.
WebSocket transport, cloud stop hooks, automatic reporting hooks, and tokenless mailbox authority are [my call] choices.
Cloud transcript access is unverified, so usage can be unknown.
The MCP exclusion follows the network-secret boundary described at design line 213.

No other looks-related decision is replaced or narrowed.
