---
id: d-h1f596
kind: decision
title: "The TypeScript code lives in ts/ beside lodge 0.2's Python"
scope: process
decided_by: planner
date: 2026-11-02T14:10:29+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "0.2", handle: "grep ^version pyproject.toml"}
---

The TypeScript code lives in `ts/` at the repository root, with its own `package.json`, `bun.lock`, configuration, `ts/src/<package>/`, and `ts/tests/<package>/`; lodge 0.2's `src/`, `tests/`, `pyproject.toml`, and `uv.lock` stay as they are until the last project has moved.

## Reasoning

The design keeps lodge 0.2 usable until a project has moved (design, "Moving from lodge 0.2"), so both codes live in one repository for a while.
A root `package.json` would share `src/` and `tests/` with Python, where `pyproject.toml` points Ruff, mypy, Vulture, and pytest (`src = ["src", "tests"]`, `files = ["src", "tests"]`, `testpaths = ["tests"]`), so each tool would need excludes for the other's files.
A second repository would split lodge's own records (`lodge/`) and history from the code they describe, against s-j8tp0n ("lodge is its own repository").
A folder named for the language says which code is which while both exist; when the Python goes, `git mv ts/* .` makes the TypeScript the root.
Cost if wrong: one `git mv` of the folder and its configuration paths.
