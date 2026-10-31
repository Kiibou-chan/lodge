---
id: d-3g6ard
kind: decision
title: "Leaner reads: several refs and queries per call, code families, phrases, and a reading guide"
scope: process
decided_by: coordinator
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "44 %", handle: "the brief, evidence item 5"}
  - {value: "5 to 11", handle: "the brief, evidence"}
  - {value: "700", handle: "the brief, evidence item 5"}
---

`show` takes several refs and `search` several queries in one call; a query that is a code returns its family and then the records citing it before word matches; a quoted phrase matches as a phrase and records with all words rank first; `show` names a record's sibling codes and citers; brief lines drop what is default; `lodge guide --read` gives a short guide for agents that only read.
Each is a product decision with its spec edit, made with `lodge add` on this branch.

## Reasoning

The brief for lodge at scale, ruling 4, binding on the plan, from a measured comparison of agents answering through lodge and through Markdown: brief search lines were about 44 % of the text agents read, agents looped over 5 to 11 refs per shell call, and a code query split into words matched about 700 records.
Cost if wrong: output changes agents must learn, told to them by the guide.
