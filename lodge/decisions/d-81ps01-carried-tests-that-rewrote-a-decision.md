---
id: d-81ps01
kind: decision
title: "Carried tests that rewrote a decision or relayed a person's words write them as the server allows"
scope: process
decided_by: planner
date: 2026-11-02T19:42:58+01:00
narrows: [d-bwb1tt]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "3", handle: "src/lodge/core/check_state.py:130-136, check 3's quote rule"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 8"}
  - {value: "79", handle: "sed -n 79p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "37-41", handle: "sed -n 37,41p src/lodge/core/check_change.py"}
  - {value: "1", handle: "git show origin/server-store:docs/superpowers/plans/2026-11-02-lodge-server-store/questions.md, STORE-1"}
---

In the third plan's carried command tests, a hand edit that rewrote a published decision writes a new file instead: `check_and_gate` writes a new decision by `author` with no quote, and `broken_agent_decision_warns_above_show` writes the broken agent decision and the entry it edits in one hand edit.
A thread message `--by author` sent with an agent token is refused, so `waiting_groups_threads` and `author_words_are_recorded_exactly` first assert the command's refusal and then write the author's message through the person's session.

## Reasoning

The store refuses a changed text for an existing decision file, and that ruling's cost if wrong names this plan's hand edits (d-pmaw3a, on `origin/server-store`).
In lodge 0.2, a new decision file by `author` with no quote makes `check` print `check 3: <id>: decided_by is author, but there is no quote; …` and exit 1, and `show` flag it `fails check` (probe 8), so `check_and_gate` keeps its shape for `check` and `show`.
On the server `check --gate` compares the current state with itself (`docs/superpowers/specs/2026-11-02-lodge-server-design.md:79`), and `check_change` turns a problem both states have into the note `already published, check 3: …` and passes (`src/lodge/core/check_change.py:37-41`; probe 8, the same file committed: `ok`, that note, exit 0), so the test asserts that.
The state Python's `broken_agent_decision_warns_above_show` reaches, the author's decision, the entry's edited text, and an unreadable file in the agent decision's place, is reached by one hand edit of two files, the decision file's name being the only difference.
d-x6vaw8 (on `origin/server-store`) refuses a message whose `by` names a person other than the actor, until the author answers STORE-1, and the person's session is the server's one way in for that person's words.
Cost if wrong: if the author answers STORE-1 with B, the two thread tests go back to lodge 0.2's form, one call each; if the store comes to allow rewriting a decision, the two hand edits still hold.
