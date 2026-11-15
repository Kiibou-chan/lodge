---
id: d-z8h78d
kind: decision
title: "Correct server import records after Task 11c review"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-bnnw4m, action: retire}
  - {entry: s-5wysdb, action: retire}
  - {entry: s-5wysdb, action: edit}
  - {entry: s-t7wqxn, action: edit}
  - {entry: s-nhx8zw, action: edit}
  - {entry: s-c0bd0b, action: edit}
  - {entry: s-5cs27z, action: retire}
  - {entry: s-anc255, action: edit}
  - {entry: s-pks1qn, action: edit}
  - {entry: s-fe4kyr, action: edit}
  - {entry: s-5246t5, action: create}
  - {entry: s-d9v0m2, action: create}
  - {entry: s-7vpsy0, action: create}
narrows: [d-2zsf4a, d-4wrzdf, d-5ma843, d-78efj7, d-79gjg2, d-98fmhx, d-9cr8e6, d-d816nz, d-k65afn, d-k7z7ns, d-m5mwcm, d-nqxsax, d-pcxpyq, d-rgta90, d-shgdb0, d-tan3tb, d-vsd6q2, d-z5yvk7]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, build order item 1; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, build order item 2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:299, build order item 4; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, build order item 5; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, build order item 6; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, build order item 7; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
  - {value: "0.2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296, command parity with lodge 0.2; docs/superpowers/specs/2026-11-02-lodge-server-design.md:284, file layout; docs/superpowers/specs/2026-11-02-lodge-server-design.md:289, imported store"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304, one person; docs/superpowers/specs/2026-11-02-lodge-server-design.md:314, one API; docs/superpowers/specs/2026-11-02-lodge-server-design.md:175, one column per step; docs/superpowers/specs/2026-11-02-lodge-server-design.md:187, one brief text; docs/superpowers/specs/2026-11-02-lodge-server-design.md:224, one step from result; docs/superpowers/specs/2026-11-02-lodge-server-design.md:229, one waiting list"}
---

Withdraw repeated claims, separate session and credential claims, and retain the open workflow, mailbox, and interface choices because the design delegates those choices within its specified views.
Preserve settled libraries and one shared API, and record concrete prerequisites, number sources, and the work item for the corrected section decisions.

## Reasoning

Coordinator ruling for fix round 1 confirms withdrawal of the board and task-page twins because s-bxws89 and s-h1e6jc already carry those claims, including code at step 6.
s-nhx8zw now holds the GitHub reading capability; s-5cs27z is retired.
s-9sjp9z needs task branch access in s-1k9wbc and the permission constraint in s-xy6qte: task merge capability and main-branch authorisation are distinct claims.
s-8ysrep needs s-paf12c for waiting-list content, while its step-3 browser view is distinct from the step-2 list.
Only s-c0bd0b states the single-person period and passkeys in step 1, because the server is reachable beyond one machine from the first Funnel (design:304).
d-98fmhx is narrowed for that placement; the ordered build list, including design:294 to 302, stays in s-pks1qn.
d-wc9wt2 remains the authority for talking inside lodge (design:196-197); design:201 supplies the viewer exclusion and security claims, now separately findable.
design:262 supplies the separate local-token and cloud-token claims.
d-zzfmj2 defers the detailed approval interaction (design:308); lodge show d-jtxwg3 --reasoning documents the temporary approval page and expressly leaves its design to the full interface.
s-s5fa8n therefore remains open; the review handle d-s5fa8n is a typo for that entry, not an existing decision.
s-fe4kyr retains the open workflow syntax, mailbox layout, and board and task-page appearance because the design delegates those choices within its specified views (design:313-317).
d-sry12f settles JSON HTTP within one shared API, d-yayhct settles the passkey library, and d-4k9wcr settles Kysely; s-165qfh holds the dependency checker.
The corrections carry the work item missing in d-k7z7ns, d-78efj7, and d-2zsf4a, and replace decorative number handles with the exact design lines carrying quantities.
M9 remains decision history in d-98fmhx: the author agreed session features first; no additional specification claim is created.
Only the listed coordinator decisions are narrowed, for these corrections; all their other section reasons and claims remain in force. No author decision is narrowed or replaced.
s-t7wqxn (Local session tokens end with the session) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage.
s-nhx8zw (Pull request and CI integration starts with GitHub) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 6 retains code views and GitHub connector.
s-c0bd0b (A person signs in with passkeys) needs The server build follows seven ordered steps, still supplied by s-pks1qn: step 1 retains core, records, API, command, import, and export; step 7 retains several people, invitations, roles, and sharing.
s-anc255 (Sessions lodge starts are talked to in their task or artefact thread) needs A session reports agent work on a task, still supplied by s-8v6ek2: From build step 2, a session represents one agent session working on a task, with its status, reported steps, and reported usage.
s-pks1qn (The server build follows seven ordered steps) remains the independent claim stated at docs/superpowers/specs/2026-11-02-lodge-server-design.md; it has no changed prerequisite.
s-fe4kyr (Builder choices include workflow syntax, mailbox layout, and interface layout) needs Structure tests enforce Python and TypeScript boundaries, still supplied by s-165qfh: For lodge 0.2 in Python, the structure test uses the standard library's `ast` to enforce the allowed-imports table, no module cycles, cross-package imports through front doors, and modules of at most 300 lines; it forbids clock and randomness calls in `core` and `app`, and confines `os`, `subprocess`, and `open` I/O calls to the permitted I/O modules; s-sb9gee, still supplied by s-sb9gee: the unchanged prerequisite; The default plan workflow runs from mock to authorised merge, still supplied by s-0tn1e8: From build step 5, the default `plan` workflow follows lodge's build process with mocking before planning.
s-5246t5 (The server lifts the viewer exclusion of live agent chat) needs Sessions lodge starts are talked to in their task or artefact thread, still supplied by s-anc255: A session lodge starts is talked to inside lodge, in the thread of its task or artefact.
s-d9v0m2 (Talking to sessions relies on sign-in and session tokens) needs Sessions lodge starts are talked to in their task or artefact thread, still supplied by s-anc255: A session lodge starts is talked to inside lodge, in the thread of its task or artefact; A person signs in with passkeys, still supplied by s-c0bd0b: A person signs in with passkeys and belongs to projects; Local session tokens end with the session, still supplied by s-t7wqxn: Each local session gets its own token, scoped to its project and task and revoked when the session ends; Cloud sessions share their environment project token, still supplied by s-7vpsy0: Cloud sessions share their environment's project token.
s-7vpsy0 (Cloud sessions share their environment project token) needs Secrets never go where other people can read them, still supplied by s-4w05xp: lodge never puts a secret where others can read it, including in a cloud environment's variables, in a repository, or in a URL.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
