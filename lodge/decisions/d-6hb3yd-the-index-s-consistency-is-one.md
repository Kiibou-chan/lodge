---
id: d-6hb3yd
kind: decision
title: "The index's consistency is one set of invariants, tested by fault injection"
scope: process
decided_by: coordinator
date: 2026-10-31T23:07:55+01:00
narrows: [d-her016]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The index's consistency findings are one class, settled by invariants in the plan, not one patch each.
A state row promises that every row it depends on is present; one transaction publishes a state with all those rows, behind a completeness marker; eviction removes everything only that state owns, in one transaction; a reader treats anything incomplete or inconsistent as a miss and takes the in-memory path.
Fault injection tests them (a write interrupted at each step, a concurrent writer, an eviction during a read), as does a revert in the property test.

## Reasoning

The rechecks found interrupted word writes leaving a searchable state without its words (the feasibility recheck's R1) and evicted words never coming back for a cached parse (the correctness recheck's N3), both from the same missing contract.
The coordinator's ruling for the second fix round.
Cost if wrong: more rows written per state, and reads that fall back to memory more often than needed.
