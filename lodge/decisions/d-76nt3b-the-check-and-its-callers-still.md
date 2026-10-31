---
id: d-76nt3b
kind: decision
title: "The check and its callers still hold with the Store port"
scope: product
decided_by: coordinator
date: 2026-10-31T03:08:15+01:00
changes:
  - {entry: s-edgt71, action: edit}
  - {entry: s-hfjr1m, action: edit}
  - {entry: s-pbt1wj, action: edit}
---

The check and its feedback and confirmation callers still hold with the Store port supplying the current and published snapshots.

## Reasoning

Task eight fix round one adds the required dependency from s-edgt71 to s-q23m04 through d-a16d4m.
The port definition in d-fkndvh is later than the check definition in d-4032xv, but its two snapshots are exactly what s-edgt71 already requires.
The unchanged statements of s-edgt71, s-hfjr1m, and s-pbt1wj remain valid together, so their edit actions acknowledge the dependency without changing their text.
This follows the guide's instruction to record an unchanged-text edit when an entry still holds after its dependency changes.
