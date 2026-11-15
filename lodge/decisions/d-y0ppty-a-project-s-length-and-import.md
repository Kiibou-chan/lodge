---
id: d-y0ppty
kind: decision
title: "A project's length and import settings live on the server, given by lodge init"
scope: process
decided_by: planner
date: 2026-11-02T19:16:26+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "79", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, line 79"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
---

A project's `[length]` and `[import]` settings live on the server, given once by `lodge init` from `.lodge.toml`, checked there, and kept in the body of plan 2's `project` event; changing them later is outside build step 1, and the guide says so.

## Reasoning

The check runs on every write on the server (design line 79), and the import sources are part of it: a record imported from a source the settings do not list fails it (`tests/e2e/test_add_import.py`, `test_import_from_an_unlisted_source_fails_the_check`).
Settings sent with each request would let two clients give one state two verdicts, and an agent widen the sources by sending its own; lodge 0.2 reads them from the checkout on each command (`src/lodge/main.py:49-53`), where they are reviewed with the code, and on the server the server's copy is the one place.
No carried command test changes the settings after the store exists: each `configure` in `tests/e2e` comes before `initialise`, `seed`, or `init` (`grep -n configure tests/e2e/*.py`), the branch-mode ones aside, which the server does not have.
Keeping them in the `project` event (d-wx7d0f) lands a project and its settings in one transaction, so no project exists without them.
Cost if wrong: a person who edits `[length]` after `init` sees no change until an operation to change settings exists, one operation and one command.
