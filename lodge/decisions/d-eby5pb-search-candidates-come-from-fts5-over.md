---
id: d-eby5pb
kind: decision
title: "Search candidates come from FTS5 over core's own words; ranking stays in core"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
  - {value: "1.09 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/fts.py /var/tmp/lodge-bench/s90000"}
  - {value: "52.8 MB", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/fts.py /var/tmp/lodge-bench/s90000"}
  - {value: "0.033 s", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/fts.py /var/tmp/lodge-bench/s90000"}
  - {value: "3.47.1", handle: "uv run --frozen python -c 'import sqlite3; print(sqlite3.sqlite_version)'"}
---

The index's full-text table holds, per parse, core's own word set of the title and of the statement, space-joined, under FTS5's `ascii` tokenizer, and gives only candidates; core ranks them with the function the in-memory search uses.
Without FTS5 a search reads the state into memory and ranks there.

## Reasoning

Core's words are runs of letters or digits without `_` (`src/lodge/core/words.py`), so they hold no ASCII separator, and the `ascii` tokenizer splits the joined text back into exactly those words; FTS5's other tokenizers fold diacritics or classify marks differently, which would lose candidates.
At 159,716 files the table took 1.09 s to fill and 52.8 MB, and a three-word AND match 0.033 s (`probes/fts.py`); SQLite 3.47.1 here has `ENABLE_FTS5`.
Cost if wrong: a slow broad search, not a different one, since every record the ranking would list is a candidate.
