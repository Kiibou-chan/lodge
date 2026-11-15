---
id: d-0q54zn
kind: decision
title: "Stored bytes decode as surrogateescape does, in the task that first decodes them"
scope: process
decided_by: coordinator
date: 2026-11-02T17:48:43+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md, C-3"}
  - {value: "1", handle: "tests/core/test_fileformat_problems.py, test_bad_utf8_is_problem_1"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, The rest of build step 1"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, The rest of build step 1"}
---

The first TypeScript code that decodes a stored file's bytes (the store of plan 2 or the importer of plan 4) maps each byte b of an invalid UTF-8 sequence to U+DC00 + b, as Python's `surrogateescape` does, and `contentHash` encodes U+DC80 to U+DCFF back to that byte.

## Reasoning

lodge 0.2 decodes with `surrogateescape` (`src/lodge/gitstore/trees.py:16`), so a file with an undecodable byte is problem 1 and its hash covers the raw bytes; `TextDecoder`'s default turns the byte into U+FFFD and the file would parse as valid (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-review.md`, C-3).
No task of this plan decodes stored bytes, so the rule waits for the later plan's brief; the carried test `bad_utf8_is_problem_1` passes today only on a synthetic surrogate.
Cost if wrong: a file corrupted on disk imports as valid text with a replacement character, and its hash differs from lodge 0.2's.
