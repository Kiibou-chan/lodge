---
id: d-p8jdqj
kind: decision
title: "Plan 3 of the server build is ten tasks in lanes by the import graph"
scope: process
decided_by: planner
date: 2026-11-02T19:16:23+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "627", handle: "wc -l src/lodge/cli/*.py"}
  - {value: "34", handle: "lodge show d-26dx04 --reasoning"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 8c"}
---

The third plan of build step 1 is ten tasks: the dependencies, the command's grammar, its settings and files, projects and accounts in the store, the API's handler and record operations, sign-in and the person's operations, the command against the server with the reading tests, the writing tests, the program and its binary, and the page.
The grammar, the settings, and the accounts are built side by side, and the page beside the command's last tasks.

## Reasoning

lodge 0.2's command is 627 lines (`wc -l src/lodge/cli/*.py`) with 34 command test files (d-26dx04), and plan 1 sizes a task at one review's worth, about one Python module group with its carried tests (d-mfayy5): the grammar is `parser.py` and half of `threads.py`, the output and running are `commands.py`, `output.py`, `thread_output.py`, and the other half of `threads.py`, and the carried tests split into the reading commands and the writing ones, the second carrying tests over code the first wrote, as plan 1's Task 8c does.
`api` has no Python module to port beyond the viewer's place as the HTTP adapter (d-x6f9za), so it is cut where a test suite stands alone: the handler and the record operations with agent tokens, then the passkeys and the person's operations, then the page (d-jtxwg3).
The lanes follow the imports: the grammar and the settings import only `#core`, the accounts only `#app` and the store, and the page only `api` (the plan, "Order and lanes"); the author asked for the build to run in parallel lanes (d-xdqsmf, "Yes, parallelise").
Cost if wrong: a task too big for one review is split in its fix round, or two lanes meet in `src/cli/index.ts` and the merge keeps both exports.
