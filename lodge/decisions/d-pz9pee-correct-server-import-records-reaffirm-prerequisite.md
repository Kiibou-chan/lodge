---
id: d-pz9pee
kind: decision
title: "Correct server import records: reaffirm prerequisite group 5"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-b6jxhr, action: edit}
  - {entry: s-txrm4h, action: edit}
  - {entry: s-s5fa8n, action: edit}
  - {entry: s-paf12c, action: edit}
  - {entry: s-w37qbc, action: edit}
  - {entry: s-r2k5t2, action: edit}
  - {entry: s-myvb3j, action: edit}
  - {entry: s-zjdzre, action: edit}
  - {entry: s-8ysrep, action: edit}
  - {entry: s-kagv3e, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "0.2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, command parity with lodge 0.2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:284, file layout; docs/superpowers/specs/2026-11-02-lodge-server-design.md:289, imported store"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-b6jxhr (Export names the person who decided or wrote) needs A decision names its deciding person or agent role, still supplied by s-ava922: On the server, `decided_by` names a person or an agent role; s-f6eaj1, still supplied by s-f6eaj1: the unchanged prerequisite.
s-txrm4h (The owner imports a store into an empty project) needs s-z1zvb4, still supplied by s-z1zvb4: the unchanged prerequisite; A decision names its deciding person or agent role, still supplied by s-ava922: On the server, `decided_by` names a person or an agent role.
s-s5fa8n (The full interface interaction for draft approval remains open) needs A person approves decisions drafted in their name, still supplied by s-yenn11: A person's decision is written only through that person.
s-paf12c (A person has one waiting list across their projects) needs Waiting items ask a person for an answer or go, still supplied by s-nfgv2t: From build step 2, a waiting item is a question waiting on a person from a thread or session; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-w37qbc (The waiting list is the phone's first screen) needs A person has one waiting list across their projects, still supplied by s-paf12c: From build step 2, a person's waiting list spans every project they belong to: thread questions, session questions, steps waiting on a go, and agent decisions waiting for confirmation; The waiting list is answerable from a phone, still supplied by s-t4tbrj: From build step 3, the waiting list is answerable from a phone.
s-r2k5t2 (An offline assignee runner creates a waiting item) needs Waiting items ask a person for an answer or go, still supplied by s-nfgv2t: From build step 2, a waiting item is a question waiting on a person from a thread or session; Runners serve only their registering person, still supplied by s-nj99c5: From build step 4, the runner belongs to its registering person and runs only sessions for tasks assigned to that person, under that person's own `claude` sign-in; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-myvb3j (Cloud sessions start and receive follow-ups through claude) needs The cloud runner supplies a pseudo-terminal, still supplied by s-7cseam: From build step 4, the runner supplies a pseudo-terminal to `claude --cloud`, which needs a terminal; Starting a session supplies its identity and agent, still supplied by s-dazqbj: From build step 4, the server asks a runner to start a session with the task brief, a session ID, a local session's project-and-task-scoped token, and the agent: Claude Code, Codex, or a cloud session; The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-zjdzre (The lodge command talks to the server) needs lodge 0.2 is serverless and the server exists, still supplied by s-07ar34: lodge 0.2 has no server and no MCP server, as settled by d-14vk9b.
s-8ysrep (The browser has a waiting-list view) needs A person has one waiting list across their projects, still supplied by s-paf12c: From build step 2, a person's waiting list spans every project they belong to: thread questions, session questions, steps waiting on a go, and agent decisions waiting for confirmation; The browser app uses the agents' API, still supplied by s-ksg593: From build step 3, the browser app uses the same API as the agents; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-kagv3e (Artefacts live on their task through API uploads) needs Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
