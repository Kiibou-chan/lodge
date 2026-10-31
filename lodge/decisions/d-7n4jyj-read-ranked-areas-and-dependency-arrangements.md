---
id: d-7n4jyj
kind: decision
title: "Read ranked areas and dependency arrangements"
scope: product
decided_by: coordinator
date: 2026-10-31T03:20:18+01:00
changes:
  - {entry: s-eb9kn7, action: create}
  - {entry: s-2bzwzv, action: create}
  - {entry: s-rh08jw, action: create}
  - {entry: s-v022r0, action: edit}
numbers:
  - {value: "116", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, line 116"}
  - {value: "122", handle: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md, line 122"}
---

The specification reads ranked areas and dependency arrangements while preserving the stored area order for checks.

## Reasoning

Design lines 116 to 122 implement the arrangement goals recorded by d-g7xvwm and d-s64jyh.
The coordinator adopts optional ranks, reading-only derived order, the two viewer choices, and dependency trees.
Advisor d-7w5aq0 supplies shared-rank feedback and the initial dependency view.
Advisor d-a3h9f3 resolves the tie and indent rule: dependants follow what they rest on, siblings in the area's order, with additional dependencies named rather than hidden by indentation.
The rank entry stands independently; the views and trees require the entry dependencies they list.
The on-demand rendering claim of d-c08bdw remains true, so no narrowing is needed.
d-qbfdqt and d-4dp4gm also remain current: read checks and the stored area-order check are preserved.
