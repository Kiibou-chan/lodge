---
id: d-s6mq0f
kind: decision
title: "lodge ships a hook that gives feedback on hand edits"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:21+01:00
changes:
  - {entry: s-4nq741, action: create}
  - {entry: s-h12s8w, action: create}
---

lodge ships a hook command for a project's Claude Code settings that gives feedback, without blocking, after a hand edit of a record file or of a file lodge has replaced. The pilot counts how often it fires.

## Reasoning

The hook serves the success measure the author called very important, that agents use lodge and no decision is written anywhere else.

It was the specification author's call to ship it, modelled on the author's hook on auto-loaded files.

It gives feedback and does not block, consistent with the guardrail style that was settled, and the pilot counts the occasions it fires so that the measure has data.
