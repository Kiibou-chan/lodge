---
id: d-sw1dwn
kind: decision
title: "Scope import writer checks and clarify moved advice"
scope: product
decided_by: coordinator
date: 2026-11-15T05:01:03+01:00
changes:
  - {entry: s-yaz279, action: edit}
  - {entry: s-3cagcv, action: edit}
  - {entry: s-5sgcxx, action: edit}
  - {entry: s-yv40f3, action: create}
  - {entry: s-2wqxmw, action: create}
narrows: [d-jtbrh6]
numbers:
  - {value: "0.2", handle: "pyproject.toml, project.version"}
---

Import writer checks apply only to decisions and threads whose author attribution is mapped.
Moved-project advice clearly excludes attachments, and import validation separates path and attachment rules.

## Reasoning

M3 follows ts/src/app/importing.ts: the changes test skips unmapped decisions and threads before the writer comparison.
The export attribution sentence belongs only to s-b6jxhr; s-yaz279 retains import mapping and drops its unnecessary export dependency.
M4 makes the attachment exception modify the advised files, not where the records live.
M7 keeps source and mapped-state validation together and separates non-UTF-8 path refusal and attachment-byte preservation into individual lookups.
The source settings revision remains part of the source check, and no publication occurs if either check fails.
The mapping is the design's [my call], as implemented under d-83kt6y and d-hg9qq9; d-sdpcyb and d-va3j7x still settle validation and moved advice.
This narrows d-jtbrh6 only for these descriptions; all remaining import and hook claims stand.
No: d-sdpcyb, d-va3j7x, and author d-b61590 remain untouched.
