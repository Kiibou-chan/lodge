---
id: d-bbhak7
kind: decision
title: "A write that keeps a file's size and timestamps is unseen by the indexed reads, as by git status"
scope: product
decided_by: coordinator
date: 2026-11-01T16:52:14+01:00
narrows: [d-jwpwe7]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A write that leaves a record file's size, timestamps, and inode unchanged, for example through a shared memory map, is not seen by the five indexed reads until the file's stat changes or git's index is refreshed, just as `git status` does not see it; the gate and `add` read every file exactly.

## Reasoning

d-jwpwe7 takes stat-clean files at git's index blob, "as git status does", and names only removed conversion sources as the case where a read then prints text other than the disk's.
The final review of the build reproduced a second case: a write through a shared memory map that kept the file's stat made the indexed `show` print the committed text while `LODGE_INDEX=off` printed the disk text, with `git status` clean.
This is the same rule, not a new one: git's own stat check cannot see such a write either, so the indexed reads agree with `git status`, and the gate and `add`, which read every file, are exact.
Recording it states the rule's full consequence rather than leaving conversion histories as its only named stale case.
