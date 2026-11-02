---
id: d-jtxwg3
kind: decision
title: "The third plan serves a minimal page for passkeys, agent tokens, and approvals"
scope: process
decided_by: planner
date: 2026-11-02T14:51:02+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 3"}
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 7"}
  - {value: "2", handle: "lodge show SRV-2"}
---

The third plan's `api` serves one minimal page, plain HTML with a small script and no framework, where the one person registers a passkey with the setup code, signs in, issues and revokes agent tokens, and approves decisions drafted in their name; the interface of step 3 replaces it.
Its server side is tested through the handler with the software authenticator, and the coordinator goes through it once in a real browser before the third plan merges.

## Reasoning

Build step 1 owns passkeys for one person (design, "Build order", item 1 and the sentence after item 7), and without a page nobody can register, sign in, or issue the first agent token after the third plan, so the command cannot reach the server outside the tests (`plan-review-practice.md`, P-I11).
A passkey is created and used only through `navigator.credentials` in a page whose origin matches the relying party (W3C Web Authentication, section "Create a New Credential"), so a command on the server's machine cannot register one.
A person's drafted decision becomes current only when that person approves it, since a signed-in person is a place an agent cannot reach (design, "The model", SRV-2); an approval through a command on the server's machine, where an agent may run, would not enforce that.
The third plan builds `api`, the passkeys, and the tokens; the second plan ends with no HTTP, and the fourth is the importer and the export, so the page belongs to the third.
How approving works in the interface is open for a later point (design, "Open"), so the page's approval is a list and a button, and its design is left to step 3.
Cost if wrong: one page and its tests thrown away when step 3's interface arrives.
