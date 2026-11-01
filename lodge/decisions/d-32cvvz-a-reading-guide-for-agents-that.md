---
id: d-32cvvz
kind: decision
title: "A reading guide for agents that only read"
scope: product
decided_by: coordinator
date: 2026-11-01T01:45:05+01:00
changes:
  - {entry: s-7f10zc, action: edit}
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

`lodge guide --read` prints a short guide for agents that only read: what lodge holds, the read commands with examples that run as written, and what the status words and flags mean, without the writing rules; the full guide points readers at it.

## Reasoning

Agents answering design questions through lodge read the full guide, whose writing rules they never used, at the start of every run.
Their wasted turns came from reads the guide did not show: unquoted multi-word queries rejected as usage errors, and shell loops over `show` broken by a separator line.
A reading guide whose examples show `show` with several refs, quoting, `--phrase`, and a code search gives those agents the commands that work, in fewer lines; the examples are tested to run, so the guide does what the code does (d-ty4dks).
This is the third part of d-3g6ard built, after d-y94v0n and d-e8pdqe.
