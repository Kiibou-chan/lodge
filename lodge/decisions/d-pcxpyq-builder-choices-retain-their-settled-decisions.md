---
id: d-pcxpyq
kind: decision
title: "Builder choices retain their settled decisions and open work"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:46+01:00
changes:
  - {entry: s-fe4kyr, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
---

Builder choices retain their settled decisions and open work.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:311-317.
The design delegates implementation choices within shared operations and the listed views.
d-sry12f settles JSON HTTP operations, d-yayhct settles the passkey library, and d-4k9wcr settles Kysely.
The dependency checker is implemented with dependency-cruiser and TypeScript's parser, as held in s-165qfh.
The workflow syntax remains open; the example fields are its required content.

No other looks-related decision is replaced or narrowed.
