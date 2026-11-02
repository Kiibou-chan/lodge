---
id: d-4qv0xb
kind: decision
title: "Carried tests that rewrote a decision write a new file; a relayed message is approved like an add"
scope: process
decided_by: planner
date: 2026-11-02T20:08:16+01:00
replaces: [d-81ps01]
narrows: [d-bwb1tt]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "3", handle: "src/lodge/core/check_state.py:130-136, check 3's quote rule"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 8"}
  - {value: "79", handle: "sed -n 79p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "37-41", handle: "sed -n 37,41p src/lodge/core/check_change.py"}
  - {value: "12c", handle: "git show origin/server-store:docs/superpowers/plans/2026-11-02-lodge-server-store.md, Task 12c"}
  - {value: "3", handle: "git show origin/server-store:docs/superpowers/plans/2026-11-02-lodge-server-store/plan-fix-3.md, For plans 3 and 4"}
---

In the third plan's carried command tests, a hand edit that rewrote a published decision writes a new file: `check_and_gate` a new unquoted decision by `author`, and `broken_agent_decision_warns_above_show` the broken agent decision beside the entry it edits.
A thread message `--by author` sent with an agent token is held for the author, so `author_words_are_recorded_exactly` and `waiting_groups_threads` assert the held line and approve it through the person's session, reading the thread's ID from the approval.

## Reasoning

The store refuses a changed text for an existing decision file (d-j28rp0, on `origin/server-store`, replacing d-pmaw3a).
In lodge 0.2, a new decision file by `author` with no quote makes `check` print `check 3: <id>: decided_by is author, but there is no quote; …` and exit 1, and `show` flag it `fails check` (probe 8), so `check_and_gate` keeps its shape for `check` and `show`.
On the server `check --gate` compares the current state with itself (`docs/superpowers/specs/2026-11-02-lodge-server-design.md:79`), and `check_change` turns a problem both states have into the note `already published, check 3: …` and passes (`src/lodge/core/check_change.py:37-41`; probe 8, the same file committed: `ok`, that note, exit 0).
The state Python's `broken_agent_decision_warns_above_show` reaches, the author's decision, the entry's edited text, and an unreadable file in the agent decision's place, is reached by one hand edit of two files, the decision file's name being the only difference.
The author answered STORE-1 with C (d-2v8vtk): an agent may relay a person's words, held until that person approves them; plan 2's Task 12c answers the relay `Written` with `outcome` held, `awaits` the person, and `held` the number, and mints an asked thread's ID at the approval, so the test reads the ID from the approval's answer, as d-bwb1tt's third substitution reads a held add's.
d-81ps01 had the relay refused (d-x6vaw8), which the author's answer overturns.
Cost if wrong: if the store comes to allow rewriting a decision, the two hand edits still hold; if relays stop being held, the two thread tests go back to lodge 0.2's form, one line each.
