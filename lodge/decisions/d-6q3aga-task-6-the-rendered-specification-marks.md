---
id: d-6q3aga
kind: decision
title: "Task 6: the rendered specification marks flagged entries in their headings"
scope: process
decided_by: coordinator
date: 2026-10-29T16:32:51+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 87"}
---

I1, `render_spec(s, d, failing, area=None)` marks an entry carrying `awaiting the author`, `imported`, or `fails check` as `## <title> (<id> · <flags>)`.

## Reasoning

Must-not 1, the plan's format (plan:307) shows them as settled.
Cost if wrong: noisier headings in the rendered specification.
Line handles such as spec:N refer to the files at this ruling's date.
