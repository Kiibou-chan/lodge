---
id: d-va3j7x
kind: decision
title: "The hook advises on every file under lodge/ of a moved project, its paths resolved by git"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "290", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:290"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
---

A project has moved when its `.lodge.toml` names its server; then the hook gives every file under `lodge/` but the attachments the advice to change records through the command, which talks to the server, whatever the store's mode, and a frozen file the same advice naming the server.
The hook reads no file itself: the composition root gives it the context and the resolution of paths from `git`.

## Reasoning

The hook's advice changes from "use `lodge add`" to "use the server" for a project that has moved (design line 290).
After a move the files under `lodge/` in a project's checkout are copies from before it, in either 0.2 mode, and an edit there changes nothing on the server, so each of them gets the advice.
`hook` keeps the permissions of lodge 0.2's hook (d-x6f9za), which reads no file; its `Path.resolve` follows links (`src/lodge/hook/post_tool_use.py:68`), which in TypeScript needs `node:fs`, refused outside `git` and `cli` (plan 1, Task 3, `file-confinement`), so `git` resolves and the composition root passes the function in, as lodge 0.2's `main` passes the context (`src/lodge/main.py:73-86`).
Cost if wrong: the advice texts change, or a narrower set of files gets them, each a change to `texts.ts` and its tests.
