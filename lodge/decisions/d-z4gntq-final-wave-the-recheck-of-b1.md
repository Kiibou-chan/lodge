---
id: d-z4gntq
kind: decision
title: "Final wave: the recheck of B1 and the build of B2 run at the same time"
scope: process
decided_by: coordinator
date: 2026-10-29T20:30:09+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 202"}
---

Recheck B1 (fresh Sonnet rechecker on a scratch copy of 2c6b62b) and build B2 run at the same time.

## Reasoning

The rechecker never writes to the worktree, and any B1 fix folds into the B2 recheck round.
Cost if wrong: a B1 fix lands after B2 and needs one more small recheck.
Line handles such as spec:N refer to the files at this ruling's date.
