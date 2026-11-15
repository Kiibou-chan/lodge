---
id: d-hn1wjb
kind: decision
title: "Correct server import records: reaffirm prerequisite group 8"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-8v6ek2, action: edit}
  - {entry: s-cf0qph, action: edit}
  - {entry: s-azfcx4, action: edit}
  - {entry: s-c0k9hx, action: edit}
  - {entry: s-dxmhjg, action: edit}
  - {entry: s-xqza9k, action: edit}
  - {entry: s-3ysqhz, action: edit}
  - {entry: s-hmj4mc, action: edit}
  - {entry: s-mrnqdh, action: edit}
  - {entry: s-krdpxq, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-8v6ek2 (A session reports agent work on a task) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list; step 4 retains runner and session starts; step 5 retains workflow, claimed and checked, usage, and stuck work.
s-cf0qph (Artefact uploads are versioned task attachments) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-azfcx4 (Each task occupies one workflow step) needs Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-c0k9hx (A project has a workflow per task kind) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-dxmhjg (Workflow changes retain who changed what and when) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-xqza9k (Workflow steps name their actors) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-3ysqhz (Workflow steps declare progression conditions) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-hmj4mc (Workflow steps specify how sessions start) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-mrnqdh (Workflow steps name execution locations) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-krdpxq (Workflow steps declare artefact inputs and outputs) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
