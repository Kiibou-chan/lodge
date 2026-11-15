---
id: d-rgta90
kind: decision
title: "The browser interface shares the API and presents task views"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:39+01:00
changes:
  - {entry: s-ksg593, action: create}
  - {entry: s-w46592, action: create}
  - {entry: s-8ysrep, action: create}
  - {entry: s-bnnw4m, action: create}
  - {entry: s-5wysdb, action: create}
  - {entry: s-7pfk9d, action: create}
  - {entry: s-y019g9, action: create}
  - {entry: s-fns8m3, action: create}
  - {entry: s-3xkj85, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:265-278, Build order and section content"}
---

The browser interface shares the API and presents task views.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:265-278.
d-ffk7wy settles the browser app, Preact, signals, and phone installation.
Existing s-wrksm5, s-t4tbrj, s-bxws89, and s-h1e6jc hold installation, phone answers, board, and task-page content.
Server-sent events are [my call].
Diff reading at length is the practical exception on a phone.

No other looks-related decision is replaced or narrowed.
