---
id: d-p48gr1
kind: decision
title: "The YAML layer keeps the enumerated refusals and lists its other differences from PyYAML"
scope: process
decided_by: coordinator
date: 2026-11-02T17:37:31+01:00
narrows: [d-bkc7md]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md, C-2"}
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "12", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 12"}
---

The TypeScript YAML layer refuses what d-bkc7md enumerates; where the YAML 1.2 parser otherwise reads a header differently from PyYAML (a tab after a colon, an empty key, an anchor outside `[0-9A-Za-z_-]`, U+0085, U+2028, U+2029, or a lone CR as a line break, and a quoted or flow value continued at column 0), the difference is listed in the Task 4 report and pinned by a test of the TypeScript behaviour.

## Reasoning

The review of Task 4 found these differences on a corpus run against lodge 0.2 (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-review.md`, C-2).
Record files reach the core only from a writer: lodge 0.2's `lodge add` or the TypeScript writer, and both refuse a text that does not read back unchanged (`src/lodge/core/fileformat.py`, `write_record`), with every value quoted by `quoted`; neither writes any of these forms, so the differences reach drafts only, and the differential run of Task 12 over this repository's records is not affected.
A draft the server reads that lodge 0.2 would refuse is exported through the writer, so the exported file is one lodge 0.2 reads.
Emulating PyYAML's scanner for tabs and line breaks would be a second parser in `core`, with its own errors.
Cost if wrong: an agent's draft with one of these forms gets a different answer from the server than from lodge 0.2; a pre-check can be added later without changing any record.
