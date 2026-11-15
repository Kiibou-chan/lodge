---
id: d-nrh0nv
kind: decision
title: "Correct server import records: reaffirm prerequisite group 6"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-m7w8c0, action: edit}
  - {entry: s-bd0qv5, action: edit}
  - {entry: s-xakcm0, action: edit}
  - {entry: s-er4t45, action: edit}
  - {entry: s-z0zk7y, action: edit}
  - {entry: s-gwppsf, action: edit}
  - {entry: s-4na883, action: edit}
  - {entry: s-ecj6se, action: edit}
  - {entry: s-j1bvy2, action: edit}
  - {entry: s-4p2vsz, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-m7w8c0 (Images and PDFs display inline) needs Artefacts live on their task through API uploads, still supplied by s-kagv3e: From build step 2, an artefact is uploaded to its task through the API; a session's folder is never its home; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-bd0qv5 (HTML mocks display in a sandbox without lodge origin access) needs Artefacts live on their task through API uploads, still supplied by s-kagv3e: From build step 2, an artefact is uploaded to its task through the API; a session's folder is never its home; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-xakcm0 (Each artefact has its own thread) needs Artefacts live on their task through API uploads, still supplied by s-kagv3e: From build step 2, an artefact is uploaded to its task through the API; a session's folder is never its home; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-er4t45 (Mocks remain after their task finishes) needs Artefacts live on their task through API uploads, still supplied by s-kagv3e: From build step 2, an artefact is uploaded to its task through the API; a session's folder is never its home; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-z0zk7y (The built task links to its source mock) needs Mocks remain after their task finishes, still supplied by s-er4t45: From build step 2, a mock remains after the task it fed is done, preserving what may have been missed and why work was done that way; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-gwppsf (An outside opinion link reveals only the artefact and thread) needs Each artefact has its own thread, still supplied by s-xakcm0: From build step 2, an artefact has its own thread, keeping mock discussion apart from coordination; Secrets never go where other people can read them, still supplied by s-4w05xp: lodge never puts a secret where others can read it, including in a cloud environment's variables, in a repository, or in a URL; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
s-4na883 (Session steps start as reported and need independent confirmation) needs A session claim never appears as a checked fact, still supplied by s-jqh7hf: lodge never shows a session's claim as a checked fact; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-ecj6se (Lodge checks that a named commit or branch exists) needs Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-j1bvy2 (Lodge checks whether a branch is merged) needs Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-4p2vsz (Gate confirmation reruns the gate on the named commit) needs Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
