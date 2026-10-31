---
id: d-ty4dks
kind: decision
title: "Phrase search has its own syntax, and the guide's examples do what the code does"
scope: process
decided_by: coordinator
date: 2026-10-31T22:45:11+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A quoted shell argument is not a phrase; phrase search gets an explicit syntax, and the reading guide's examples match what the code does.

## Reasoning

The correctness review's I7: the shell removes the quotes, so `lodge search "berth crane"` reaches lodge as two words, and the guide would teach a phrase search that does not happen.
The coordinator's ruling 5 for the fix round.
Cost if wrong: one more option for agents to learn.
