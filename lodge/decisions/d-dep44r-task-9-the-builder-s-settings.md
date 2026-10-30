---
id: d-dep44r
kind: decision
title: "Task 9: the builder's settings, stale-mark, attachment, and pre-push-hook choices stand"
scope: process
decided_by: coordinator
date: 2026-10-29T17:34:38+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 124"}
---

The builder's choices stand: `ProjectSettings.raw` is the whole table (Task 12's `main` passes `raw.get("hook", {})`), the stale mark after a rejected push lives in the process, attachments are never overwritten, and pushes run her pre-push hooks.

## Reasoning

The stale mark only shortens the next fetch wait and a push without force rejects a stale tree anyway, and her hooks are hers to keep (task-9-report.md, concerns 1 to 6).
Cost if wrong: a pre-push hook can refuse lodge's push, shown as a `LodgeError`.
Line handles such as spec:N refer to the files at this ruling's date.
