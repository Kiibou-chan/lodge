---
id: d-zq5sfb
kind: decision
title: "lodge is public, Python, file-based, and follows the author's prose rules"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:16+01:00
changes:
  - {entry: s-fk3yzy, action: create}
  - {entry: s-a4jfp1, action: create}
  - {entry: s-j8tp0n, action: create}
  - {entry: s-t9z0at, action: create}
---

lodge is public from its first commit, written in Python, keeps files in git as the only source of truth, keeps a project's knowledge in that project's repository, and writes record prose to the author's rules.

## Reasoning

Public from the first commit was the author's decision when she said she intended the tool to become public and chose public now over private until a first release; that decision changed the earlier choice of a private repository, because a private repository would have needed a setup script and token in the meantime.

The same decision is why code holds no personal paths or specifics of the first user, and why everything project-specific is in `.lodge.toml`.

Python was chosen because it is easily accessible; the author likes Kotlin, but judged it too much for now.

Files in git are the only source of truth, and any index is disposable, so there is nothing to keep in step; this was agreed with her.

Knowledge lives in the repository of the project it is about, and lodge is its own repository, both settled.

Record prose follows the author's invariants, which are British English, no em-dashes, an Oxford comma, and one sentence per line.
