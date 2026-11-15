---
id: d-d816nz
kind: decision
title: "Task artefacts persist and have their own conversations"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:22+01:00
changes:
  - {entry: s-kagv3e, action: create}
  - {entry: s-m7w8c0, action: create}
  - {entry: s-bd0qv5, action: create}
  - {entry: s-xakcm0, action: create}
  - {entry: s-er4t45, action: create}
  - {entry: s-z0zk7y, action: create}
  - {entry: s-gwppsf, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:218-225, Build order and section content"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
---

Task artefacts persist and have their own conversations.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:218-225.
Task ownership prevents session loss from losing work.
Separate threads keep mock discussion apart from coordination, and retained mocks explain later decisions.
Sandboxed HTML and restricted sharing are [my call] choices because mocks contain scripts and outsiders must see only the shared artefact.

No other looks-related decision is replaced or narrowed.
