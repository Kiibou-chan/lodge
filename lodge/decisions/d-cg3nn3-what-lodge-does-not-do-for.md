---
id: d-cg3nn3
kind: decision
title: "What lodge does not do for now is recorded as specification entries"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:15+01:00
changes:
  - {entry: s-07ar34, action: create}
  - {entry: s-7ah5n7, action: create}
  - {entry: s-rger6n, action: create}
  - {entry: s-582qav, action: create}
---

The non-goals are specification entries: no server and no MCP server, a limited scope, soft length guidance, and a read-only viewer.

## Reasoning

Each non-goal has a reason in the specification.

A server is left out because a serverless prototype is reasonable first; a shared server is the later ideal and might be worth a little money, so storage sits behind one interface a server can replace, and Kotlin, which the author prefers, is a candidate then.

An MCP server is left out because the author does not think she can install additional MCP servers in cloud environments, so a command-line tool run through Bash is the route.

Other kinds of project knowledge are left out until they have been evaluated, first on the past and then in a pilot.

Her personal to-do list is left out for now, with the possibility of integration later in whatever way makes sense.

Conversation logs are left out as provenance; the specification notes elsewhere that cloud transcripts are not always accessible.

The author doubts that hard character limits would serve writers well, and expects guardrails alone to help.

Making the viewer read-only was the specification author's call, taken from the project whose viewer served as the model: the author's decisions reach lodge through a session, quoted, as they reach the first user's files today.

Porting a second project is left out, and whether a second project adopts lodge later stays open.
