---
id: d-1zmfdr
kind: decision
title: "The command sends the agent token from LODGE_TOKEN when it is set, and no token otherwise"
scope: process
decided_by: planner
date: 2026-11-02T19:42:54+01:00
replaces: [d-z1pncx]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "6", handle: "sed -n 49p docs/superpowers/specs/2026-11-02-lodge-server-design.md (must-not 6)"}
  - {value: "4", handle: "sed -n 299p docs/superpowers/specs/2026-11-02-lodge-server-design.md (build order, step 4)"}
---

The `lodge` command finds the root as the nearest folder at or above it holding `.git`, and reads the server's URL and project from `[server]` in `.lodge.toml` there.
It sends `LODGE_TOKEN` as `Authorization: Bearer` when set and not empty, and no `Authorization` otherwise, so a cloud environment's network secret can add the header on the way.
It uses `https`, or `http` only to this machine; `[store]` is an unknown section, and `[hook]` is left to the fourth plan's hook.

## Reasoning

d-z1pncx took a cloud session to hold lodge's token in its environment, but a network secret is a key Anthropic's proxy adds as a header to requests for the hosts it names, and "the session never sees the key" (`docs/research/2026-11-02-server-feasibility.md:43`).
The design keeps every secret out of a cloud environment's variables (`docs/superpowers/specs/2026-11-02-lodge-server-design.md:49`, must-not 6), gives a cloud environment lodge's project token as a network secret (`:192`), and has cloud sessions use the `lodge` command (`:213`); a command that stops when `LODGE_TOKEN` is unset cannot serve them (`docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-correctness.md`, I-8).
Without a token the server answers `unauthorised`, so a local run that forgot the variable still ends in one sentence, which names both places a token comes from.
The rest of d-z1pncx holds as it argued: the server goes beside the project's settings in `.lodge.toml` (`src/lodge/gitstore/settings.py:33-36`), the token stays out of the repository by must-not 6, `cli` may not spawn `git rev-parse` (`ts/tests/structure/calls.ts`, `process spawning outside git`), a bearer token over plain `http` to another machine can be read on the way, and `[store]` and `[hook]` mean nothing to the server's command (`src/lodge/core/settings.py:31-37`, `src/lodge/main.py:42-46`).
Which header the proxy adds, and whether it can be `Authorization: Bearer`, the research does not say; step 4 of the design's build order, which starts cloud sessions, checks it (`:299`).
Cost if wrong: if the proxy cannot add `Authorization: Bearer`, the server also reads the token from the header the proxy sets, one function in `ts/src/api/auth.ts`, and the command is unchanged.
