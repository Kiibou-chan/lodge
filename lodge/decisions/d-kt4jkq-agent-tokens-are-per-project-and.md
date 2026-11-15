---
id: d-kt4jkq
kind: decision
title: "Agent tokens are per project and issued by the person, whose operations need the person's session"
scope: process
decided_by: planner
date: 2026-11-02T19:16:28+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "256", handle: "SHA-256, FIPS 180-4"}
  - {value: "262", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, line 262"}
  - {value: "76", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, line 76"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Must nots, item 6"}
---

An agent token is issued by the signed-in person for one project's name, with an optional agent role its requests act as, shown once, stored as its SHA-256, and revocable; it may create that project and call every operation on it but the person's.
Listing, approving, and declining held adds, confirming, issuing, revoking, and listing tokens, and listing projects, answer only the person's session cookie sent with the server's own origin; sessions and setup codes are stored as hashes too.

## Reasoning

The design scopes a session's token to its project (design line 262), and a cloud environment holds a project token (design, "Constraints"); a token issued for a project's name lets `lodge init` create that project with it, so no other way to create projects is needed.
A person's decision becomes current only when that person approves it (SRV-2, d-zzfmj2), since "a signed-in person is a place an agent cannot reach" (design line 76); an agent holding a token could otherwise approve or confirm in the person's name.
The role makes the token's requests `agent(role)` in `app` (d-kj59bz), so `decided_by` of a role and a person's hold (d-znagqe) see the same actor the token names.
d-yayhct has the token "stored hashed, and revocable", and must-not 6 keeps secrets where others cannot read them (design, "Must nots").
A browser sends a cookie with a page's request to the server; `SameSite=Strict` keeps it off requests from other sites, and an `Origin` that is not the server's own refuses a request from another page that gets through.
Cost if wrong: a later need for one token over several projects turns the project into a list on the token; one field and its check in `api/auth.ts`.
