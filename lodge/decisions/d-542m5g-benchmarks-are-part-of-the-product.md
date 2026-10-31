---
id: d-542m5g
kind: decision
title: "Benchmarks are part of the product, on synthetic data only"
scope: process
decided_by: coordinator
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "1,600", handle: "the brief's ruling 5"}
  - {value: "16,000", handle: "the brief's ruling 5"}
  - {value: "160,000", handle: "the brief's ruling 5"}
---

`scripts/bench_store.py`, a read-replay benchmark that runs a command list against two lodge builds and compares timing and output, and a recorded table of timings at 1,600, 16,000, and 160,000 files are part of the product.
They use synthetic data only.

## Reasoning

The brief for lodge at scale, ruling 5, binding on the plan.
lodge is public (s-fk3yzy), so no other project's records may appear in a benchmark.
Cost if wrong: a benchmark that cannot be shared.
