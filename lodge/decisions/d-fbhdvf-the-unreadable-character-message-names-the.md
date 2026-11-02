---
id: d-fbhdvf
kind: decision
title: "The unreadable-character message names the code point in decimal, as lodge 0.2 does"
scope: process
decided_by: coordinator
date: 2026-11-02T17:37:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1", handle: "uv run --frozen python -c over 'a: b\\nc: \\x01\\n' through lodge.core.yamlio.load_yaml"}
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md, C-3"}
---

`loadYaml` says `unreadable character N`, N the decimal code point, as lodge 0.2 says it, not the character as `pyRepr` gives it.

## Reasoning

PyYAML's `ReaderError.character` is the code point as an integer, so lodge 0.2's `{error.character!r}` prints `1` for U+0001 (`src/lodge/core/yamlio.py:64-66`; `docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md`, C-3); the plan read it as the repr of a string.
Parity with lodge 0.2 is the rule (d-88p8h9).
Cost if wrong: one message string.
