---
id: d-5mhgpp
kind: decision
title: "lodge's intent, goals, and success measures"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:15+01:00
changes:
  - {entry: s-kcvh60, action: create}
  - {entry: s-m83kjq, action: create}
  - {entry: s-xx4pk4, action: create}
  - {entry: s-rx9d11, action: create}
  - {entry: s-3ht96p, action: create}
  - {entry: s-ph9z0t, action: create}
numbers:
  - {value: "tens of thousands of characters", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:18"}
---

lodge exists so that agents record and read a project's decisions and specification in one defined way, and the author browses them without a session.
Its goals are short, searchable, layered knowledge, one defined way to write it, and replacing the first user's files, and six measures judge the pilot.

## Reasoning

The reasons the specification gives for building lodge at all are these.

Advisor rulings took the largest share of the first user's fresh Claude tokens, more than all review.

A ruling run is long and costly because the advisor rebuilds the case with `git show`, `sed`, and `grep` over long dated logs, and the cost tracks the number of calls, not the length of the prompt.

The logs grow without bound, with entries of tens of thousands of characters, few entries that say what they replace, and history leaking into the specification.

The author reaches decisions and rulings only through a session.

The author's words on short, searchable decisions with the full reasoning as a further step are in d-n30kqr, and on tooling that constrains how knowledge is worked with in d-c6n1ng; the goals above are the specification's reading of them, which is why writing goes through one defined route.

On replacing the old files rather than sitting beside them, the author's words are in d-vzvfg2.

The structure rules come first rather than last because the first user's cleanup came after the fact; the author's requirement is in d-vxfdz7.

The six success measures were agreed with the author (d-9k0dfe), each to be measured.

The baseline for rulings is measured on the first user, in fresh tokens, calls, and minutes per ruling.

The baseline for the third measure is that few entries in the first user's logs say what they replace.

The measure that agents actually use lodge, with no decision written anywhere else, is the one the author called very important (d-9k0dfe); the hook against writing elsewhere serves it.
