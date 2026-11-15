---
id: s-yaz279
kind: spec
title: "Import changes only author attribution"
rests_on: [s-txrm4h]
---

The importer maps each decision's `decided_by: author` and each thread message's `by: author` to the project's owner through the writers.
It refuses a decision or thread it would map if its writer does not reproduce the source byte for byte unchanged.
For a mapped thread, only the author attribution lines change; every other byte stays.
