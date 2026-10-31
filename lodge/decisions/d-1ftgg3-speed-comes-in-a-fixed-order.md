---
id: d-1ftgg3
kind: decision
title: "Speed comes in a fixed order: superlinear steps, libyaml, then the identical-state reuse"
scope: process
decided_by: coordinator
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "6.7 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/phases.py /var/tmp/lodge-bench/s9000 --profile OUT, then pstats on OUT"}
  - {value: "16,008", handle: "find /var/tmp/lodge-bench/s9000/lodge -type f | wc -l"}
  - {value: "0.67 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/phases.py /var/tmp/lodge-bench/s9000"}
  - {value: "3.47 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/phases.py /var/tmp/lodge-bench/s9000 --pure-yaml"}
---

Speed work comes in this order: first `_missing` and any other superlinear step a profile at 16,000 and 160,000 files finds; then libyaml with a fallback to the Python loader on any C error; then reusing the parsed snapshot when current and published trees are identical, skipping the change check only where its result is provably the identical-state result.

## Reasoning

The brief for lodge at scale, ruling 2, binding on the plan.
`_missing` alone took 6.7 s of a profiled read at 16,008 files (`probes/phases.py --profile`), and the C loader parses the same headers about five times faster (0.67 s against 3.47 s at 16,008 files).
Cost if wrong: an order that delays the largest saving by a task or two.
