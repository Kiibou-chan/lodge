---
id: d-mkstz5
kind: decision
title: "lodge-on-itself merges into main before the viewer's records tasks"
scope: process
decided_by: coordinator
date: 2026-10-31T02:55:51+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-viewer.md"
---

The branch `lodge-on-itself` (Tasks 1, 2, 4, and 5 complete, Task 3 deferred to the viewer) merges into `main` now, and its final whole-branch review is folded into the final review of `lodge-viewer`, which contains it.

## Reasoning

Task 8's first dry run failed check 4 because the 82 entries exist only on unpublished branches, so a `link` change to them reads as a change to a new entry (`docs/superpowers/plans/2026-10-31-lodge-viewer/task-8-report.md`).
The published state is the merge base with `main`; once the entries are on `main`, `link` changes are what the design means them to be.
The author allowed merges to `main` at the coordinator's judgment (d-5drmnk).
Every task of `lodge-on-itself` was reviewed and its findings fixed (its progress file), and the gate is green at its tip.
Cost if wrong: a finding of the final review on those records is fixed on `main` through the viewer branch, rather than before the merge; nobody installs from `main` until the release tag, which waits for that review.
