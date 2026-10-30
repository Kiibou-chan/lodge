---
id: d-5mhgpp
kind: decision
title: "lodge's intent, goals, and success measures are specification entries"
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
---

lodge exists so that agents record and read a project's decisions and specification in one defined way, and the author browses them without a session. Its intent, its goals, and the six measures that judge the pilot become specification entries in the purpose area.

## Reasoning

The reasons the specification gives for building lodge at all are these.

Advisor rulings took the largest share of the first user's fresh Claude tokens, more than all review.

A ruling run is long and costly because the advisor rebuilds the case with `git show`, `sed`, and `grep` over long dated logs, and the cost tracks the number of calls, not the length of the prompt.

The logs grow without bound, with entries of tens of thousands of characters, few entries that say what they replace, and history leaking into the specification.

The author reaches decisions and rulings only through a session.

The author's framing was that decisions must be searchable and short, with their reasoning shortened too, and the full reasoning only available as a third step if needed.

She also wanted tooling that works on this knowledge effectively and constrains how it can be worked with and what can be done with it, which is why writing goes through one defined route.

On replacing the old files, her ruling was that the tooling takes their place, like any other knowledge kept in files in the project, rather than sitting beside them; a second copy would be the upkeep cost the third must-not names.

The cleanup the first user needed is the reason the structure rules come first rather than last.

The success measures were agreed after the design, each to be measured.

The baseline for rulings is measured on the first user, in fresh tokens, calls, and minutes per ruling, because those are the quantities the ruling runs were costly in.

The baseline for the third measure is that few entries in the first user's logs say what they replace.

The measure that agents actually use lodge, with no decision written anywhere else, was the one the author weighted most, and it is the reason the hook against writing elsewhere exists.
