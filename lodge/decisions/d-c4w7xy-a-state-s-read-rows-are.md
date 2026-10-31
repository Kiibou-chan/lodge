---
id: d-c4w7xy
kind: decision
title: "A state's read rows are stored in buckets by the last two characters of the ID"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "1,024", handle: "32 times 32, the Crockford alphabet squared"}
  - {value: "0.92 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/phases.py /var/tmp/lodge-bench/s90000"}
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
  - {value: "3 s", handle: "the brief's ruling 3"}
  - {value: "156", handle: "160,000 divided by 1,024"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

A state's per-record read rows are stored as 1,024 marshal blobs, one per value of the last two characters of the record ID, and hold the derived parts only; the record's own text comes from the parse cache.

## Reasoning

Inserting one row per record took 0.92 s at 159,716 files (`probes/phases.py`), a third of the 3 s budget for a new state, while a show needs one record and its few links.
IDs end in random Crockford base32 characters (s-fdzcr2), so the buckets are even, about 156 records each at 160,000.
Keeping the text in the parse cache only keeps a state to the derived facts.
Cost if wrong: a broad search decodes many buckets, measured in Task 10.
