---
id: d-p60ka9
kind: decision
title: "Brief lines drop the status current under the default filter"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "10 %", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/fts.py /var/tmp/lodge-bench/s90000"}
  - {value: "200", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/fts.py /var/tmp/lodge-bench/s90000"}
---

Under the default status filter a brief line omits ` · current`, and the output's first line says that listed records are current unless marked; every other field stays.

## Reasoning

Under the default filter every listed record is current (`src/lodge/core/search.py`, `Filters.status`), so the word carries nothing; it was 10 % of the characters of 200 brief lines on the synthetic store (`probes/fts.py`), and an advisor's measurement on a real store found it among the largest default fields.
Who decided and the day stay, because whether a change is the author's or an agent's is what tells a reader how settled it is (s-q4s548), and flags stay for the same reason.
Cost if wrong: a reader who misses the first line reads an unmarked record as current, which it is.
