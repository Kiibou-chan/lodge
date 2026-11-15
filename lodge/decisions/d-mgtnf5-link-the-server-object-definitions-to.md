---
id: d-mgtnf5
kind: decision
title: "Link the server object definitions to what they require"
scope: product
decided_by: coordinator
date: 2026-11-15T04:48:29+01:00
changes:
  - {entry: s-8v6ek2, action: link}
  - {entry: s-cf0qph, action: link}
  - {entry: s-nfgv2t, action: link}
  - {entry: s-g8m3qv, action: link}
---

The server object definitions name the entries they require.

## Reasoning

Sessions and artefacts require tasks, waiting items require a person, and a server project requires its event store.
These links complete dependencies in the model without changing any entry statement.
The coordinator permits this additional link-only decision after the section decisions.
No: d-sk1r7r still states the model, d-j3z85y still schedules its recording after the build, and d-rn4qzq still governs sign-in settings and lifetimes.
None is replaced or narrowed; this decision only supplies omitted dependency links.
