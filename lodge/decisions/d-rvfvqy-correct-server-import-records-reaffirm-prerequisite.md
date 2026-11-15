---
id: d-rvfvqy
kind: decision
title: "Correct server import records: reaffirm prerequisite group 3"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-bk3f8p, action: edit}
  - {entry: s-g8m3qv, action: edit}
  - {entry: s-mn4xj9, action: edit}
  - {entry: s-sge25h, action: edit}
  - {entry: s-ts16f0, action: edit}
  - {entry: s-3y79d0, action: edit}
  - {entry: s-07ar34, action: edit}
  - {entry: s-fpxzb9, action: edit}
  - {entry: s-t4tbrj, action: edit}
  - {entry: s-cg69z0, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, build order item 1; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, build order item 6; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "0.2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, command parity with lodge 0.2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:284, file layout; docs/superpowers/specs/2026-11-02-lodge-server-design.md:289, imported store"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-bk3f8p (Registering a machine issues its runner token) needs A person signs in with passkeys, still supplied by s-c0bd0b: A person signs in with passkeys and belongs to projects.
s-g8m3qv (A project groups records settings and its owner) needs s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: the ordered core, tasks, interface, runner, workflow, code, and multi-person phases remain intact.
s-mn4xj9 (A project holds its export target) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite.
s-sge25h (A project holds its workflow) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work.
s-ts16f0 (Project code views link its repositories) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-3y79d0 (A project holds members and their roles) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
s-07ar34 (lodge 0.2 is serverless and the server exists) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 1 retains core, records, API, command, import, and export.
s-fpxzb9 (Open session questions share a waiting list) needs Waiting items ask a person for an answer or go, still supplied by s-nfgv2t: From build step 2, a waiting item is a question waiting on a person from a thread or session; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-t4tbrj (The waiting list is answerable from a phone) needs Waiting items ask a person for an answer or go, still supplied by s-nfgv2t: From build step 2, a waiting item is a question waiting on a person from a thread or session; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-cg69z0 (Session reports are shown apart from checked facts) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 5 retains workflow, claimed and checked, usage, and stuck work; Session steps start as reported and need independent confirmation, still supplied by s-4na883: From build step 5, a step a session reports is shown as reported; lodge marks it checked only when it has confirmed it itself.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
