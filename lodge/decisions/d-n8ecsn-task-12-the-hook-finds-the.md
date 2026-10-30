---
id: d-n8ecsn
kind: decision
title: "Task 12: the hook finds the repository from the edited file, and the README states the glob syntax"
scope: process
decided_by: coordinator
date: 2026-10-29T18:50:16+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 169"}
---

M1 and M2, the hook finds the repository from the edited file's folder, not the session's, and fires only where lodge is initialised there; M3, the README states the frozen-glob syntax lodge implements, relative to the repository root (`*` does not cross `/`, `[...]` is literal); M4, the frozen-file text names `lodge guide`; M5, resolving the edited path counts as reading the hook's input (LODGE-5).

## Reasoning

See task-12-review.md, Minors, each run.
Cost if wrong: one more path lookup per edit.
Line handles such as spec:N refer to the files at this ruling's date, in the history before the squash, which this repository does not hold; the section named beside a handle is the way in.
Report and review names are files in `docs/superpowers/plans/done/2026-10-29-lodge/`; probe scripts were scratch and are not kept.
