---
id: d-vd3175
kind: decision
title: "A defaulted Python parameter becomes a field of one trailing options object"
scope: process
decided_by: planner
date: 2026-11-02T19:05:30+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 3"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, the plan's own number"}
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'Task 11: Applying drafts'"}
---

In `app`, a Python method's parameters without a default stay positional, and those with a default become one trailing options object with their names in camelCase, so `add(drafts, dry_run=True)` becomes `add(drafts, { dryRun: true })`.

## Reasoning

The carried tests call the operations with keywords (`add(drafts, dry_run=True, attachments=[LOG])` in `tests/app/test_writes_attach.py`); positional TypeScript would need `undefined` placeholders, and a parameter added later would shift every value after it without a type error where the types agree.
An options object has the shape of the API's JSON body, one per operation (d-sry12f), so plan 3 maps a request to a call field by field.
Plan 1 kept the core's functions positional (`applyDrafts`, Task 11 of `docs/superpowers/plans/2026-11-02-lodge-server-core.md`), whose callers pass every argument, so this rule binds `app` only.
Cost if wrong: the call sites in `app`, its tests, and plan 3's handlers are renamed.
