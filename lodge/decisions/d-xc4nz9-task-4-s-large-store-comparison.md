---
id: d-xc4nz9
kind: decision
title: "Task 4's large-store comparison is bounded, and parity is proven on the smaller stores"
scope: process
decided_by: coordinator
date: 2026-11-01T01:51:53+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "900 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md, Task 1"}
  - {value: "785", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/task-4-review.md, equivalence section"}
---

Task 4's old-against-new comparison on the largest synthetic store keeps Task 1's 900 s bound per call: an old build that exceeds it is recorded as exceeding it, never retried without a bound; the reuse of identical states is proven equal by the review's 785 old-against-new runs on the two smaller synthetic stores and the repository's own store, across staged, unstaged, untracked, touched-only, renamed, deleted, hand-edited, branch-mode, and rewritten-branch states.

## Reasoning

The plan's Task 4 Step 4 asks for that comparison on the largest store, but the build before the plan's fixes does not finish a single read there, so the step cannot finish as written; the builder stopped and asked, rightly.
The reuse rests on a proof that holds for every input, since loading depends only on the files and attachments and no part of the change check fires when a state is compared with itself; the runs on the smaller stores test that proof against the old code, while the largest store adds only size, which Task 12's table measures on the new build alone.
