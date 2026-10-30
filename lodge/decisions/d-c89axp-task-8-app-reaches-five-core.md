---
id: d-c89axp
kind: decision
title: "Task 8: app reaches five core names as core.<name>, not by direct import"
scope: process
decided_by: coordinator
date: 2026-10-29T17:00:36+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 110"}
---

`app` reaches the five core names that are also core module names (`check_change`, `check_state`, `derive`, `feedback`, `search`) as `from lodge import core` and `core.<name>`, and Tasks 10 to 12 do the same; the structure rules and module names stay.

## Reasoning

`tests/structure_imports.py` reads `from lodge.core import derive` as the submodule, and changing that rule is the author's call (CLAUDE.md, Structure checks).
Cost if wrong: two import styles side by side until a rename.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
