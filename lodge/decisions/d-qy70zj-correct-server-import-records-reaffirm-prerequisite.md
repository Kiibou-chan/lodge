---
id: d-qy70zj
kind: decision
title: "Correct server import records: reaffirm prerequisite group 4"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-wrksm5, action: edit}
  - {entry: s-a4jfp1, action: edit}
  - {entry: s-gcwv38, action: edit}
  - {entry: s-7cseam, action: edit}
  - {entry: s-51ab7j, action: edit}
  - {entry: s-ava922, action: edit}
  - {entry: s-yenn11, action: edit}
  - {entry: s-nfgv2t, action: edit}
  - {entry: s-ksg593, action: edit}
  - {entry: s-3xkj85, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "0.2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, command parity with lodge 0.2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:284, file layout; docs/superpowers/specs/2026-11-02-lodge-server-design.md:289, imported store"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-wrksm5 (The browser app installs on phones and computers) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-a4jfp1 (Python lodge and the TypeScript server) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-gcwv38 (The full interface uses Preact and signals) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-7cseam (The cloud runner supplies a pseudo-terminal) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-51ab7j (Cloud identity comes from a checked session ID) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 4 retains runner and session starts.
s-ava922 (A decision names its deciding person or agent role) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 7 retains several people, invitations, roles, and sharing.
s-yenn11 (A person approves decisions drafted in their name) needs A decision names its deciding person or agent role, still supplied by s-ava922: On the server, `decided_by` names a person or an agent role; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list.
s-nfgv2t (Waiting items ask a person for an answer or go) needs A person signs in with passkeys, still supplied by s-c0bd0b: A person signs in with passkeys and belongs to projects; The server build follows seven ordered steps, still supplied by s-pks1qn: step 2 retains tasks, reporting, artefacts, briefs, and waiting list; step 5 retains workflow, claimed and checked, usage, and stuck work.
s-ksg593 (The browser app uses the agents' API) needs The browser app installs on phones and computers, still supplied by s-wrksm5: From build step 3, the browser app installs on a phone and a computer; The full interface uses Preact and signals, still supplied by s-gcwv38: From build step 3, the interface uses Preact with `@preact/signals`, built with plain `tsc` and esbuild; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-3xkj85 (Phone use supports practical work except long diff reading) needs The browser app installs on phones and computers, still supplied by s-wrksm5: From build step 3, the browser app installs on a phone and a computer; The waiting list is answerable from a phone, still supplied by s-t4tbrj: From build step 3, the waiting list is answerable from a phone.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
