---
id: d-n65rhr
kind: decision
title: "A state is kept the second time it is read, after the output"
scope: process
decided_by: coordinator
date: 2026-11-01T06:04:08+01:00
narrows: [d-c4w7xy]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A read keeps a state in the index only the second time it finds that state not kept: the first such read answers in memory and writes the state's key as a marker, with any published facts and parse units it computed; a later read that finds the marker answers in memory, writes and flushes its output, and only then keeps the state in one transaction, whose failure changes neither the output nor the exit status; no read keeps a state before its output is flushed, and markers are bounded to the newest kept.

## Reasoning

Keeping a whole state at the largest synthetic store costs several seconds, measured in plan fix 7b, and a read that kept before printing would add that to every read after a change.
Many states are read once, after an edit and before the next one, so keeping on first sight pays the keep for states never read again; keeping on second sight pays it only for states read more than once, and after the output, so the reader waits for none of it.
Shortcuts that reuse an earlier state's stored rows were rejected in review for cases where they differ from a full build, so a kept state is always built in full from the files, and the full checks run on every read.
