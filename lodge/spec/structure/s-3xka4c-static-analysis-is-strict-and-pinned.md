---
id: s-3xka4c
kind: spec
title: "Static analysis is strict in both environments"
---

Python uses Ruff for linting and formatting, mypy in strict mode, and Vulture with a pinned allow-list; unused imports and variables fail the gate.
The TypeScript gate uses Biome for linting and formatting, `tsc` in strict mode, and knip for unused code.
Warnings fail the gate.
Configuration and dependencies are pinned in each environment.
