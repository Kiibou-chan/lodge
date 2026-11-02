---
id: d-bs5mm8
kind: decision
title: "The hook's settings parse in app, its context is built in cli, and main gives both the git functions"
scope: process
decided_by: planner
date: 2026-11-02T19:15:14+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at f2dcc72, Task 3"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at f2dcc72, Task 3"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "41", handle: "src/lodge/main.py:41-45"}
  - {value: "45", handle: "src/lodge/main.py:41-45"}
  - {value: "73", handle: "src/lodge/main.py:73-78"}
  - {value: "78", handle: "src/lodge/main.py:73-78"}
  - {value: "90", handle: "src/lodge/cli/parser.py:90"}
---

`parseHookSettings` lives in `app`, where the command's settings reader and the hook both reach it; `cli` builds the hook's context from `.lodge.toml`, given `git`'s `repoRootOf` and `isFolder`; the grammar takes `lodge hook EVENT` as lodge 0.2's does and runs it through a function of `Io` that the composition root builds.
The carried hook tests run in a real repository with store folders made by hand and no `[server]`, keeping lodge 0.2's assertions.

## Reasoning

Plan 1's import table lets `cli` and `hook` import only `app` and `core`, and only `main` imports `git` (`ts/tests/structure/table.ts:1-10` on `origin/server-core`), so neither the command nor the hook may call `git` themselves.
lodge 0.2 checks `[hook]` on every command and again in the hook's context (`src/lodge/main.py:41-45` and `:73-78`); with the check in `hook`, `cli` could not reach it, and `app` is the one package both import.
Plan 3's `readSettings` refuses `[store]` as an unknown section (plan 3 at f2dcc72, Task 3), and the hook must still read lodge 0.2's `[store] mode` for a project that has not moved, so the context reads the file leniently in `cli`, the package that holds smol-toml.
lodge 0.2 parses `hook EVENT` before argparse, so an unknown event exits 0 (`src/lodge/cli/parser.py:90`); the grammar keeps that.
Plan 3's test project writes `[server]` into every `.lodge.toml` and has a `.git` folder that is no repository (plan 3, Task 7a), but the carried tests run `git worktree add` and read branch mode, which a moved project ignores (d-va3j7x), so they get their own repository.
Cost if wrong: the hook's context moves to another package, a change of one file and its callers.
