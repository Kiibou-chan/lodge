---
id: d-yayhct
kind: decision
title: "Passkeys through @simplewebauthn/server, tested with a software authenticator"
scope: process
decided_by: planner
date: 2026-11-02T14:10:37+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "1", handle: "design, Build order, item 1"}
  - {value: "14.0.3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 2"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md, item 2"}
---

The one person registers a passkey with a one-time setup code the server prints when it is set up, and signs in with it to a session cookie; the server verifies with @simplewebauthn/server, and the tests play the browser with a software authenticator, so no test needs a browser.

## Reasoning

The design leaves the passkey library to the builder (design, "Left to the builder") and wants passkeys in step 1 for one person (design, "Build order", last paragraph).
@simplewebauthn/server 14.0.3 verified a registration and a sign-in made by an ES256 key from WebCrypto, with attestation `none`, and refused a wrong challenge, under `bun test` (probe 2, `probes/tests/passkey.test.ts`).
Before any passkey exists nothing can sign in, so the first registration needs another proof; a code printed once on the server's own machine proves the person can reach that machine, and is spent on use.
A passkey is bound to the server's public name, so that name is a setting fixed before the first registration.
Cost if wrong: another library behind the same two operations, register and sign in, in `api`.
