---
id: s-edgt71
kind: spec
title: "Reads run every check; only the gate and add refuse"
rests_on: [s-j70a0k, s-zv83s7]
---

Checks 4, 5, and 6 (entry without a decision, altered decision, and new link to a superseded record) compare the published state with the state about to be published.
Reads, the viewer, and `lodge check` run all seven against the published state, so a record that fails any check is shown as failing.
Only `lodge check --gate` and `lodge add` refuse (LODGE-9).
The check therefore takes two snapshots, and the Store port gives the current and the published snapshot, which a server can also give; no history beyond that is needed.
