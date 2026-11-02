---
id: d-sry12f
kind: decision
title: "The API is JSON operations over HTTP, one per operation of the app"
scope: process
decided_by: planner
date: 2026-11-02T14:10:36+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
  - {value: "0", handle: "uv run --frozen --quiet lodge guide | tail -1"}
  - {value: "1", handle: "uv run --frozen --quiet lodge guide | tail -1"}
  - {value: "2", handle: "uv run --frozen --quiet lodge guide | tail -1"}
---

The API's first shape is `POST /api/v1/<operation>` with a JSON body and a JSON answer, one operation per operation of the app (search, show, waiting, timeline, spec, check, draft, mint, add, ask, reply, close, threads, thread, confirm, behind-area, and the person's approve), agents sending a bearer token and a person a session cookie; an error answers with its kind and one sentence, which the command maps to lodge 0.2's exit codes.

## Reasoning

The design leaves REST or RPC open, "within one API for the interface, the command, and the MCP server" (design, "Left to the builder").
The command's operations are the app's (`src/lodge/app/lodge.py`, `Lodge`), and an MCP server's tools are named operations with JSON inputs, so one operation per call maps onto both with no resource design in between.
`add` takes several drafts at once and `check` returns a verdict, neither a resource a REST route would name.
lodge 0.2's exit codes are 0 done, 1 failed check or conflict, 2 usage or environment (`lodge guide`, last line), so an error kind (usage, not found, conflict, check failed) is what the command needs to keep them.
The version in the path lets the interface and the command change at their own pace later.
Cost if wrong: the operations stay and only their routes change, in `api` and the command's client.
