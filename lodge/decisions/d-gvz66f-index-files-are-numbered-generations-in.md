---
id: d-gvz66f
kind: decision
title: "Index files are numbered generations in WAL mode; the cap is twice SCALE-1's bytes per file"
scope: process
decided_by: planner
date: 2026-10-31T23:27:18+01:00
narrows: [d-4n5tr6, d-her016, d-hf2fms]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "10 minutes", handle: "a planner's bound, far above a read's length"}
  - {value: "1,500", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md, SCALE-1 A, 240 MB / 160,000"}
  - {value: "240 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md, SCALE-1 A"}
  - {value: "160,000", handle: "the brief's ruling 3"}
  - {value: "3 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-report.md, insert of every parse 1.38 s and FTS 1.09 s at 159,716 files"}
---

Index files are `index-<digest>.<generation>.sqlite` in WAL mode with `synchronous=NORMAL`; a writer finding the file over `2 × INDEX_BYTES_PER_FILE × files` builds the next generation under a temporary name, closes it, and renames it in; a later opening deletes generations superseded for 10 minutes, with their `-wal` and `-shm`.
Writes use `BEGIN IMMEDIATE`; a re-kept state becomes the newest.

## Reasoning

The coordinator's ruling of the third fix round asks for a rename swap and WAL; a rename over a WAL file still open elsewhere would pair it with the old file's `-wal`, so the new file gets a new name instead.
`INDEX_BYTES_PER_FILE = 1,500` is SCALE-1's option A, about 240 MB over 160,000 files; `NORMAL` is safe from corruption in WAL mode.
Cost if wrong: one rebuild of about 3 s when the cap is passed.
