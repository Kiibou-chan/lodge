---
id: d-x6vaw8
kind: decision
title: "Only a person writes a thread message under their own name"
scope: process
decided_by: planner
date: 2026-11-02T19:35:59+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "75-76", handle: "sed -n 75,76p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "139-145", handle: "sed -n 139,145p src/lodge/app/threads.py"}
  - {value: "357", handle: "git show origin/server-api:docs/superpowers/plans/2026-11-02-lodge-server-api.md | sed -n 357p"}
  - {value: "3e4c29c", handle: "git log -1 --format=%h origin/server-api"}
  - {value: "6", handle: "AST count of ask, reply, and close calls in tests/app/*.py whose by is the literal author"}
  - {value: "25", handle: "the same count for the literals agent (21), coordinator (2), and reviewer (2)"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/questions.md, STORE-1"}
---

`ask`, `reply`, and `close` refuse a message whose `by` names a person other than the actor, with `Forbidden` and nothing written, so an agent cannot write a person's words into a thread and one person cannot write another's; a person may still write under a role, as lodge 0.2's label allows; this holds until the author answers whether agents may relay a person's words.

## Reasoning

The design writes a person's decision only through that person, "since a signed-in person is a place an agent cannot reach" (`docs/superpowers/specs/2026-11-02-lodge-server-design.md:75-76`, SRV-2), and a thread message by a person is that person's words (the guide: write `--by author` "only with the author's words verbatim").
A thread whose last message is a person's no longer waits for that person (`waiting_in`, `src/lodge/app/threads.py:139-145`), so a message written for them ends their wait without them, and plan 3 passes `by` from the request body (its plan at `origin/server-api` 3e4c29c, line 357), so without the refusal any agent token can write it (correctness review I-5).
The carried app tests write `by: author` and agent roles through one `wired` `Lodge` (the `ask`, `reply`, and `close` calls of `tests/app/*.py`, counted over their syntax trees: 6 by `author`, 25 by a role), whose actor is `person("author")`, so refusing a role under a person's actor would change carried tests, while refusing another person's name changes none.
Whether agents may relay a person's chat words into a thread, as lodge 0.2 lets them with where and when, is a value trade-off the design does not settle, so it goes to the author as STORE-1 and this is the default until she answers.
Cost if wrong: if agents may relay, the check leaves `_message` and plan 3's command tests that write `--by author` through an agent token go back to lodge 0.2's form.
