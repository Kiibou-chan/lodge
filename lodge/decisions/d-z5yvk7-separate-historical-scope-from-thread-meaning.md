---
id: d-z5yvk7
kind: decision
title: "Separate historical scope from thread meaning and evaluation"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:12+01:00
changes:
  - {entry: s-7ah5n7, action: edit}
  - {entry: s-0c65f3, action: create}
  - {entry: s-65pyqz, action: create}
  - {entry: s-wgkrmr, action: edit}
  - {entry: s-5tgnrn, action: edit}
  - {entry: s-73ee5k, action: edit}
  - {entry: s-r2cc8d, action: edit}
  - {entry: s-1hecad, action: edit}
narrows: [d-6x8fd9, d-68b0j2, d-cg3nn3]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "0.2", handle: "pyproject.toml:3, project.version = \"0.2.0\""}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:21-30, Build order and section content"}
---

Separate historical scope from thread meaning and evaluation.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:21-30.
The lodge 0.2 exclusions stay historical.
The thread meaning follows d-68b0j2 and its reasoning in d-a3h9f3.
The evaluation-and-pilot condition comes from d-cg3nn3.
The removed server-scope sentence is already held by s-d1dd20, s-cf0qph, s-8v6ek2, s-t4tbrj, and s-6r0exg; these are linked rather than restated.
Only coordinator decisions are narrowed, and all other claims remain.
s-wgkrmr still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-5tgnrn still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-73ee5k still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-r2cc8d still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-1hecad still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
No other looks-related decision is replaced or narrowed.
