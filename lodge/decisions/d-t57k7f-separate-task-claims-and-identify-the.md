---
id: d-t57k7f
kind: decision
title: "Separate task claims and identify the built server"
scope: product
decided_by: coordinator
date: 2026-11-15T05:00:53+01:00
changes:
  - {entry: s-07ar34, action: edit}
  - {entry: s-d1dd20, action: edit}
  - {entry: s-azfcx4, action: create}
  - {entry: s-h4x7bx, action: create}
  - {entry: s-1csktg, action: create}
  - {entry: s-8v6ek2, action: edit}
  - {entry: s-cf0qph, action: edit}
narrows: [d-sk1r7r]
numbers:
  - {value: "0.2", handle: "pyproject.toml, project.version"}
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 2"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 4"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 5"}
  - {value: "one level", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, The model, Task, one level of nesting"}
---

The server claim names its settling decision, and task definitions separate workflow execution, planning, and code links.

## Reasoning

M5 removes the unrelated viewer sentence from s-07ar34; d-3d4g9j and d-dyrpc6 still settle the viewer.
M9 names d-8kasej for the built server, and d-14vk9b remains the source of the lodge 0.2 MCP exclusion.
M7 retains the task identity and nesting in s-d1dd20 and separates the workflow, planner, and code-link lookups.
M8 keeps tasks at Build order item 2 and workflow execution at item 5.
The Build order gives no specific step for planner-created child tasks or a task having code links, so these claims carry no inferred step; runner item 4 and code-view item 6 do not directly assign them.
The design marks one-level nesting as [my call].
Sessions and artefacts still depend on the same task definition, so s-8v6ek2 and s-cf0qph are reaffirmed unchanged.
This narrows d-sk1r7r only for these descriptions and the inferred step assignments; all other model claims and earlier narrowings remain.
No: the author decisions d-8kasej and d-14vk9b remain untouched.
