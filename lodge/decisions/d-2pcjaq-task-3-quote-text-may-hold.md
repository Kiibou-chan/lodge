---
id: d-2pcjaq
kind: decision
title: "Task 3: quote text may hold line breaks and tabs as JSON escapes"
scope: process
decided_by: coordinator
date: 2026-10-29T15:39:27+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 50"}
---

`quote.text` may hold line breaks and tabs, written as JSON escapes; other header strings keep the control-character ban.

## Reasoning

Her words can span lines and the JSON quoting reads them back exactly.
Cost if wrong: none.
Line handles such as spec:N refer to the files at this ruling's date.
