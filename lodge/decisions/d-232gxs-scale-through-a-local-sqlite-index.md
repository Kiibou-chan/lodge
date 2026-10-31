---
id: d-232gxs
kind: decision
title: "Scale through a local SQLite index in the git common dir, with no server unless measured necessary"
scope: process
decided_by: coordinator
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "160,000", handle: "the brief's ruling 3"}
  - {value: "0.3 s", handle: "the brief's ruling 3"}
  - {value: "3 s", handle: "the brief's ruling 3"}
---

lodge scales through a local SQLite index in the git common dir, never committed, safe to delete, and rebuilt on a version mismatch or corruption: parses keyed by content and parser version, and per state the statuses, flags, and check results reads need, with a full-text index.
Reads answer from it; the gate and `add` may use the parse cache but always derive and check in full.
Targets on native disk at 160,000 files: a read on a seen state at most 0.3 s, a read after one changed record at most 3 s; a server is out of scope unless the warm read stays above 0.3 s.

## Reasoning

The brief for lodge at scale, ruling 3, binding on the plan, answering the author's request of 2026-10-31 that lodge handle large amounts of data, local file-based solutions preferred.
s-j8tp0n already holds that any index is disposable, and s-07ar34 that there is no server for now.
Cost if wrong: if the targets cannot be met with an index, the plan stops and reports instead of building a server.
