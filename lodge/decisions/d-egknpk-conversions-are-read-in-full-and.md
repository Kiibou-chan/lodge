---
id: d-egknpk
kind: decision
title: "Conversions are read in full and reported beside the targets"
scope: process
decided_by: coordinator
date: 2026-11-01T05:38:44+01:00
narrows: [d-232gxs]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "3.1 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/plan-fix-6/plan-fix-6b.md, conversion row (identity 3.148 s at 83ef70b)"}
  - {value: "160,000", handle: "the brief's ruling 3"}
---

Where a conversion source is present (`core.autocrlf` true or `input`, or an attributes source that converts), the fast identity reads every file it may convert (d-dqpf59), about 3.1 s at 160,000 files under `core.autocrlf=input`; that configuration is measured and reported beside the targets, not under them, and the stop on missed targets (d-26e6zj) applies to the configuration without conversions.

## Reasoning

Git's index records a file's stat but not whether the bytes on disk were converted when git wrote its blob, so with a conversion source present a stat-clean file can still differ from git's blob; reading it is the only exact answer.
Two ways to avoid the reads were measured and rejected: a private git index as a per-file stat cache failed an adversarial review with reproduced stale blobs, among them a write through a memory map on native ext4 that kept a file's stat, and a stat cache in lodge's own index file costs more than the target in Python's stat calls alone.
Correctness comes first, so the configuration with conversions is slower and says so in the recorded table, rather than read from a cache that can be wrong.
