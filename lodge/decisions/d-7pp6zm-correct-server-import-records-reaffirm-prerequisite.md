---
id: d-7pp6zm
kind: decision
title: "Correct server import records: reaffirm prerequisite group 12"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-p02emc, action: edit}
  - {entry: s-9sjp9z, action: edit}
  - {entry: s-5fd1qs, action: edit}
  - {entry: s-5af9zq, action: edit}
  - {entry: s-ts73yt, action: edit}
  - {entry: s-h4x7bx, action: edit}
  - {entry: s-1csktg, action: edit}
  - {entry: s-pyr5rx, action: edit}
  - {entry: s-vvtd7f, action: edit}
  - {entry: s-pekv90, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, build order item 6; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-p02emc (A comment on a diff line becomes a thread) needs A task exposes its branches and diff, still supplied by s-1k9wbc: From build step 6, a task exposes its branches and diff; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-9sjp9z (A task can merge its branch on a person's go) needs A task exposes its branches and diff, still supplied by s-1k9wbc: From build step 6, a task exposes its branches and diff; s-xy6qte, still supplied by s-xy6qte: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-5fd1qs (Python tests specify the carried server behaviour) remains the independent claim stated at docs/superpowers/specs/2026-11-02-lodge-server-design.md; it has no changed prerequisite.
s-5af9zq (Development is test-first) remains the independent claim stated at docs/superpowers/specs/2026-11-02-lodge-server-design.md; it has no changed prerequisite.
s-ts73yt (Tasks and questions keep their own conversation context) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks.
s-h4x7bx (The planner creates children and the parent waits) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks.
s-1csktg (Tasks have code links) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks.
s-pyr5rx (A person moves a task on or sends it back with a reason) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks.
s-vvtd7f (Reported usage is totalled per task and step) needs Sessions report their work through the API, still supplied by s-n242p0: From build step 2, a session reports its steps and their state, status, artefacts, questions, and usage through the API; Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-pekv90 (A project sets how long a session can go without reporting) needs Sessions report their work through the API, still supplied by s-n242p0: From build step 2, a session reports its steps and their state, status, artefacts, questions, and usage through the API; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
