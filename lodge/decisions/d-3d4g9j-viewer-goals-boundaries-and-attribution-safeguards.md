---
id: d-3d4g9j
kind: decision
title: "Viewer goals, boundaries, and attribution safeguards"
scope: product
decided_by: coordinator
date: 2026-10-31T03:02:19+01:00
changes:
  - {entry: s-648y95, action: create}
  - {entry: s-rbt13j, action: create}
  - {entry: s-bdkjte, action: create}
  - {entry: s-sm2mf7, action: create}
  - {entry: s-z2nb2t, action: create}
  - {entry: s-c8hrye, action: create}
  - {entry: s-bxqj2f, action: create}
  - {entry: s-9xwya5, action: create}
  - {entry: s-12ta2e, action: create}
  - {entry: s-ycx03c, action: create}
  - {entry: s-1cgvhe, action: create}
  - {entry: s-hfjr1m, action: edit}
narrows: [d-cg3nn3]
---

The viewer supports confirmation, record threads, and dependency-aware reading within explicit scope and attribution safeguards.
Existing must-nots continue to hold.

## Reasoning

The approved implementation now provides the interaction previously available only through a session, as motivated by the design's opening context.
The author decisions d-9dqycj, d-g7xvwm, d-s64jyh, d-1bnqj5, d-cvtrj6, and d-rnjh2s settle the quoted intent; d-dyrpc6 supplies confirmation intent, and d-2hcgav leaves editing for later.
The specific goals, the exclusion of live agent execution, the decision-link boundary, the configured-address boundary, and the operational safeguards are coordinator calls drawn from the design.
A live agent launched by a web page needs a separate security change; retaining the thread format avoids a later record migration.
For the advisor-marked attribution safeguard, d-7w5aq0 requires a separate author record with lodge-generated title and statement, so confirmation cannot misattribute agent prose.
The verbatim-form rule and decision-mediated changes preserve the existing must-nots.
s-hfjr1m still holds unchanged: the change to s-edgt71 does not alter the distinction between advisory feedback and a failing check refusing a write.
d-cg3nn3 is narrowed only where it calls the viewer read-only, since confirmation and threads now write from it.
Its other non-goals remain current; d-96n7j6 and d-1x1mgv are not superseded, since the unchanged feedback entry retains both its dependencies and advisory meaning.
