---
id: d-4pbeax
kind: decision
code: SCALE-1
title: "The index may take about 240 MB at 160,000 record files, keeping four states"
scope: product
decided_by: author
date: 2026-10-31T23:43:33+01:00
confirms: [d-hf2fms]
quote: {text: "A", where: "chat, answering SCALE-1", when: "2026-10-31 23:43"}
numbers:
  - {value: "240 MB", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md, option A"}
  - {value: "160,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md, option A"}
  - {value: "four", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md, option A"}
---

lodge's index may take about 240 MB of a repository's git folder at 160,000 record files, keeping four stored states.

## Reasoning

The author chose option A of SCALE-1 in docs/superpowers/plans/2026-10-31-lodge-at-scale/questions.md over B (about 160 MB, two states).
The plan's KEPT_STATES = 4 and its size cap follow this choice.
