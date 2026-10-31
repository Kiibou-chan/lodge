---
id: d-na1eg7
kind: decision
title: "A link change passes when another decision in the same change edits the entry"
scope: process
decided_by: coordinator
date: 2026-10-31T03:13:56+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-viewer.md"
---

Check 4 accepts a `link` action on an entry whose text also changed in the same change when another decision of that change lists the entry with `edit` or `create`; a `link` with no such decision still fails when anything beyond `rests_on` changed.

## Reasoning

Check 4 compares the published entry with the entry about to be published, so when one change holds a `link` decision and a later `edit` decision on the same entry, the text edit is charged to the `link` decision too (Task 9b's dry run, `docs/superpowers/plans/2026-10-31-lodge-viewer/task-9b-report.md`).
The design's rule is that a `link` change alters only `rests_on`; within one change, the edit decision accounts for the text, so the rule still holds for what each decision claims.
The alternative, publishing the link decisions first, would merge unreviewed viewer code into `main` before the final review.
Cost if wrong: a `link` decision could ride along with an edit it did not make, but the edit decision still names the entry, so no entry change goes without a decision.
