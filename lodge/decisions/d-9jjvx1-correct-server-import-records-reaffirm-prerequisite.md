---
id: d-9jjvx1
kind: decision
title: "Correct server import records: reaffirm prerequisite group 11"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-a62w0p, action: edit}
  - {entry: s-c0zke5, action: edit}
  - {entry: s-a2y9t3, action: edit}
  - {entry: s-pammwd, action: edit}
  - {entry: s-n4pdfq, action: edit}
  - {entry: s-dv5e12, action: edit}
  - {entry: s-40yykh, action: edit}
  - {entry: s-42kzcz, action: edit}
  - {entry: s-1k9wbc, action: edit}
  - {entry: s-18jj1r, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, build order item 6; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-a62w0p (Lodge does not read Claude Code session state) remains the independent claim stated at docs/superpowers/specs/2026-11-02-lodge-server-design.md; it has no changed prerequisite.
s-c0zke5 (Claude Code hooks report heartbeat status and usage) needs Sessions report their work through the API, still supplied by s-n242p0: From build step 2, a session reports its steps and their state, status, artefacts, questions, and usage through the API; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-a2y9t3 (Unreadable cloud transcripts leave usage unknown) needs Claude Code hooks report heartbeat status and usage, still supplied by s-c0zke5: From build step 2, lodge ships Claude Code hooks that report a heartbeat after each tool call, status at each stop, and usage from the session's own transcript, without requiring the agent to report most of it; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-pammwd (A repository mailbox carries calls without network access) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage.
s-n4pdfq (Mailbox authority is push access and a known session ID) needs A repository mailbox carries calls without network access, still supplied by s-pammwd: For a session without network access to lodge, a mailbox branch in the project's repository carries messages.
s-dv5e12 (Code stays in git) remains the independent claim stated at docs/superpowers/specs/2026-11-02-lodge-server-design.md; it has no changed prerequisite.
s-40yykh (Lodge reads code from a clone on any host) needs Code stays in git, still supplied by s-dv5e12: Code stays in git; s-mnfeyz, still supplied by s-mnfeyz: the unchanged prerequisite; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-42kzcz (Decision IDs link commits and decisions both ways) needs Code stays in git, still supplied by s-dv5e12: Code stays in git; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-1k9wbc (A task exposes its branches and diff) needs Lodge reads code from a clone on any host, still supplied by s-40yykh: From build step 6, lodge keeps a clone of each project repository and reads branches, commits, merges, and diffs from it, on any host; Tasks group work and allow one level of children, still supplied by s-d1dd20: From build step 2, a task is a unit of work in a project with its assignee, threads, artefacts, sessions, and decisions; a plan and each task of a plan are tasks; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-18jj1r (A task can start a session on its branch) needs A task exposes its branches and diff, still supplied by s-1k9wbc: From build step 6, a task exposes its branches and diff; A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage; The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
