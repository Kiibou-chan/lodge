---
id: d-edj27k
kind: decision
title: "Correct server import records: reaffirm prerequisite group 10"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-1hecad, action: edit}
  - {entry: s-h1e6jc, action: edit}
  - {entry: s-bxws89, action: edit}
  - {entry: s-nj99c5, action: edit}
  - {entry: s-7zx39z, action: edit}
  - {entry: s-awkdkw, action: edit}
  - {entry: s-dazqbj, action: edit}
  - {entry: s-xe5bmq, action: edit}
  - {entry: s-68vtrb, action: edit}
  - {entry: s-n242p0, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, build order item 6; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-1hecad (Session to-do items may name produced code references) needs Each task occupies one workflow step, still supplied by s-azfcx4: From build step 5, each task occupies one step of its project's workflow at a time; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-h1e6jc (A task page shows its state and related work) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; Each task occupies one workflow step, still supplied by s-azfcx4: From build step 5, each task occupies one step of its project's workflow at a time; Tasks have code links, still supplied by s-1csktg: A task has code links; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views; step 6 retains code views and GitHub connector.
s-bxws89 (Project boards group task cards by step) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-nj99c5 (Runners serve only their registering person) needs lodge never handles Claude sign-in credentials, still supplied by s-ydkmyq: lodge never offers claude.ai sign-in, or collects, stores, or relays anyone's Claude credentials or session tokens; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-7zx39z (Runners keep an outbound WebSocket open) needs Runners serve only their registering person, still supplied by s-nj99c5: From build step 4, the runner belongs to its registering person and runs only sessions for tasks assigned to that person, under that person's own `claude` sign-in; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-awkdkw (A hand-over brief assembles the task context) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-dazqbj (Starting a session supplies its identity and agent) needs A hand-over brief assembles the task context, still supplied by s-awkdkw: From build step 2, the task's brief is one text read first by a session, containing its step, artefacts, decisions, and open threads; Runners serve only their registering person, still supplied by s-nj99c5: From build step 4, the runner belongs to its registering person and runs only sessions for tasks assigned to that person, under that person's own `claude` sign-in; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-xe5bmq (Cloud setup remains the environment owner's action) needs s-t8sj11, still supplied by s-t8sj11: the unchanged prerequisite; Secrets never go where other people can read them, still supplied by s-4w05xp: lodge never puts a secret where others can read it, including in a cloud environment's variables, in a repository, or in a URL; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-68vtrb (Manually started Claude Code sessions are talked to there) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage.
s-n242p0 (Sessions report their work through the API) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
