---
id: d-jch6c9
kind: decision
title: "Server safeguards preserve trust and human control"
scope: product
decided_by: coordinator
date: 2026-11-15T05:12:12+01:00
changes:
  - {entry: s-ydkmyq, action: create}
  - {entry: s-jqh7hf, action: create}
  - {entry: s-4w05xp, action: create}
  - {entry: s-xy6qte, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
---

The server preserves the existing must-nots and protects credentials, checked facts, secrets, and permission to merge.

## Reasoning

Must nots, lines 44 to 50, retain s-q4s548, s-pncjp8, and s-4ykcm0. The credential boundary follows the design's subscription and unmodified-client reasoning. Separating claims from checks protects against presenting reports as evidence; secret placement protects other people; merge permission retains human control. d-zzfmj2 enforces a person's authority over their decisions, and d-5ps72w approves the added safeguards. No claim is marked [my call]. These are permanent prohibitions rather than scheduled feature promises.
No other related decision is replaced or narrowed; looks-related feedback is answered no.
