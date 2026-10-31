---
id: d-q051s2
kind: decision
title: "libyaml only behind a guard that admits the writer's header shapes"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "2,516", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-opus.md, B1"}
  - {value: "200,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-opus.md, B1"}
  - {value: "165,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-review-opus.md, B1, three runs of about 55,000"}
---

The C loader parses a header only when a guard admits it, every line having a shape lodge's writer produces; every other header goes to the Python loader.
Task 3's tests include a seeded fuzz comparison of the two loaders on admitted headers, bounded in run time, and the trailing-tab case.

## Reasoning

The correctness review's B1: with a fallback on C errors alone, 2,516 of 200,000 fuzzed headers parsed under C and failed under Python, among them `title: x` followed by a tab, so a check 1 failure would disappear; a guard of that kind gave zero differences on about 165,000 admitted headers.
The coordinator's ruling 1 for the fix round.
Cost if wrong: headers outside the guard parse at the Python loader's speed, once per blob with the parse cache.
