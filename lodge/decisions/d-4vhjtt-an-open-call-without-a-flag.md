---
id: d-4vhjtt
kind: decision
title: "An open call without a flag is a read"
scope: process
decided_by: coordinator
date: 2026-11-02T20:36:22+01:00
narrows: [d-d0vca9]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "137", handle: "ts/tests/structure/calls.ts:137-139"}
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "211", handle: "tests/structure_calls.py:211-215"}
  - {value: "233", handle: "tests/structure_calls.py:233-239"}
---

Outside `git`, the call rule reports `open` and `openSync` as a file write only when the call names a flag argument that is not a string literal or whose literal holds `w`, `a`, or `+`; a call without a flag argument is a read, since Node's and Bun's `open` default to `"r"`.

## Reasoning

The rule as built reports any `open(…)` without a flag as a write (`ts/tests/structure/calls.ts:137-139`), so a plain read such as `openSync(p)` in `cli`, and plan 3's `io.open(data)` port in `api`, fail the gate (plan 1's final review, F-1, `final-review.md`).
lodge 0.2 reports a call by name, `open(p)`, only when a mode is given that writes or is not a literal (`tests/structure_calls.py:211-215`, `:233-239`); its attribute form reads the mode from the first argument because pathlib's `Path.open(mode)` takes it there, an idiom JavaScript has no counterpart for, so the flag's place in TypeScript is the second argument and its absence means a read.
d-x6f9za keeps each adapter at its lodge 0.2 permissions, so this restores the rule's intent rather than loosening it.
Cost if wrong: a write through an object whose `open` takes its flag elsewhere goes unreported; review catches it, and the rule gains that form.
