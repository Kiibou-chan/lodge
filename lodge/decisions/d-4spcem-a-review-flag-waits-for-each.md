---
id: d-4spcem
kind: decision
title: "A review flag waits for each person whose decision raised it"
scope: process
decided_by: planner
date: 2026-11-02T19:05:51+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
---

A flagged decision waits for each person whose decision, or a decision they confirmed, raised the flag under lodge 0.2's rules; that person's later confirmation or replacement clears their part, and the decision stays flagged while a part is left; `Derived.awaiting` gives the persons, and the flags name them.

## Reasoning

The design: "A review flag on a person's decision clears only when that person confirms, not when another owner does" (design, "The model").
lodge 0.2's rules decide which decisions raise a flag and which clear it (`_flagged`, `_cleared`, and `_counts_for` in `src/lodge/core/derive.py`); reading them per person changes nothing for a project with one person, so the carried tests hold.
A decision that touches two people's decisions waits for both, since either one's words were changed.
Cost if wrong: a rule where any one of them clears is one condition in the derivation.
