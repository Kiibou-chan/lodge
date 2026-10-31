---
id: d-t22n7w
kind: decision
title: "The viewer-exemption minors R1 to R3 and the aliased datetime minor are still open"
scope: process
decided_by: coordinator
date: 2026-10-30T02:19:05+01:00
replaces: [d-226x4j]
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
---

The viewer-exemption minors R1 to R3 and the aliased `datetime` minor were not taken by the final fix wave and wait for the next code plan.

## Reasoning

Done ledger lines 41 to 44 hold the four minors, and line 45 deferred R1 to R3 to the final fix wave.
The wave's items (`docs/superpowers/plans/done/2026-10-29-lodge/final-wave-brief.md`) name none of them, and the ledger closes the wave at line 208.
The gap R1 names is still in `tests/structure_calls.py:161-165`: package data read in `viewer` is matched by name, so a write through `files(...)` is not seen.
