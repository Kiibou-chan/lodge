---
id: d-h3v99q
kind: decision
title: "Restrict viewer writes to trusted requests and record kinds"
scope: product
decided_by: coordinator
date: 2026-10-31T03:20:40+01:00
changes:
  - {entry: s-q42qd7, action: create}
  - {entry: s-704ssg, action: create}
  - {entry: s-rpn77e, action: create}
  - {entry: s-bet2rj, action: create}
  - {entry: s-nnp7y3, action: create}
  - {entry: s-nzhyh3, action: edit}
  - {entry: s-dm37qr, action: edit}
  - {entry: s-582qav, action: edit}
  - {entry: s-bty9z4, action: edit}
numbers:
  - {value: "124", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, line 124"}
  - {value: "132", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, line 132"}
---

Viewer writes require a startup token and an allowed origin and host, and write only author confirmations and threads.

## Reasoning

Design lines 124 to 132 make the writable viewer a trust boundary.
The coordinator adopts POST tokens, whole-header host matching, explicit reverse-proxy ports, required allowed origins, and the existing author-label trust of LODGE-2.
Browsers send Origin on POST, so its absence is refused.
Advisor d-7w5aq0 supplies constant-time token comparison and the restriction on record writes.
The viewer uses the shared application and Store paths: the layering statement of d-fkndvh remains true and needs no narrowing.
s-dm37qr and s-582qav already state the correct viewer writes after Task 9b; those edits are not repeated.
The origin and reachability claims require the allowed-host rule; the write-limit claim requires separate confirmations and append-only threads.
s-dm37qr still holds unchanged: ranked dependency rendering changes its displayed specification order, not its local operation, writes, or read features.
s-582qav still holds unchanged after reaffirming s-dm37qr: confirmations and threads remain the viewer writes, and other edits remain session work.
s-bty9z4 still holds unchanged after correcting s-nzhyh3: viewer writes still use the Store, and branch-mode commits and pushes remain the same.
Related feedback for d-m4ky49, d-6zyet3, and d-ejdyds is answered no: their reconciliation, eight checks, and reading-area dependency links still hold.
