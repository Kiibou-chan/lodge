---
id: d-c400w8
kind: decision
title: "The parse cache is keyed by path and blob ID and stored as marshal of plain tuples"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "16,008", handle: "find /var/tmp/lodge-bench/s9000/lodge -type f | wc -l"}
  - {value: "0.011 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/codec.py /var/tmp/lodge-bench/s9000"}
  - {value: "0.014 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/codec.py /var/tmp/lodge-bench/s9000"}
  - {value: "0.021 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/codec.py /var/tmp/lodge-bench/s9000"}
  - {value: "1.56 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/phases.py /var/tmp/lodge-bench/s90000"}
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
---

The parse cache is keyed by a file's path and its git blob ID, and stores the parse as `marshal` of plain tuples, strings, and integers, never `pickle`.

## Reasoning

Parsing depends on the path (an entry's area comes from its folder, `src/lodge/core/fileformat.py`, `parse_record`), so the path is part of the key.
`pickle.loads` runs code a planted index file names; `marshal.loads` builds only data, and the decoder accepts only the tuple shapes it wrote.
At 16,008 files marshal took 0.011 s out and 0.014 s back plus 0.021 s to rebuild the records; pickle one by one took 1.56 s back at 159,716 (`probes/codec.py`, `probes/phases.py`).
Cost if wrong: a slower or larger cache, not a wrong one.
