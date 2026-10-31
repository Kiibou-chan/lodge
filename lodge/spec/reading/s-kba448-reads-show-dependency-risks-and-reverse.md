---
id: s-kba448
kind: spec
title: "Reads show dependency risks and reverse links"
rests_on: [s-8f6scf, s-wcv4en]
---

Reads derive the reverse dependency relation, "supports".
Level 1 shows dependencies that are in doubt, retired, or changed after the entry's own last change, including "rests on s-xxxxxx, changed since".
Level 3 lists `rests_on` and `supports` in both directions.
