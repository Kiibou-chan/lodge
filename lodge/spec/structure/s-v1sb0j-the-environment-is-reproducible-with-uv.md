---
id: s-v1sb0j
kind: spec
title: "Python and TypeScript environments are reproducible"
---

lodge 0.2 requires Python 3.12 or later.
`pyproject.toml` and `uv.lock` are committed, so a fresh clone reproduces the Python environment with `uv sync`.
Python runtime dependencies stay limited to PyYAML, and its viewer uses the standard library's HTTP server.
The TypeScript environment sits beside it: Bun 1.3.14 runs the server, tests, and tools, with dependencies pinned in `ts/package.json` and `ts/bun.lock`.
