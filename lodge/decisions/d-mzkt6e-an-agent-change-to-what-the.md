---
id: d-mzkt6e
kind: decision
title: "An agent change to what the author decided raises a derived review flag"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:19+01:00
changes:
  - {entry: s-01k42c, action: create}
  - {entry: s-0s9m2d, action: create}
  - {entry: s-dfejrb, action: create}
  - {entry: s-j5ttw1, action: create}
---

An agent decision that replaces or narrows an author decision, or changes an entry whose last change was an author decision, is flagged as awaiting the author.
The flag is derived, shown at Level 1, and cleared by an author decision.

## Reasoning

The flag answers the must-not that an agent must not quietly rewrite what the author decided (d-9k0dfe); the flag and its rule are the specification author's call, marked in the design document for the author to check; it is derived rather than typed so that it cannot be forgotten.

A decision she confirmed counts as hers for the flag (LODGE-6, d-8nkamy), chosen over flagging only decisions she wrote.

The agent decision takes effect at once, as flagged rulings do in the first user today, so work does not stall overnight.

When an author decision replaces an agent decision whose entry edits still stand, feedback asks whether it edits those entries back, because a replacement does not undo the edits (LODGE-7, d-wc6bah).

lodge trusts `decided_by: author` as written (LODGE-2, d-qsfjqa), chosen over requiring her confirmation somewhere an agent cannot reach; the required quote makes a wrong attribution visible, and the pilot's random sample checks attributions.
