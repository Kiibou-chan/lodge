---
id: d-vsspgk
kind: decision
title: "Separate independent workflow fields for lookup"
scope: product
decided_by: coordinator
date: 2026-11-15T05:14:15+01:00
changes:
  - {entry: s-xqza9k, action: edit}
  - {entry: s-hmj4mc, action: edit}
  - {entry: s-3ysqhz, action: create}
  - {entry: s-mrnqdh, action: create}
narrows: [d-11yx0r]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, Build order, item 5"}
---

Workflow actors, progression conditions, session-start modes, and execution locations each have their own specification entry.

## Reasoning

Workflow as data lists these as independent fields, so each needs its own lookup entry under the plan's claim-per-entry rule.
The coordinator approves this corrective split before the task commits; d-11yx0r is narrowed only for its combined entry groupings, with no change to the workflow contract.
The existing actor and start-mode IDs retain their meanings, while progression and location gain separate entries; all still rest on s-tprwhs.
None of these fields is marked [my call]; d-5ps72w approves the design and no author decision is narrowed.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
