---
id: d-d0vca9
kind: decision
title: "The file-writing rule matches fs's write functions, not every method named write"
scope: process
decided_by: coordinator
date: 2026-11-02T19:57:30+01:00
replaces: [d-4zg8q3]
narrows: [d-mfskz3]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, B-1"}
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md, Task 8"}
  - {value: "43", handle: "ts/tests/structure/calls.ts:43-46"}
  - {value: "149", handle: "ts/tests/structure/calls.ts:147-149"}
---

Outside `git`, the call rule reports `write`, `writev`, and their `Sync` forms only as functions called by name (imported from `fs`), and `.write`, `.writer`, and `.delete` as methods only on a `Bun.file(…)` call; a method named `write` on any other receiver, such as `process.stdout.write` in `cli` or `main`, is not a file write.

## Reasoning

The rule as built reports every call of a property named `write` outside `git` (`ts/tests/structure/calls.ts:43-46` and `:147-149`), so the command cannot print its output and `api` cannot write to standard error (plan 3's practice review, B-1, run at 6cc1986: `src/main.ts:2: file writing outside git`).
d-mfskz3 meant the file-writing forms lodge 0.2 refuses (`tests/structure_calls.py:14-38`, applied at `:139` and `:171`, where no method named `write` appears), and lodge 0.2's `cli` prints; a stream that writes a file is already refused where it is made (`createWriteStream`, `open` with a write flag), so a method named `write` on another receiver adds no file access.
d-x6f9za keeps each adapter at its lodge 0.2 permissions, so this restores the rule's intent rather than adding an allowed edge.
Cost if wrong: a file write through some other object's `write` method goes unreported; the gate's review then catches it, and the rule gains that receiver.
