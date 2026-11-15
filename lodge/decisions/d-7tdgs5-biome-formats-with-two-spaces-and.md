---
id: d-7tdgs5
kind: decision
title: "Biome formats with two spaces and lines of 100 characters"
scope: process
decided_by: planner
date: 2026-11-02T14:22:42+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "100", handle: "grep line-length pyproject.toml"}
---

Biome formats the TypeScript with an indent of two spaces and a line width of 100 characters.

## Reasoning

Ruff's line length for lodge 0.2 is 100 (`pyproject.toml`, `line-length = 100`), so a reviewer reads both codes at one width.
Two spaces is Biome's default and the common TypeScript indent, so the formatter's defaults stay untouched but for the width.
Cost if wrong: one reformatting commit.
