---
id: d-rn4qzq
kind: decision
title: "Sign-in fixes origin and person at setup, requires user verification, and keeps sessions thirty days"
scope: process
decided_by: planner
date: 2026-11-02T19:16:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, probe 2"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, probe 2"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Goals, item 5"}
---

The server's origin and the person's name are fixed by the first `lodge server setup`; passkeys are created and used with user verification required; a session lasts thirty days; a ceremony's challenge lives in the server's memory for five minutes and is spent on use.

## Reasoning

A passkey is bound to the relying party's ID, the host of the origin, which d-yayhct fixes "before the first registration"; WebAuthn needs a secure context, and `http://localhost` is one (W3C Secure Contexts, "Is origin potentially trustworthy?"), so the coordinator's browser check can run on one machine.
A passkey is the only factor, and user verification is what makes it more than something held (W3C Web Authentication, "User Verification"); the software authenticator sets the flag (plan 1, probe 2: flags `0x45` and `0x05`).
The person reads the waiting list on a phone (design, goal 5), so a session long enough not to ask every day serves; one ends at once on sign-out.
A challenge serves one ceremony, so a server restart that loses the pending ones costs one retry.
Cost if wrong: a constant in `api/session.ts` or `api/passkeys.ts`.
