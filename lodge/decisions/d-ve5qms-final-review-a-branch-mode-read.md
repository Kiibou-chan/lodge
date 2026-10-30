---
id: d-ve5qms
kind: decision
title: "Final review: a branch-mode read that cannot take the lock serves the cached ref and says so"
scope: process
decided_by: coordinator
date: 2026-10-29T19:32:58+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 190"}
---

G1, a branch-mode read that cannot take the lock serves the cached ref and says so.

## Reasoning

The plan's offline rule already serves the cache on a failed fetch, and a read never needs the lock to be correct.
Cost if wrong: a read during another add shows a state at most one add old, labelled.
Line handles such as spec:N refer to the files at this ruling's date.
