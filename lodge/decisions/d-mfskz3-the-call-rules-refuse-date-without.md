---
id: d-mfskz3
kind: decision
title: "The call rules refuse Date without new and every file-writing form outside git"
scope: process
decided_by: coordinator
date: 2026-11-02T17:24:03+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-3-review.md"}
  - {value: "471", handle: "git rev-parse --short 471b8ca"}
  - {value: "0.2", handle: "pyproject.toml, version"}
---

In `core` and `app`, every call of `Date` without `new` is refused whatever its arguments, and only `new Date(x)` with one argument passes in `app`.
Outside `git`, every form that writes a file is refused: `createWriteStream`, `write`, `writev`, `link`, `mkdtemp` and their `Sync` forms, `open` whose flags are absent, not a literal, or hold `w`, `a`, or `+`, and `write`, `writer`, or `delete` on a `Bun.file(…)`.

## Reasoning

The plan's list in Task 3 names `new Date()` and `Date()` by argument count, but `Date("x")` without `new` ignores its argument and returns the current time (`task-3-review.md`, I4, run on 471b8ca: `callViolations` gives `[]`), so the list lets the clock into `app`, which the design and LODGE-5 forbid.
The plan's list of writing calls omits forms lodge 0.2 refuses (`tests/structure_calls.py:331-371`, `_open_mode`), and d-x6f9za keeps each adapter at its 0.2 permissions, so `cli` may read drafts but not write (`task-3-review.md`, I5, run on 471b8ca).
The rule wins over the list that was meant to carry it.
Cost if wrong: an adapter that later needs to write a file outside `git` needs an allowed edge, which is the author's call recorded as a decision; one extra rule to relax.
