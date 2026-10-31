---
id: d-cg3nn3
kind: decision
title: "lodge's non-goals for now: no server, no MCP server, limited scope, soft limits, read-only viewer"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:15+01:00
changes:
  - {entry: s-07ar34, action: create}
  - {entry: s-7ah5n7, action: create}
  - {entry: s-rger6n, action: create}
  - {entry: s-582qav, action: create}
---

For now lodge has no server and no MCP server, leaves out other kinds of knowledge and projects, keeps length limits soft, and has a read-only viewer.

## Reasoning

Each non-goal has a reason in the specification.

No server for now: the author's decision on a serverless start is d-rkcb17. A shared server later, storage behind one interface, and Kotlin as a candidate language then are the design document's non-goals (`docs/superpowers/specs/2026-10-29-lodge-design.md:43`).

No MCP server: the author's decision is d-14vk9b.

Other kinds of project knowledge are left out until they have been evaluated, first on the past and then in a pilot.

The author's personal to-do list is left out for now, and may be integrated later.

Conversation logs are left out as provenance; the author's words on accessible provenance are in d-pf8xm9.

Length limits stay soft; the author's words on guardrails are in d-c6n1ng.

Making the viewer read-only was the specification author's call, taken from the project whose viewer served as the model: the author's decisions reach lodge through a session, quoted, as they reach the first user's files today.

Porting a second project is left out, and whether a second project adopts lodge later stays open (s-hh97bm).
