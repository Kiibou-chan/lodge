---
id: s-v1sb0j
kind: spec
title: "The environment is reproducible with uv"
---

Python 3.12 or later is required.
`pyproject.toml` and `uv.lock` are committed, so a fresh clone in a cloud session reproduces the environment with `uv sync`.
Runtime dependencies are kept to PyYAML, and the viewer uses the standard library's HTTP server.
