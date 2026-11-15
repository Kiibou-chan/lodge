---
id: d-dfkqec
kind: decision
title: "The command parses .lodge.toml with smol-toml and refuses a whole-number float as lodge 0.2 does"
scope: process
decided_by: planner
date: 2026-11-02T19:16:25+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "80", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 1"}
  - {value: "2", handle: "lodge guide, last line"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 1"}
  - {value: "1.9.1", handle: "ts/package.json, dependencies"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 7"}
---

The command parses `.lodge.toml` with smol-toml and `integersAsBigInt`, turns each TOML integer into a number and each float, date, or time into null, and leaves the core's settings check to refuse what lodge 0.2 refuses; a TOML error is reported as the first line of smol-toml's message.

## Reasoning

`Bun.TOML.parse` gives the whole number 80 for `title_chars = 80.0` and `{"store":{}}` for a header `[store` with no closing bracket, where `tomllib` gives a float and an error, and lodge 0.2 prints `lodge: .lodge.toml: length.title_chars must be a positive whole number` and exits 2 (`docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md`, probes 1 and 2).
smol-toml 1.9.1 with `integersAsBigInt` gives a `bigint` for `80`, `0x50`, and `99999999999999999999`, and a `number` for `80.0`, `8e1`, and `inf`, in a table, an inline table, or a dotted key alike (probe 1).
Null is refused by `parseCoreSettings` wherever lodge 0.2 refuses a float: as a length (not a number), as a section (not a table), and in `import.sources` (not a file name) (`ts/src/core/settings.ts`, `parseCoreSettings`), and in the order lodge 0.2 checks them, since the check is the same code.
smol-toml's message runs over several lines, and lodge 0.2's test wants one sentence (`tests/e2e/test_malformed_settings_one_sentence_exit_2.py`).
smol-toml 1.9.1 was published on 2026-10-09 (probe 7), more than two weeks before it is added (d-4psbdv).
Cost if wrong: one dependency and one conversion in `cli/settings.ts`.
