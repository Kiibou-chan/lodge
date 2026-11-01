---
id: d-j51qmy
kind: decision
code: DISK-1
title: "The index may take about 305 MB at 160,000 record files, keeping four states"
scope: product
decided_by: author
date: 2026-11-01T11:21:01+01:00
replaces: [d-4pbeax]
narrows: [d-a8gkrh]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
quote: {text: "A", where: "chat, answering DISK-1", when: "2026-11-01 11:20"}
numbers:
  - {value: "305 MB", handle: "1,900 bytes per file times 160,000 files"}
  - {value: "1,900", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/timings.md, the 1,900 columns"}
  - {value: "160,000", handle: "d-4pbeax, statement"}
  - {value: "251 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-10c-review.md:111"}
  - {value: "8.4 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-10c-review.md:111"}
  - {value: "276 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-10c-review.md:113"}
  - {value: "240 MB", handle: "d-4pbeax, statement"}
---

lodge's index may take about 305 MB of a repository's git folder at 160,000 record files, 1,900 bytes per file, keeping four stored states.

## Reasoning

The author chose A of DISK-1 over keeping SCALE-1's 240 MB, under which no complete state fits at 160,000 files, and over a plan round to shrink what a state holds.
SCALE-1's 240 MB rested on an estimate; one complete state measures 251 MB and each further state 8.4 MB, so four states need about 276 MB, which 305 MB holds with room.
The four states of d-4pbeax stay; only the bytes change.
d-a8gkrh keeps its formula and its rule for when the cap is checked; its `INDEX_BYTES_PER_FILE` becomes 1,900, so the cap is about 305 MB at 160,000 files, not 240 MB.
