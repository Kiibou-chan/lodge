---
id: d-n9w4by
kind: decision
title: "A code query is a single token with a family in the state; citers are matched in the level-1 text"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A search query is a code when it is one token of the code grammar and at least one record of the state has it as its code or as the start of its code followed by a dot; its family then lists first, the code itself, then the rest by code, then the records whose title or statement holds it as a whole token, newest first, then word matches.
`show` lists up to ten siblings and ten citers, one brief line each, then a line with the counts left out.

## Reasoning

Any other single word would change today's ranking for plain word searches, so code mode needs a family to exist.
Codes are `[A-Za-z0-9][A-Za-z0-9._-]*` (`src/lodge/core/fields.py`), so a whole token is bounded by characters outside that set, with a trailing sentence dot allowed; `X-10` and `X-1a` are not `X-1`, and `X-1.why` belongs to the family, not to the citers.
Search covers titles and statements (s-3n0ndk), so citers do too.
Cost if wrong: a citing record named only in a reasoning is missed, which `search` with words still finds.
