---
id: d-shpxnq
kind: decision
title: "The specification page gets an outline and folding areas"
scope: product
decided_by: coordinator
date: 2026-10-31T10:00:52+01:00
changes:
  - {entry: s-2bzwzv, action: edit}
---

The viewer's specification page opens with a "Sections" outline of areas and their entries, and each area folds under its heading.

## Reasoning

The author asked for a section navigator and folding (d-fz8vy2); the page held every entry of every area open on one page with only a row of area links.
Folding uses the HTML `details` element, so the page still runs no script under the viewer's content security policy (`src/lodge/viewer/server.py`, `POLICY`).
Areas start open because a link to an entry inside a closed area does not open it in every browser, so the outline's links would otherwise land nowhere; the outline's per-area entry lists start folded, so the outline itself stays short.
The outline follows the order the page shows, so its links read top to bottom.
Cost if wrong: the defaults of two `open` attributes in `src/lodge/viewer/spec.py`.
