---
id: d-z1pncx
kind: decision
title: "The command names its server and project in .lodge.toml and takes its token from LODGE_TOKEN"
scope: process
decided_by: planner
date: 2026-11-02T19:16:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Must nots, item 6"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
---

The `lodge` command finds the repository's root as the nearest folder at or above it holding `.git`, reads the server's URL and the project's name from `[server]` in `.lodge.toml` there, and takes the agent token from the environment variable `LODGE_TOKEN`.
It sends the token over `https`, or over `http` only to this machine.
`[store]` is an unknown section for it, and `[hook]` is left for the hook of the fourth plan to check.

## Reasoning

Plan 1's parity table says `init` "names the server and the project" (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`, the row of `tests/e2e/test_init.py`), and `.lodge.toml` already holds a project's settings in its repository (`src/lodge/gitstore/settings.py:33-36`), so the server goes beside them.
Must-not 6 forbids a secret in a repository or a URL (design, "Must nots"), so the token cannot sit in `.lodge.toml`; a cloud session holds lodge's project token as a network secret of its environment (design, "Starting"), which reaches the session's environment.
`cli` may not spawn a process (d-x6f9za; `ts/tests/structure/calls.ts`, `process spawning outside git`), so it cannot run `git rev-parse` as lodge 0.2 does (`src/lodge/gitstore/setup.py:17-24`); a `.git` folder, or a file in a worktree, marks the top of a working tree.
A bearer token over plain `http` to another machine can be read on the way, and the server's public name is an `https` Tailscale Funnel (design, "Constraints").
lodge 0.2's `parse_core_settings` refuses a section it does not know (`src/lodge/core/settings.py:31-37`), so one `.lodge.toml` cannot serve both lodge 0.2 and the server, and `[store]`, lodge 0.2's checkout or branch mode, means nothing to the server; lodge 0.2 checks `[hook]` on every command (`src/lodge/main.py:42-46`), and that check needs the hook package, which the fourth plan builds.
Cost if wrong: a repository nested inside another's folder finds the wrong root where `git rev-parse` would not; one function in `cli/settings.ts`.
