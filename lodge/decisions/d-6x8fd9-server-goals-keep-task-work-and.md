---
id: d-6x8fd9
kind: decision
title: "Server goals keep task work and context together"
scope: product
decided_by: coordinator
date: 2026-11-15T05:11:49+01:00
changes:
  - {entry: s-k570d9, action: create}
  - {entry: s-ts73yt, action: create}
  - {entry: s-wgkrmr, action: create}
  - {entry: s-gyamm5, action: create}
  - {entry: s-fpxzb9, action: create}
  - {entry: s-81kf9s, action: create}
  - {entry: s-5tgnrn, action: create}
  - {entry: s-cg69z0, action: create}
  - {entry: s-6r0exg, action: create}
  - {entry: s-7ah5n7, action: edit}
  - {entry: s-c8hrye, action: edit}
narrows: [d-cg3nn3, d-3d4g9j]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "0.2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:6, 71; lodge 0.2 exclusions retained"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 2"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 3"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 4"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 5"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:21-25, 98, 111, 175"}
---

The server makes task state, context, durable outputs, and collaboration explicit while preserving record meanings.

## Reasoning

Goals, lines 21 to 30, keep context local, preserve outputs beyond sessions, and make work actionable without asking a session. d-ffk7wy settles the installable phone interface; d-wc9wt2 settles talking to lodge-started sessions inside lodge; d-8kasej settles the server and runners; d-5ps72w approves these goals. No goal is marked [my call]. s-31atpc already states the preserved record meanings of line 29, so it is linked rather than repeated. Narrow d-cg3nn3 only for the universal exclusion of phone use and task knowledge, and d-3d4g9j only for the universal exclusion of live sessions: their lodge 0.2 exclusions and viewer safeguards remain. No author decision is narrowed. The coordinator approves these scoped edits and the step mapping; unassigned own-thread claims have no guessed build step.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
