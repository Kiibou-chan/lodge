---
id: d-1x1mgv
kind: decision
title: "Writes go through lodge, and feedback advises without refusing"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:19+01:00
changes:
  - {entry: s-8m99ba, action: create}
  - {entry: s-bjhnwg, action: create}
  - {entry: s-hfjr1m, action: create}
  - {entry: s-aagqv8, action: create}
---

All writing goes through lodge, a decision and the entries it changes together.
Feedback at write time advises and does not refuse; a failing check still refuses the add.
The feedback covers length, related decisions, numbers without a handle, and a coming review flag.

## Reasoning

Writing through lodge, never by hand, is how every change to the specification comes to name the decision behind it.

Feedback rather than refusal at write time was settled with the author as the guardrail style (`docs/superpowers/specs/2026-10-29-lodge-design.md:148`); her words on guardrails are in d-c6n1ng. A failing check still refuses the add (LODGE-9, d-qbfdqt), as d-4032xv describes.

The feedback asks when a decision that changes nothing, replaces nothing, and narrows nothing sits among related current decisions.

The check on digits without a `numbers` handle was the specification author's call, so that figures can be traced.

The note that an agent decision will raise a review flag comes at write time, when the draft can still change.
