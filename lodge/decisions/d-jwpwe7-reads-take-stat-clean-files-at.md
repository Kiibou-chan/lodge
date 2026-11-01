---
id: d-jwpwe7
kind: decision
code: STALE-1
title: "Reads take stat-clean files at git's index blob, as git status does"
scope: product
decided_by: author
date: 2026-11-01T11:18:58+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
quote: {text: "A", where: "chat, answering STALE-1", when: "2026-11-01 11:18"}
numbers:
  - {value: "3.1 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md, Task 8c, Step 4, R11-A"}
  - {value: "160,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md, Task 8c, Step 4"}
  - {value: "0.3 s", handle: "d-hxmdkz, statement"}
---

With no conversion source present, the five indexed reads take a file that git's index records as stat-clean at git's index blob, as `git status` does; after a conversion source is removed without the file being touched or staged again, such a read prints git's index text, which differs from the disk's only for `ident`, `filter`, and `working-tree-encoding` histories and never for line ends, which lodge's parser normalises; the gate and `add` read every file exactly.

## Reasoning

The author chose A of STALE-1 over B, a read that hashes every file on every read.
Hashing every file costs about 3.1 s at 160,000 files in the plan's identity task, ten times the 0.3 s target for a seen read, while the gate and `add` stay exact.
The one stale case is the one `git status` also has, and the gate and `add` catch it because they read every file.
This leaves d-atsx8n whole, since a path with a conversion source present is still read from disk, and d-7e8zhd whole, since every command outside the five reads stays on exact trees.
