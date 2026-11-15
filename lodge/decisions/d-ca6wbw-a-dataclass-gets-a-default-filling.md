---
id: d-ca6wbw
kind: decision
title: "A dataclass gets a default-filling function only where a Python call leaves a default out"
scope: process
decided_by: planner
date: 2026-11-02T15:33:35+01:00
narrows: [d-hshapm]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "11", handle: "grep -n '### Task 11' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "3", handle: "grep -n '### Task 3' docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "26", handle: "grep -n '^26\\.' docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md"}
---

In the first plan a frozen dataclass of `core` gets a default-filling function only where a call in `src/lodge` or `tests` leaves a defaulted field out, defined beside its type and exported through `#core` when the type is in `__all__`.
`Draft` and `Snapshot` get none, and Task 11's `front_door_exports_nothing_else` allows `decision`, `specEntry`, `area`, `problem`, `message`, `lengthGuidance`, `coreSettings`, `tree`, and `filters`, besides the stand-ins for Python's library.

## Reasoning

d-hshapm gives "the default-filling function of each dataclass among them", and the plan's test allowed only those of `model.ts`, while the carried tests build `LengthGuidance`, `CoreSettings`, `Tree`, and `Filters` with defaults left out through `lodge.core` (`tests/core/test_settings.py:10`, `tests/core/test_check_threads.py:29` and `:52`, `tests/core/test_apply.py:61`, `tests/core/test_search.py:38`), and a TypeScript test reaches `core` only through `#core`, the `front-door` rule binding tests (the plan's Task 3, `grep -n 'front-door' docs/superpowers/plans/2026-11-02-lodge-server-core.md`); so the test has to allow those four, each defined in the module of its type (`plan-recheck-2.md`, N2-r).
`uv run --frozen python docs/superpowers/plans/2026-11-02-lodge-server-core/probes/fix3/defaults_filled.py .` counts the calls of each core dataclass that leave a defaulted field out, and finds none for `Draft` or `Snapshot`, and some for each of the other nine (`probes.md`, item 26).
`Draft` is built only at `src/lodge/core/drafts.py:45`, with every field, and `Snapshot` only at `src/lodge/core/snapshot.py:70` and `tests/core/builders.py:94`, with every field (`threads` at `builders.py:101`, so the recheck's reading of that call as filling `threads` does not hold).
A `draft` or `snapshot` function would be code nothing calls, which the porting rule refuses ("nothing is added that the Python does not do", Global Constraints, "Porting"), and knip would not catch it, since it leaves a front door's exports alone (Global Constraints, the knip item; `probes.md`, `isAuthor`).
`_Add` of `apply.py` is filled at `src/lodge/core/apply.py:63` but is not in `__all__`, so its function stays inside `apply.ts` and the test never sees it.
Cost if wrong: a later plan that builds a `Draft` or a `Snapshot` with a field left out adds the function, its export, and its name in the test, a line each.
