---
id: d-xka649
kind: decision
title: "Correct server import records: reaffirm prerequisite group 2"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-2wqxmw, action: edit}
  - {entry: s-raw3fj, action: edit}
  - {entry: s-rx3eqg, action: edit}
  - {entry: s-s981gy, action: edit}
  - {entry: s-25m983, action: edit}
  - {entry: s-vg9y38, action: edit}
  - {entry: s-p6n0x6, action: edit}
  - {entry: s-sezq1z, action: edit}
  - {entry: s-x7sw4r, action: edit}
  - {entry: s-pjnxhg, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-2wqxmw (Import preserves attachment bytes) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine.
s-raw3fj (Waiting items show enough context to answer) needs A person has one waiting list across their projects, still supplied by s-paf12c: From build step 2, a person's waiting list spans every project they belong to: thread questions, session questions, steps waiting on a go, and agent decisions waiting for confirmation; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-rx3eqg (Waiting answers return as messages to the asking session) needs A person has one waiting list across their projects, still supplied by s-paf12c: From build step 2, a person's waiting list spans every project they belong to: thread questions, session questions, steps waiting on a go, and agent decisions waiting for confirmation; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-s981gy (New waiting items can raise push notifications) needs A person has one waiting list across their projects, still supplied by s-paf12c: From build step 2, a person's waiting list spans every project they belong to: thread questions, session questions, steps waiting on a go, and agent decisions waiting for confirmation.
s-25m983 (Local session messages are relayed both ways) needs Sessions lodge starts are talked to in their task or artefact thread, still supplied by s-anc255: A session lodge starts is talked to inside lodge, in the thread of its task or artefact.
s-vg9y38 (Cloud replies appear through session stop reports) needs Sessions lodge starts are talked to in their task or artefact thread, still supplied by s-anc255: A session lodge starts is talked to inside lodge, in the thread of its task or artefact.
s-p6n0x6 (MCP exposes the same operations to local sessions only) needs The lodge command talks to the server, still supplied by s-zjdzre: The `lodge` command talks to the server.
s-sezq1z (People join projects through invitation links) needs A person signs in with passkeys, still supplied by s-c0bd0b: A person signs in with passkeys and belongs to projects; A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
s-x7sw4r (Owners decide confirm authorise merges and change workflows) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; A person approves decisions drafted in their name, still supplied by s-yenn11: A person's decision is written only through that person; s-xy6qte, still supplied by s-xy6qte: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
s-pjnxhg (Members work on tasks answer questions and raise doubts) needs A project groups records settings and its owner, still supplied by s-g8m3qv: A project groups its records, settings, and owner; The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
