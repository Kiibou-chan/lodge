---
id: d-mfayy5
kind: decision
title: "Tasks 5, 7, 8, and 9 of the core plan are split, their numbers kept"
scope: process
decided_by: planner
date: 2026-11-02T14:51:01+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "5", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 5"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 7"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 8"}
  - {value: "9", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 9"}
---

Tasks 5, 7, 8, and 9 are split: 5a record files, 5b drafts and the text tests of record files; 7a doubts and derived statuses, 7b confirmations and the order; 8a the state check, 8b the change check, 8c the other check tests; 9a levels, 9b the specification and search.
The numbers are kept so the reviews' handles hold; a test file whose code an earlier half ported is seen failing against a mutation named in the report.

## Reasoning

Tasks 5, 7, 8, and 9 port 682 and 877, 463 and 780, 494 and 1,189, and 557 and 825 Python lines of module and test (`wc -l`; `plan-review-practice.md`, P-I9), where the largest task commit of the viewer build was 1,122 lines with its report, and that build split two tasks for size (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md`, Call 22).
Each cut follows the imports, so a reviewer can reject one half and accept the other: `drafts.py` imports only what 5a ports; `confirmation.py` and `order.py` import `derive.py`, which 7a ports; `check_entries.py`, `check_immutable.py`, and `check_change.py` import `check_state.py`, which 8a ports; and `render.py` and `search.py` import `views.py`, which 9a ports, as do the four tests that wait as `test.todo` (`grep '^from lodge.core' src/lodge/core/*.py`).
Every carried check test but `test_check_state.py` goes through `check_change` (`tests/core/checks.py`), so 8c's three files carry tests over code 8b ported; showing each failing against a named mutation is how the viewer build's fix rounds kept test-first for code that already existed (`docs/superpowers/plans/done/2026-10-31-lodge-viewer-progress.md`, its Task 6a line).
Cost if wrong: five more coordinator rounds of brief, gate, and review.
