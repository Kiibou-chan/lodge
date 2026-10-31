---
id: d-s2ypth
kind: decision
title: "One-shot commands run with the cyclic collector off"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
  - {value: "1.32 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/gc_derive.py /var/tmp/lodge-bench/s90000"}
  - {value: "0.91 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/gc_derive.py /var/tmp/lodge-bench/s90000"}
---

Every command except `view` runs with Python's cyclic garbage collector disabled.

## Reasoning

At 159,716 files `derive` took 1.32 s with the collector on and 0.91 s with it off (`probes/gc_derive.py`), since each collection walks every parsed record; a command lives for seconds and creates no reference cycles that matter, while the viewer is long-lived and keeps the collector.
Cost if wrong: more memory for one command, released when it exits.
