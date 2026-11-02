---
id: d-87kzys
kind: decision
title: "Python's whitespace in a pattern is a class text.ts builds"
scope: process
decided_by: planner
date: 2026-11-02T15:17:32+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "001", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 12 (0x1c to 0x1f)"}
  - {value: "0085", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 12 (0x85)"}
  - {value: "12", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 12"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/plan-review-correctness.md, finding M-7"}
  - {value: "4", handle: "grep -n '### Task 4' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "10", handle: "grep -n '### Task 10' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
---

In the first plan `text.ts` exports `PY_SPACE_CLASS`, a character class written as `\u{…}` escapes of the code points `isPySpace` takes, and a pattern with Python's `\s` is built with `new RegExp` around it.

## Reasoning

The one `\s` of the core is in `src/lodge/core/feedback.py:20`, and JavaScript's `\s` differs from Python's at U+001C to U+001F, U+0085, and U+FEFF (probe 12 of `probes.md`), while `text.ts` exported only the predicate `isPySpace`, which a pattern cannot use (`plan-recheck-1.md`, m3).
Writing the class as escapes keeps control characters out of the regular-expression literals Biome checks with `noControlCharactersInRegex` (`plan-review-correctness.md`, M-7), and Task 4's test compares the class with `isPySpace` over every code point, so the class is read in the task that adds it and knip passes.
The other option, Task 10 matching `\s?` by hand around the pattern, would put a second copy of Python's whitespace set in `feedback.ts`.
Cost if wrong: a class that differs from `isPySpace` is caught by Task 4's test before any pattern uses it.
