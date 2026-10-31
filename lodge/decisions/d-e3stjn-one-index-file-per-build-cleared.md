---
id: d-e3stjn
kind: decision
title: "One index file per build, cleared in place past the cap; old builds' files go after 7 days, locked"
scope: process
decided_by: coordinator
date: 2026-10-31T23:39:23+01:00
narrows: [d-gvz66f, d-n6tqzq]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "7 days", handle: "the coordinator's ruling"}
  - {value: "40 lines", handle: "the coordinator's ruling"}
  - {value: "10 minutes", handle: "d-gvz66f"}
---

One index file per build key, never swapped or renamed; past the size cap, the writer that notices deletes every table's rows in one `BEGIN IMMEDIATE` transaction, WAL readers keep their snapshot, and freed pages are reused; no VACUUM on a read.
After a clear, states rebuild lazily as cold reads, reported as cold, not under the changed-read stop.
Old builds' files are deleted only after 7 days without a write and under an exclusive non-blocking lock on a lock file readers hold shared.
The conversion key is compared whole before and after the git call.

## Reasoning

The third recheck's R1 (two rebuilders sharing a temporary file mix a WAL snapshot), R2 (10 minutes untouched does not prove an old file has no reader), R3 (a changed and restored attributes file files a wrong conversion under the old key), and R4 (a rebuild inside a changed read breaks its stop); this replaces the generation part of d-gvz66f.
The coordinator's ruling for the fourth fix round; without a lock protocol of about 40 lines, deletion of old builds' files would be dropped.
Cost if wrong: a clear costs one cold read.
