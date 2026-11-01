---
id: d-9n3mad
kind: decision
title: "A disposable index speeds reads"
scope: product
decided_by: coordinator
date: 2026-11-01T02:30:45+01:00
changes:
  - {entry: s-gy0nsm, action: create}
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "1.6 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
  - {value: "1,600", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
  - {value: "17.6 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
  - {value: "16,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
  - {value: "900 s", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
  - {value: "160,000", handle: "docs/superpowers/plans/2026-10-31-lodge-at-scale/brief.md, evidence 3"}
---

lodge keeps a disposable index in the git common dir, never committed, one file per lodge build, that never changes what a read prints or what the gate decides; its entry rests on s-j8tp0n.

## Reasoning

Every read parsed every record file, so a read grew with the store: synthetic stores took about 1.6 s per read at 1,600 files, 17.6 s at 16,000, and more than 900 s at 160,000, measured before this plan's fixes.
A local SQLite file answers a read on a state seen before without parsing again, and needs no server (d-232gxs and d-hf2fms, confirmed by the author in d-4pbeax).
s-j8tp0n holds that files in git are the only source of truth and any index is disposable, so the index holds only what can be rebuilt from the files, and the gate and `add` never trust it (d-q0tb8r).
One file per lodge build keeps two builds on one machine from reading each other's rows (d-e3stjn).
