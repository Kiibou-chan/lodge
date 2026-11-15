---
id: s-yaz279
kind: spec
title: "Import changes only author attribution"
rests_on: [s-txrm4h, s-b6jxhr]
---

The importer maps each decision's `decided_by: author` and each thread message's `by: author` to the project's owner through the writers.
It refuses a source file that its writer does not reproduce byte for byte unchanged.
For a mapped thread, only the author attribution lines change; every other byte stays.
The export keeps the person's name.
