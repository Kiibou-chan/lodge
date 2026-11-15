---
id: s-165qfh
kind: spec
title: "Structure tests enforce Python and TypeScript boundaries"
rests_on: [s-ctywm6, s-t9zd7a]
---

For lodge 0.2 in Python, the structure test uses the standard library's `ast` to enforce the allowed-imports table, no module cycles, cross-package imports through front doors, and modules of at most 300 lines; it forbids clock and randomness calls in `core` and `app`, and confines `os`, `subprocess`, and `open` I/O calls to the permitted I/O modules.
For the TypeScript server, the structure tests use dependency-cruiser over the import graph and TypeScript's parser over calls to enforce allowed imports, no module cycles, cross-package imports through front doors, and modules of at most 300 lines; `core` stays pure, with time and randomness entering through ports and clock, randomness, file, and network calls refused.
