---
id: d-zthdm7
kind: decision
title: "Task 7a of plan 3 stays one task, its report mapping each ported function to the tests that pin it"
scope: process
decided_by: planner
date: 2026-11-02T19:42:56+01:00
narrows: [d-p8jdqj]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "374", handle: "wc -l src/lodge/cli/commands.py src/lodge/cli/output.py src/lodge/cli/thread_output.py src/lodge/cli/threads.py (122 + 96 + 48 + 108)"}
  - {value: "41-93", handle: "sed -n 41,93p src/lodge/cli/commands.py"}
  - {value: "87-108", handle: "sed -n 87,108p src/lodge/cli/threads.py"}
  - {value: "6", handle: "sed -n 6p tests/e2e/test_before_init_one_sentence_exit_2.py"}
  - {value: "7", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md, Task 7b"}
  - {value: "7a", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md, Task 7a"}
  - {value: "7b", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md, Task 7b"}
  - {value: "7c", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-6"}
---

Task 7a keeps the client, the output, the running of every command, the test server, and the reading tests in one task.
Its report maps every function ported from `output.py`, `thread_output.py`, `commands.py`, and `threads.py` to the carried tests that assert its lines, and a function that no carried test pins is seen failing against a named mutation, as Task 7b's tests are.

## Reasoning

`run` dispatches every command in one function (`src/lodge/cli/commands.py:41-93`) and `run_thread` prints through `read_lines` and `check_lines` of `output.py` (`src/lodge/cli/threads.py:87-108`), so every cut the practice review offers (`docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md`, I-6) either leaves `run` with stand-ins for the commands of the later task, though a 7a test already runs `search`, `show`, `id`, and `check` (`tests/e2e/test_before_init_one_sentence_exit_2.py:6`), or ports `output.py` across two tasks, which d-tha8st avoids so that one review sees a module against its port.
The review's mutations for a 7c would test code written in the same task, which test-first does not need: a carried test over a module that does not exist yet fails.
The ported Python is 374 lines, each carried test asserts lodge 0.2's lines exactly, and the map turns the review's parity check into one table, function by function.
Cost if wrong: Task 7a's review takes longer, or misses an output line that Task 7b's writing tests or S1 find, one fix round on the main line.
