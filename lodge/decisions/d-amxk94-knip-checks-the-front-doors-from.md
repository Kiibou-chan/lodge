---
id: d-amxk94
kind: decision
title: "knip checks the front doors from plan 3 on, names a test or another plan needs marked public"
scope: process
decided_by: planner
date: 2026-11-02T19:42:55+01:00
replaces: [d-djh40k]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 4"}
  - {value: "333", handle: "git show origin/server-store:docs/superpowers/plans/2026-11-02-lodge-server-store.md | sed -n 333p"}
  - {value: "64-76", handle: "git show origin/server-import:docs/superpowers/plans/2026-11-02-lodge-server-import.md | sed -n 64,76p"}
  - {value: "6cc1986", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-1"}
---

From the third plan's program task, knip runs with `includeEntryExports`, as d-s2rdn2 says.
An export nothing reads is removed, unless a front-door test requires it or the fourth plan's table of consumed names lists it; then it is tagged `/** @public */` where it is defined.
The front-door tests require `__all__` of lodge 0.2's `core` and `app`, and the additions `#app`'s `front_door_exports_nothing_else` allows.
An export of a test file that nothing reads loses its `export`.

## Reasoning

d-djh40k exempted only `#core`'s names, but with `includeEntryExports` knip 6.42.0 reports every front door and test files too: at `6cc1986` it named `Command` and `UNREAD` of `src/cli/index.ts` and `EXAMPLE` of `tests/core/thread-files.test.ts` (`docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md`, I-1).
Plan 2's front-door test requires every name of `src/lodge/app/__init__.py`'s `__all__` from `#app` (`docs/superpowers/plans/2026-11-02-lodge-server-store.md`, line 333, on `origin/server-store`), and the fourth plan consumes names of `#app`, `#store`, `#api`, and `#cli` that nothing reads until it builds (`docs/superpowers/plans/2026-11-02-lodge-server-import.md`, lines 64-76, on `origin/server-import`), so removing them would break the one test or the other plan.
knip does not report an export tagged `@public` (probe 4: `Unused exports (8)` became `Unused exports (7)` with `LookupError` tagged).
The fourth plan already assumes the option on from this plan (its Global Constraints, "Exports"), so moving it there would move the work and not the risk.
Cost if wrong: a tag left on a name that later gains a reader is one harmless line, and a name the fourth plan drops stays tagged until someone removes it.
