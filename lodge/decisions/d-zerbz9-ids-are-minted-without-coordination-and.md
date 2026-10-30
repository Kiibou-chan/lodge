---
id: d-zerbz9
kind: decision
title: "IDs are minted without coordination, and links are stored one way"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:17+01:00
changes:
  - {entry: s-fdzcr2, action: create}
  - {entry: s-8f6scf, action: create}
---

An ID is a type prefix and six random characters, minted without coordination, and a record may carry a human code.
Links are written on the decision only; lodge derives and shows the reverse direction.

## Reasoning

Identifiers are random so that sessions mint them without coordination and never reuse one.

The form of an ID, and storing links on the decision only, are the specification author's calls, marked in the design document for the author to check.

A code such as ITEM-1 is carried as well, unique and checked, because the author and the sessions quote codes in conversation and search must find a record by one.

The agreed model said links go both ways and are checked.

Both directions are shown and checked, but only one is stored, so the two copies cannot disagree; the reverse direction is never stored.
