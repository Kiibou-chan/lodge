---
id: d-n50szp
kind: decision
title: "Task 12: the hook's advice is to reverse your own edit with the same tool, never with git"
scope: process
decided_by: coordinator
date: 2026-10-29T18:47:06+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 168"}
---

I1, the hook's advice is the review's text (reverse your own edit with the same tool; never `git checkout`, `git restore`, `git stash`, or `git clean` on the file; tell the author if it cannot be restored exactly).

## Reasoning

"undo with git" discards her uncommitted edits and records an earlier `lodge add` staged (task-12-review.md, I1).
Cost if wrong: none.
Line handles such as spec:N refer to the files at this ruling's date.
