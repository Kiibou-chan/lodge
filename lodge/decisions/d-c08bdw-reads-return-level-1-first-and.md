---
id: d-c08bdw
kind: decision
title: "Reads return Level 1 first, and the specification is rendered on demand"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:20+01:00
changes:
  - {entry: s-3n0ndk, action: create}
  - {entry: s-v022r0, action: create}
  - {entry: s-wz17sv, action: create}
  - {entry: s-7f10zc, action: create}
---

Search and show return Level 1, the readable specification is rendered on demand and not committed, reads state how fresh their data is, and agents learn the rules from a guide lodge prints.

## Reasoning

Level 1 first keeps reads cheap, and reasoning and provenance on request keeps the third step explicit.

The readable specification is rendered on demand because a committed copy would be a third copy, which the third must-not rules out.

A read states how fresh its data is when it comes from a shared branch, so the reader can judge whether it is current.

A project's `CLAUDE.md` points at the guide instead of copying it, so the rules live once, versioned with the tool.
