---
id: d-kky8qc
kind: decision
title: "The command's grammar is a small parser of its own, written to argparse's messages"
scope: process
decided_by: planner
date: 2026-11-02T19:16:33+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 6"}
  - {value: "232", handle: "wc -l src/lodge/cli/parser.py"}
---

The command's grammar is a small parser of its own in `cli`, written to argparse's usage lines and messages, with no library.

## Reasoning

The carried tests read argparse's text: `usage: lodge <name>` at the start of each help (`tests/e2e/test_help_lists_every_command.py`), `invalid choice` (`tests/e2e/test_id.py`, `tests/e2e/test_search.py`), and `is not a positive whole number` (`tests/e2e/test_search_limit.py`); the plan's probe 6 records the rest of argparse's lines.
A library words these otherwise (commander prints `Usage:` and `error: option ... argument ... is invalid`), so each would need overriding.
The grammar is fifteen commands with positionals and options (`src/lodge/cli/parser.py`, 232 lines, and `src/lodge/cli/threads.py`), small enough for one module.
Cost if wrong: one module replaced by a library with its messages overridden.
