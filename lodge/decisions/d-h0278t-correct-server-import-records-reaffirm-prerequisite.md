---
id: d-h0278t
kind: decision
title: "Correct server import records: reaffirm prerequisite group 9"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-68mfam, action: edit}
  - {entry: s-an745k, action: edit}
  - {entry: s-pttahq, action: edit}
  - {entry: s-pw47pk, action: edit}
  - {entry: s-d0tvr8, action: edit}
  - {entry: s-h48a8n, action: edit}
  - {entry: s-0tn1e8, action: edit}
  - {entry: s-hke5m9, action: edit}
  - {entry: s-73ee5k, action: edit}
  - {entry: s-r2cc8d, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "third", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:248, third fix round; docs/superpowers/specs/2026-11-02-lodge-server-design.md:111, what a fix round counts"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-68mfam (Workflow failures follow named back-edges) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-an745k (Workflow checklists expose omissions) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-pttahq (Reviews report findings with severity) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; A session claim never appears as a checked fact, still supplied by s-jqh7hf: lodge never shows a session's claim as a checked fact; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-pw47pk (Progression thresholds read review findings) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; A session claim never appears as a checked fact, still supplied by s-jqh7hf: lodge never shows a session's claim as a checked fact; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-d0tvr8 (Session-driven review moves remain reported) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; A session claim never appears as a checked fact, still supplied by s-jqh7hf: lodge never shows a session's claim as a checked fact; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-h48a8n (A fix round counts entry into a fix step) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-0tn1e8 (The default plan workflow runs from mock to authorised merge) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The planner creates children and the parent waits, still supplied by s-h4x7bx: The planner session creates child tasks through the API from the plan; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-hke5m9 (The default child task workflow builds reviews and rechecks) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-73ee5k (Lodge tracks the workflow step of each task) needs Each task occupies one workflow step, still supplied by s-azfcx4: From build step 5, each task occupies one step of its project's workflow at a time; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-r2cc8d (Session to-do reports sit under the workflow step) needs Each task occupies one workflow step, still supplied by s-azfcx4: From build step 5, each task occupies one step of its project's workflow at a time; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
