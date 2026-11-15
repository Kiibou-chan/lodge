---
id: d-k32haa
kind: decision
title: "Correct server import records: reaffirm prerequisite group 7"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-7aqvsh, action: edit}
  - {entry: s-gnn2ha, action: edit}
  - {entry: s-k570d9, action: edit}
  - {entry: s-wgkrmr, action: edit}
  - {entry: s-gyamm5, action: edit}
  - {entry: s-81kf9s, action: edit}
  - {entry: s-5tgnrn, action: edit}
  - {entry: s-6r0exg, action: edit}
  - {entry: s-tprwhs, action: edit}
  - {entry: s-d1dd20, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-7aqvsh (The interface distinguishes reported and checked states) needs Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-gnn2ha (Workflow progression can require checked evidence) needs Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself; A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-k570d9 (Task state is actionable in one interface) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-wgkrmr (Session outputs belong to the task and survive the session) needs Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-gyamm5 (New sessions start from the task context) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-81kf9s (Project workflows are adaptable data) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-5tgnrn (lodge starts or suggests sessions across execution locations) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-6r0exg (Other people use lodge alone or together) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing; A project holds members and their roles, still supplied by s-3y79d0: From build step 7, a project holds several members and their roles.
s-tprwhs (A workflow defines a project task's steps) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work; A project holds its workflow, still supplied by s-sge25h: From build step 5, a project holds its workflow.
s-d1dd20 (Tasks group work and allow one level of children) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
