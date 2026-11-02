---
id: d-n9nm8h
kind: decision
title: "The import checks a store as a change from an empty state"
scope: process
decided_by: coordinator
date: 2026-11-02T19:54:57+01:00
narrows: [d-j28rp0]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "pyproject.toml, version"}
---

Where d-j28rp0 says the import runs lodge 0.2's state check on the store it imports, the import instead runs the change check from an empty state with the store's settings and then with the project's (plan 4's d-sdpcyb); the store's refusals are unchanged.

## Reasoning

Plan 4's correctness review found that the state check passes a store whose sources or title lengths break its settings, since those checks judge only new decisions inside the change check (`plan-review-correctness.md` B-1 in `docs/superpowers/plans/2026-11-02-lodge-server-import/` on `server-import`), and plan 4's fix round replaced its import check accordingly (d-sdpcyb, probe 9 there).
d-j28rp0 states what callers must check before `publish`; its clause about the import named the replaced check, so plan 2's builders reading it would expect the wrong one.
Cost if wrong: none to plan 2's code, which the import's check does not touch; only the statement's pointer changes.
