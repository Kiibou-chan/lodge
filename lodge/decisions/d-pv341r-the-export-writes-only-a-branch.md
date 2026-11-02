---
id: d-pv341r
kind: decision
title: "The export writes only a branch of its own, without a work tree or force"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "50", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:50"}
  - {value: "283", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:283"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "284", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:284"}
  - {value: "402", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 4"}
  - {value: "34", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 4"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 4"}
---

The export writes a branch that holds nothing outside `lodge/` and that no work tree has checked out, building the commit in a temporary index, making none when the tree is unchanged, and pushing without force when the target names a remote; any other branch is refused.

## Reasoning

lodge never merges into a project's main branch without a person's go (design line 50), and a project's main branch holds its code, so a branch holding only `lodge/` can never be one; a separate repository's branch qualifies alike (design line 283, d-khew4n).
lodge 0.2's branch mode keeps its store on a branch holding only `lodge/` (`src/lodge/gitstore/branch.py`, `init_branch`, with `KEPT`), so such a branch is a lodge 0.2 store as it stands, which the export must be (design line 284), and a project's own 0.2 branch can be the target.
lodge 0.2 commits through a temporary index and pushes without force, never touching a work tree (`src/lodge/gitstore/plumbing.py`); on a bare repository, 402 files take 34 ms, an unchanged tree makes no commit, and a branch that moved is refused by `update-ref` (probe 4 of the plan's `probes.md`).
Moving a branch that a work tree has checked out would make that work tree show the export as its own changes, reversed, so that branch is refused (probe 4).
Cost if wrong: a project that wants its export inside its main branch's tree needs a mode that asks a person's go for each commit.
