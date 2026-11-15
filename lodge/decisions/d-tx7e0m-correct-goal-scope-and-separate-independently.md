---
id: d-tx7e0m
kind: decision
title: "Correct goal scope and separate independently looked-up server claims"
scope: product
decided_by: coordinator
date: 2026-11-15T05:26:12+01:00
changes:
  - {entry: s-c8hrye, action: edit}
  - {entry: s-fpxzb9, action: edit}
  - {entry: s-t4tbrj, action: create}
  - {entry: s-6r0exg, action: edit}
  - {entry: s-chycjf, action: edit}
  - {entry: s-wrksm5, action: create}
  - {entry: s-q6g68q, action: create}
  - {entry: s-nhx8zw, action: edit}
  - {entry: s-mnfeyz, action: create}
  - {entry: s-d56aky, action: create}
  - {entry: s-xy6qte, action: edit}
  - {entry: s-c0k9hx, action: edit}
  - {entry: s-dxmhjg, action: create}
  - {entry: s-pttahq, action: edit}
  - {entry: s-pw47pk, action: create}
  - {entry: s-d0tvr8, action: create}
  - {entry: s-73ee5k, action: edit}
  - {entry: s-r2cc8d, action: create}
  - {entry: s-1hecad, action: create}
  - {entry: s-0tn1e8, action: edit}
  - {entry: s-hke5m9, action: edit}
  - {entry: s-h1e6jc, action: edit}
narrows: [d-6x8fd9, d-ktz4rj, d-11yx0r, d-pfdqpp]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "0.2", handle: "pyproject.toml:3, project.version = \"0.2.0\""}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:297, Build order, item 2"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, Build order, item 3"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:300, Build order, item 5"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:301, Build order, item 6"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302, Build order, item 7"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:98, one workflow per kind of task; 109, one waiting list"}
---

Server goals retain local conversation context, independent claims have separate entries, and workflow and task-page wording follows the design's build order.

## Reasoning

Goals at design lines 21 to 30 do not assign a step to Talking with a session at lines 184 to 190.
Remove that sentence from s-c8hrye, retain its lodge 0.2 scope and instructions, and retain the server goal once in s-ts73yt; Talking belongs in sessions in Task 11c without a guessed step.
This narrows d-6x8fd9 for that imported claim, the waiting-list grouping, the other-people wording, and its incorrect lodge version handle; project.version above supplies the version evidence.
The independent workflow-kind and event-history choices at line 98 are separate [my call] claims.
Findings, threshold evaluation, and reported progression at lines 109 to 110 are independent lookups, all retaining their model dependencies and resting on the session-claim safeguard s-jqh7hf.
Workflow step tracking, session to-do reporting, and code references at line 169 split cleanly while retaining dependencies.
The default workflows at lines 116 to 165 name their steps and use continues for forward edges, reserving returns for failure edges.
These groupings and wording narrow d-11yx0r without changing workflow semantics.
Non-goals at lines 36 and 40 separate desktop scope, installability, shell eligibility, GitHub integration, host-independent git, and the deferred GitLab connector; only installability and GitHub code integration receive the build steps assigned at lines 298 and 301.
This narrows d-ktz4rj only for its combined claim groupings.
The task page at line 174 shows code from the code-views step at line 301, narrowing d-pfdqpp for its premature code presentation.
The plain apostrophe in s-xy6qte changes its title for consistent lookup, with its safeguard unchanged.
The workflow field entries move beside the other field entries in the area order.
The build-order entry and claimed-and-checked entry remain Task 11c's work.
The historical lodge 0.2 exclusions, thread semantics, evaluation condition, and server scope in s-7ah5n7 remain together for now because separating them would require a wider historical scope and dependency review.
No author decision is narrowed or replaced; all existing safeguards remain.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
