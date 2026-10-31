---
id: d-5qyhyw
kind: decision
title: "Task 6: search words are runs of letters or digits, lower-cased, without English function words"
scope: process
decided_by: coordinator
date: 2026-10-29T16:26:36+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
numbers:
  - {value: "2", handle: "src/lodge/core/search.py, _RELATED_WORDS"}
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 84"}
---

Search and `related` take words as runs of letters or digits, lower-cased, and ignore a fixed list of English function words.

## Reasoning

With digits as separators a query for a results number finds nothing, and with function words counted `related`'s threshold of 2 is met by "the" and "is" (task-6-report.md, concerns 1 and 3).
Cost if wrong: a query made only of function words falls back to the exact ID or code match.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
