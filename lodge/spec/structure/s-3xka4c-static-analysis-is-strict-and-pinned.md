---
id: s-3xka4c
kind: spec
title: "Static analysis is strict and pinned"
---

No code goes unused: Ruff's unused-import and unused-variable rules apply, and Vulture runs over the package with a pinned allow-list.
mypy runs in strict mode.
Ruff is the linter and formatter, with its configuration pinned in `pyproject.toml`.
