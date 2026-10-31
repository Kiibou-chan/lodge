---
id: d-a8gkrh
kind: decision
title: "The cap is SCALE-1's 240 MB with no factor; one state over the cap alone never triggers a clear"
scope: process
decided_by: planner
date: 2026-10-31T23:54:14+01:00
narrows: [d-gvz66f, d-e3stjn]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "240 MB", handle: "d-4pbeax"}
  - {value: "160,000", handle: "d-4pbeax"}
  - {value: "480 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-4.md, W3"}
  - {value: "2.5 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-4.md, W4"}
  - {value: "89.6 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-recheck-4.md, W4"}
  - {value: "16 MiB", handle: "the planner's bound for the WAL file"}
---

`INDEX_FILE_CAP = max(16 MiB, INDEX_BYTES_PER_FILE × files)`, about 240 MB at 160,000 files, as d-4pbeax chose.
The cap is checked before a keep only when a state has been kept since the last clear, so a store whose one state exceeds the cap holds at most two states between clears, and every second changed read clears.
Index connections set `secure_delete=OFF` and `journal_size_limit` to 16 MiB.

## Reasoning

The fourth recheck's W3 (a factor of 2 put the file at 480 MB for good, since a clear never shrinks it) and W4 (with secure delete compiled in, a clear wrote the whole file through the WAL, 2.5 s for 89.6 MB on the FUSE disk).
Cost if wrong: more frequent clears, each one cold read.
