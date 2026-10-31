---
id: d-jj72ps
kind: decision
title: "lodge runs as a command-line tool installed from a public tag in each session"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:16+01:00
changes:
  - {entry: s-az7rg4, action: create}
  - {entry: s-9n7han, action: create}
  - {entry: s-qkcp0s, action: create}
  - {entry: s-7m3smc, action: create}
numbers:
  - {value: "Python 3.13", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:72"}
---

lodge is a command-line tool that every session installs from a tag of its public repository.
The entries state what holds after the cloud check: a fresh session holding only the first user's project installs lodge, with the author's authorisation in the spawning prompt.

## Reasoning

The command-line route is settled: cloud sessions run lodge through Bash, with instructions in the project (`docs/superpowers/specs/2026-10-29-lodge-design.md:69`); the author's words on MCP servers are in d-14vk9b.

Installing from a tag of the public repository is LODGE-4 (d-y8p15p).

Every session installs lodge itself, because attaching lodge as a session repository does not reach the child sessions that the first user's coordinator starts, which get one repository each.

The specification first recorded two things as unchecked: whether the session proxy lets a session clone a public repository it does not hold, and whether instructions held in the repository or in a spawning session's prompt can authorise the install that auto mode blocks.

The cloud check settles the first and half of the second; its result is on line 221 of `docs/superpowers/plans/done/2026-10-29-lodge-progress.md`.

A fresh cloud session holding only the first user's project, run on Sonnet with the author's authorisation in its spawning prompt and no human message before it, ran `uv tool install` from the public tag and it succeeded and was not blocked.

The same session then ran `lodge --version`, `lodge guide`, and, in a scratch repository, `lodge init`, `lodge id s`, and `lodge check`, and all succeeded.

So the proxy does not stop the clone, the fallbacks of publishing lodge to PyPI or attaching it to each child session are not needed, and a spawning prompt that carries the authorisation is enough.

A `CLAUDE.md` line and a settings allow rule were not tested, which is why the entry says that is still open.

The image facts (Python 3.13, uv, which hosts answer, and the proxy scope) were checked in a cloud session of the first user on the day the specification was written.
