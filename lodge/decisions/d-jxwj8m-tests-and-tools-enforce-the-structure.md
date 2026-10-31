---
id: d-jxwj8m
kind: decision
title: "Tests and tools enforce the structure from the first commit"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:23+01:00
changes:
  - {entry: s-165qfh, action: create}
  - {entry: s-3xka4c, action: create}
  - {entry: s-20ev8v, action: create}
  - {entry: s-v1sb0j, action: create}
numbers:
  - {value: "300 lines", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:261"}
  - {value: "Python 3.12", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:269"}
---

A structure test written with `ast`, strict typing, Ruff, Vulture, and test-first development with end-to-end tests enforce the structure from the first commit.
Python 3.12 or later and PyYAML are the environment.

## Reasoning

Enforcement comes first here because in the first user it came last.

The use of `ast` for the structure test, Vulture with a pinned allow-list, strict mypy, pytest, and the PyYAML-only dependency list were the specification author's calls.

The end-to-end tests use a temporary git repository with a bare remote so that pushing and a rejected push are exercised.

Committing `pyproject.toml` and `uv.lock` means a fresh clone in a cloud session reproduces the environment with `uv sync`.

The viewer uses the standard library's HTTP server, as an existing project's does.
