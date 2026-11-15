---
id: d-ktz4rj
kind: decision
title: "Server scope leaves optional product extensions for later"
scope: product
decided_by: coordinator
date: 2026-11-15T05:11:57+01:00
changes:
  - {entry: s-6z04mq, action: create}
  - {entry: s-gdtksn, action: create}
  - {entry: s-chycjf, action: create}
  - {entry: s-tjq0rm, action: create}
  - {entry: s-gyyt5k, action: create}
  - {entry: s-4gjz9j, action: create}
  - {entry: s-nhx8zw, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "second", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:37"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 3"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order, item 6"}
---

The server leaves optional editing, comparison, desktop, infrastructure, and hosting extensions outside its present scope.

## Reasoning

Non-goals, lines 34 to 40, defer a code editor, require project-specific app starting before visual comparison, and require a desktop shell to justify itself by running the local server. d-d3js00 settles SQLite and d-ffk7wy settles the installable browser app. The design cites subscription billing and environment eligibility as reasons for excluding Managed Agents and self-hosted cloud environments, not as newly verified service promises. GitLab follows project need. No claim here is marked [my call]; d-5ps72w approves the scope.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
