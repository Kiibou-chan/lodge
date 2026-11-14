---
id: d-wx7d0f
kind: decision
title: "Projects and their members are events behind a Projects port"
scope: process
decided_by: planner
date: 2026-11-02T19:05:41+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 3"}
---

A project and its members are `project` and `member` events, reached through the `Projects` port of `app` (`create`, `members`, `addMember`, and `storeFor`), which the store's `SqliteProjects` implements; one database holds every project, each event naming its own; a project's name matches `^[a-z0-9][a-z0-9-]{0,62}$` and a person's `^[a-z][a-z0-9-]{0,31}$`.

## Reasoning

Everything lodge stores is an event (design, "The model"), and a project has its members and their roles (design, "New objects").
The people of `decided_by` are the project's members (d-kj59bz), so the store must hold them before the API exists.
`api` may import only `app` and `core` (d-k5swcq), so plan 3's `project-create` (d-sry12f) reaches the store through a port.
Both names are written plain in a record header, which quotes a value outside `[A-Za-z0-9][A-Za-z0-9._-]*` (`_PLAIN` in `src/lodge/core/fileformat.py`), and appear in URLs, so lower-case letters, digits, and hyphens need no escaping anywhere.
Cost if wrong: widening a name later is a change of pattern, since no name is ever rewritten.
