---
id: d-94tynf
kind: decision
title: "Codex builds without a sandbox and commits its own build branch"
scope: process
decided_by: author
date: 2026-11-14T20:30:06+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
quote: {text: "A", where: "lodge build session", when: "2026-11-14T20:29:23+01:00"}
numbers:
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"}
---

From plan 2 to plan 4, Codex runs with full access and no sandbox, commits, and pushes its own build branch; a pre-push hook refuses `main`; the coordinating session still reviews every task before its branch merges.

## Reasoning

Asked as CODEX-1 in the lodge build session; the author answered "A".
Until now Codex ran in its workspace-write sandbox with no network and no sockets, and the coordinating session ran the gate, committed, and pushed.
Plan 3's tests serve the API with `Bun.serve` on `127.0.0.1` (`docs/superpowers/plans/2026-11-02-lodge-server-api.md:539`), which the sandbox refuses, so the coordinating session would have run every server test on Codex's behalf.
The same setup already holds for gloss, where the author ruled that the sandbox is for evaluations only.
Cost if wrong: a Codex commit the gate would have refused lands on a build branch, where the task review catches it and a fix round reverts it; `main` stays out of reach through the hook.
