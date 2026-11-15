---
id: d-j3z85y
kind: decision
title: "The author's decisions behind the server design go into lodge before the build"
scope: process
decided_by: planner
date: 2026-11-02T14:10:38+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1", handle: "ARCH-1, docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md"}
  - {value: "4", handle: "ARCH-4, docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md"}
  - {value: "2", handle: "SRV-2, docs/superpowers/specs/2026-11-02-lodge-server-design.md, The model"}
  - {value: "9", handle: "docs/superpowers/plans/done/2026-10-31-lodge-viewer.md, Task 9a"}
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
---

The plan's first task records the author's eight answers behind the server design (ARCH-1 to ARCH-4, the export to a separate repository, SRV-1, SRV-2, and her approval) as author decisions with her quotes; the entries they make false wait until the code is built, for the fourth plan's records task.

## Reasoning

`CLAUDE.md` makes `lodge spec` the authority and has the plan argue from it, but lodge holds none of these answers: `lodge search TypeScript` prints "no matches", and s-a4jfp1 says "lodge is written in Python".
Her decisions in lodge let the plan cite a record for each premise, as the viewer plan did with her quotes (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md`, Task 9a).
The entries s-a4jfp1, s-07ar34, s-z1zvb4, and s-j8tp0n still hold for lodge 0.2, which stays in use until a project moves (design, "Moving from lodge 0.2"), so editing them now would state what is not yet true.
Cost if wrong: eight author records, immutable, whose `where` and minute need her replacement if wrong; the coordinator takes both from the session before adding.
