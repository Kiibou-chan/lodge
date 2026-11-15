---
id: d-m5mwcm
kind: decision
title: "Separate import checks from refusal to publish"
scope: product
decided_by: coordinator
date: 2026-11-15T05:39:51+01:00
changes:
  - {entry: s-5sgcxx, action: edit}
  - {entry: s-chdc8y, action: create}
  - {entry: s-cssfnb, action: create}
  - {entry: s-6r0exg, action: edit}
  - {entry: s-tprwhs, action: edit}
  - {entry: s-d1dd20, action: edit}
narrows: [d-sw1dwn, d-jtbrh6]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
---

Separate import checks from refusal to publish.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:289.
Source settings, mapped settings, and atomic refusal remain the contract of d-sdpcyb.
Separate entries make each independently findable.
Only d-sw1dwn and d-jtbrh6 are narrowed, retaining their other claims.
s-6r0exg still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-tprwhs still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
s-d1dd20 still holds: its dependency was split or reaffirmed without removing the prerequisite that its unchanged claim needs.
No other looks-related decision is replaced or narrowed.
