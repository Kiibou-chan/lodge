---
id: d-atsx8n
kind: decision
title: "A path git may convert is always read from disk"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "224 to 232 ms", handle: "git check-attr --stdin -z text eol filter ident working-tree-encoding < paths, in /var/tmp/lodge-bench/s90000"}
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
---

A path under `lodge/` whose bytes git may convert between the working tree and the blob (`core.autocrlf` set, or a `text`, `eol`, `filter`, `ident`, or `working-tree-encoding` attribute) is always read from disk and hashed, never taken from git's index.

## Reasoning

`git diff-files` calls a file unchanged by its stat, so with a conversion the working-tree bytes differ from the blob while git reports no change, and the parse of the blob would not be the parse of the file today's `disk_tree` reads (`src/lodge/gitstore/checkout.py`, `disk_tree`).
Checking every path costs 224 to 232 ms at 159,716 files (`git check-attr --stdin`), so it runs only when the attributes' signature changes, and not at all when no attributes file and no conversion setting exist.
Cost if wrong: a slower read in a repository with attributes, never a wrong one.
