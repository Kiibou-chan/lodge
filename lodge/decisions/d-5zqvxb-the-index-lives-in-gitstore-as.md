---
id: d-5zqvxb
kind: decision
title: "The index lives in gitstore, as new modules"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The SQLite index is part of `gitstore`, in new modules, behind a new `Index` port in `app`.

## Reasoning

Adding a package or an allowed import edge is the author's call (`CLAUDE.md`, Structure checks; `tests/structure_tables.py`, `ALLOWED`), and `gitstore` already owns the git common dir (`src/lodge/gitstore/setup.py`, `_common_dir`) and the blob IDs the index is keyed by.
Cost if wrong: a later move of a few modules into their own package.
