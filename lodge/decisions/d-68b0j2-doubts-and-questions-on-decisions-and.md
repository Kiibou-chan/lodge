---
id: d-68b0j2
kind: decision
title: "Doubts and questions on decisions and entries"
scope: product
decided_by: coordinator
date: 2026-10-31T03:14:52+01:00
changes:
  - {entry: s-yj4r17, action: create}
  - {entry: s-ejjpek, action: create}
  - {entry: s-4wna3s, action: create}
  - {entry: s-77krr7, action: create}
  - {entry: s-nda0br, action: create}
  - {entry: s-r7c3wn, action: create}
  - {entry: s-nxakwv, action: create}
  - {entry: s-3e6zp3, action: create}
  - {entry: s-a67fqm, action: edit}
  - {entry: s-evv024, action: edit}
  - {entry: s-0s9m2d, action: edit}
  - {entry: s-ms14fq, action: edit}
  - {entry: s-wcv4en, action: edit}
  - {entry: s-7ah5n7, action: edit}
numbers:
  - {value: "78", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, Doubts and questions and Rests on"}
  - {value: "5", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, Doubts and questions and Rests on"}
  - {value: "1", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, Doubts and questions and Rests on"}
---

Threads record append-only doubts and questions on decisions or entries, with verbatim author messages, separate waiting groups, visible marks, and decisions for resulting changes.

## Reasoning

The built thread behaviour extends the author's entry-focused words in d-9dqycj to decisions too, following d-7w5aq0 and design line 78.
The s-7ah5n7 edit follows d-a3h9f3 and d-9dqycj: a thread holds no claim of its own and settlements enter as decisions.
The closing-message entry follows d-a3h9f3: an empty closing text preserves who closed it without inventing author words.
For the advisor claims, d-7w5aq0 supplies decision-or-entry targets, check 5 immutability, author-message time provenance, the two waiting groups, the search boundary, and checks 1 and 5 for threads.
Thread storage, append-only messages, agent thread commands, viewer provenance, decision-doubt propagation, and acting through decisions are coordinator calls.
The other related decisions stay current; none is superseded.

Messages are never edited, so a thread records what was said rather than a revised account.
A doubt on a decision must show on the specification because the author reads there; marking only the decision would hide the doubt from that read.
