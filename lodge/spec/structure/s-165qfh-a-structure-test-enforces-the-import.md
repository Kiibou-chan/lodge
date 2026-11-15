---
id: s-165qfh
kind: spec
title: "Structure tests enforce Python and TypeScript boundaries"
rests_on: [s-ctywm6, s-t9zd7a]
---

The Python structure test uses the standard library's `ast`.
The TypeScript structure tests use dependency-cruiser over the import graph and TypeScript's parser over calls.
They enforce allowed imports, no module cycles, cross-package imports through front doors, and modules of at most 300 lines.
`core` stays pure: time and randomness enter through ports, and clock, randomness, file, and network calls are refused.
