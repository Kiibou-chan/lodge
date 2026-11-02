---
id: d-hshapm
kind: decision
title: "#core exports Python's names, the default-filling functions, and the stand-ins for Python's library"
scope: process
decided_by: planner
date: 2026-11-02T15:17:30+01:00
narrows: [d-s2rdn2]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "4", handle: "grep -n '### Task 4' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "5", handle: "grep -n '### Task 5a' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "11", handle: "grep -n '### Task 11' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
---

In the first plan `#core` exports every name of `__all__` of `src/lodge/core/__init__.py`, the default-filling function of each dataclass among them, and the names of `errors.ts`, `text.ts`, and `stamps.ts`, and nothing else.
`quoted`, `unreadableChar`, and `LINE_BREAKS_AND_TABS` stay inside the package, as in Python.

## Reasoning

`__all__` holds neither `quoted` nor `unreadable_char`, and no test under `tests/core` imports a name from a module of `lodge.core` other than the package (`grep -rn "from lodge.core\.[a-z_]* import" tests/core` prints nothing), so no carried test needs them through the front door; their readers, `fields.py`, `fileformat.py`, `threads.py`, and `confirmation.py`, are modules of the same package (`plan-recheck-1.md`, N2).
Task 4 can therefore leave them out of `#core` and put `yamlio.ts` in knip's `entry` list until Task 5a reads them (d-tha8st), rather than export them through `#core` and have Task 11 take them out again.
The default-filling functions (`decision`, `specEntry`, `area`, `problem`, and `message`, from the dataclasses with defaults in `src/lodge/core/model.py`) stand in for Python's constructors, which a test reaches through the class name in `__all__`; the carried tests build records with them, so the front door exports them, and Task 11's test allows exactly those, read as the camelCase of a `PascalCase` name of `__all__` defined in `model.ts`.
The names of `errors.ts`, `text.ts`, and `stamps.ts` stand in for Python's standard library, and their tests reach them only through `#core`, since the front-door rule binds tests (d-x6f9za).
Cost if wrong: if a later plan needs `quoted` outside `core`, it adds the name to `#core` and to the test's allowance, one line each.
