---
id: d-syhqa6
kind: decision
title: "Final review: the checkout gate checks both HEAD's tree and the working tree"
scope: process
decided_by: coordinator
date: 2026-10-29T19:32:58+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 189"}
---

C1, the checkout gate checks both HEAD's tree and the working tree and fails if either fails.

## Reasoning

HEAD alone stops checking staged records before a commit, the working tree alone misses a partial commit.
Cost if wrong: a gate run with uncommitted, broken records fails before the commit, which is the earlier and cheaper place.
Line handles such as spec:N refer to the files at this ruling's date.
