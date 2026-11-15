---
id: d-djh40k
kind: decision
title: "knip checks the front doors from the third plan on, unread core names of __all__ marked public"
scope: process
decided_by: planner
date: 2026-11-02T19:16:37+01:00
narrows: [d-s2rdn2]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 11"}
  - {value: "6.42.0", handle: "ts/package.json, devDependencies"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 4"}
---

From the third plan's program task, knip runs with `includeEntryExports`, as d-s2rdn2 says; a name of `#core` that lodge 0.2's `__all__` holds and no file reads is tagged `/** @public */` in its module, and every other export nothing reads is removed.

## Reasoning

d-hshapm has `#core` export every name of `__all__`, and plan 1's front-door test fails without one (plan 1, Task 11), while d-s2rdn2's cost if wrong has such a name "removed then"; the two cannot both hold for a name nothing reads.
knip 6.42.0 does not report an export tagged `@public` (the plan's probe 4: with `LookupError` tagged, `Unused exports (8)` becomes `Unused exports (7)` and `LookupError` is not named).
At `a73a148`, `--include-entry-exports` reports eight unused exports, `LookupError`, `THREADS`, and `attachmentPath` among them (probe 4); `app` and `cli` read some of them by then.
Cost if wrong: a tag left on a name that later gains a reader is harmless, and one line to remove.
