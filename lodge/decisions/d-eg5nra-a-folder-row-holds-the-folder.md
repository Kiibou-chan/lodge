---
id: d-eg5nra
kind: decision
title: "A folder row holds the folder's difference from the base tree"
scope: process
decided_by: coordinator
date: 2026-11-01T08:51:56+01:00
narrows: [d-8kq2nk]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A folder row holds the folder's difference from the base tree, its names the base lacks with their kinds and the base's names it lacks, keyed by the base tree's ID and taken with `lstat`, so a read whose folders are unchanged takes none of the base's names and never follows a link.

## Reasoning

Rows holding a folder's whole listing made every read with unchanged folders load the base tree's names, the largest remaining cost in the identity after the other fixes, measured in the plan's revision of its identity tasks.
A row of differences from a base keyed by that base's tree ID can never apply to another base, and `lstat` keeps a link in a folder from leading the read outside the repository.
