---
id: d-4m6m35
kind: decision
title: "A rank beyond a safe integer is refused"
scope: process
decided_by: coordinator
date: 2026-11-02T17:48:43+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "2^53", handle: "bun -e 'console.log(Number.MAX_SAFE_INTEGER)'"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md, C-1"}
  - {value: "16", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md, C-1"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md, C-1"}
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md, C-1"}
  - {value: "0.2", handle: "pyproject.toml, version"}
---

The TypeScript reader refuses a `rank` that is not a safe integer (above 2^53 - 1) as a format problem naming the key, where lodge 0.2 reads any integer; the report lists it as a known narrowing.

## Reasoning

`Number` rounds a rank of 16 or more digits silently, and the rounded value then passes the read-back check and is written out (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md`, C-1, Task 5a).
Every rank in this repository's records is between 1 and 10 (same finding), so the narrowing reaches only a draft with an implausible rank, and a refusal says so where rounding would change the record unseen.
A `bigint` rank would carry Python's behaviour into every reader and comparison for no record that needs it.
Cost if wrong: a draft with a huge rank is refused by the server and accepted by lodge 0.2.
