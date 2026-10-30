---
id: d-w5x6g5
kind: decision
title: "Final wave: lodge keeps its own accepted ref to detect a rewritten branch"
scope: process
decided_by: coordinator
date: 2026-10-29T19:50:32+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 195"}
---

G4, lodge keeps its own ref `refs/lodge/accepted`, the last lodge tip it accepted, moved only by lodge (forward on a read whose fetched tip contains it, and after its own push; set on first use); every read compares it with the remote-tracking tip, a rewrite stands until acknowledged, reads say so, `check --gate` compares the accepted tip with the new one, and `add` refuses while that comparison has problems; the acknowledgement is deleting the ref with the git command the message names, not a new flag.

## Reasoning

Git's own fetch moves the remote-tracking ref, so only a ref lodge alone moves can see a rewrite, and a git command keeps the CLI the spec describes.
Cost if wrong: a stranger has to run one git command to accept a rewrite they meant.
Line handles such as spec:N refer to the files at this ruling's date.
