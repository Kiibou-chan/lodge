---
id: d-yng7m8
kind: decision
title: "The server design goes into lodge whole, each unbuilt claim naming its build step"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, 'Build order', item 1"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 4's paragraph"}
  - {value: "10", handle: "uv run --frozen --quiet lodge spec | grep -c '^# '"}
  - {value: "9", handle: "docs/superpowers/plans/done/2026-10-31-lodge-viewer.md, Tasks 9a to 9c"}
---

The server design goes into lodge whole, one coordinator decision per section, in three tasks after the server is built; an entry for a claim that build step 1 did not build says from which build step it holds and rests on the entry for the build order.
New areas `work` (tasks and workflows) and `sessions` (sessions and artefacts) hold the sections no existing area covers.

## Reasoning

The design document is frozen at the end of this plan (plan 1, plan 4's paragraph), and the viewer's design was frozen only once its content lived in lodge (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md`, Task 10), so all of it goes in, as the viewer plan's Tasks 9a to 9c put that design in, section by section.
lodge must not show wrong information (s-q4s548), and after build step 1 most of the design is not built (design, "Build order"), so an entry stating such a claim names the step it holds from.
The entries the built server makes false (s-a4jfp1, s-07ar34, s-z1zvb4, s-j8tp0n, s-v1sb0j, s-165qfh, s-3xka4c) are edited now, since the code they waited for exists (d-j3z85y).
The design's tasks, workflows, sessions, and artefacts have no area today (`lodge spec`'s ten areas), and putting them in `model` would make that area cover the server's whole product.
Cost if wrong: the area of some entries changes later, one decision per area; the step named in an entry is edited when the step is built.
