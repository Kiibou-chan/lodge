---
id: d-s5s2c3
kind: decision
title: "fetch is allowed in api, cli, and hook, and refused in the other packages"
scope: process
decided_by: coordinator
date: 2026-11-02T17:24:03+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-3-review.md"}
  - {value: "0.2", handle: "pyproject.toml, version"}
---

The call rules report `fetch` and `new WebSocket` in `store` and `git` as `sockets outside api`; `api`, `cli`, and `hook` may call them, and `core` and `app` stay under their own ban.

## Reasoning

The review found `fetch` unreported outside `api` (`task-3-review.md`, m1).
The command talks to the server over HTTP (plan 3, "the `lodge` command at parity with lodge 0.2, talking to the server"), and a session reports through a hook (design, "Reporting"), so `cli` and `hook` need `fetch`; `store` and `git` have no reason to reach the network.
Cost if wrong: a later adapter that needs the network gets an allowed edge, a one-line change to the rule and its tests.
