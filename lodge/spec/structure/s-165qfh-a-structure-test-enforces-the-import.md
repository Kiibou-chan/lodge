---
id: s-165qfh
kind: spec
title: "A structure test enforces the import and size rules"
---

A structure test, written with the standard library's `ast`, enforces the rules from the first commit.
It checks the allowed-imports table, no import cycles between modules, imports across packages only through front doors, no module over about 300 lines, and no forbidden call in `core` (clock, randomness, `os`, `subprocess`, or `open`).
