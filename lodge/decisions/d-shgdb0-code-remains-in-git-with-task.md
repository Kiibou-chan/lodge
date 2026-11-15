---
id: d-shgdb0
kind: decision
title: "Code remains in git with task views and authorised merges"
scope: product
decided_by: coordinator
date: 2026-11-15T05:40:36+01:00
changes:
  - {entry: s-dv5e12, action: create}
  - {entry: s-40yykh, action: create}
  - {entry: s-42kzcz, action: create}
  - {entry: s-5cs27z, action: create}
  - {entry: s-1k9wbc, action: create}
  - {entry: s-18jj1r, action: create}
  - {entry: s-p02emc, action: create}
  - {entry: s-9sjp9z, action: create}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:296-304, Build order and section content"}
  - {value: "one", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:250-256, Build order and section content"}
---

Code remains in git with task views and authorised merges.

## Reasoning

Source: docs/superpowers/specs/2026-11-02-lodge-server-design.md:250-256.
Git remains the code source on any host, while GitHub supplies pull requests and CI.
Decision identifiers provide bidirectional traceability without a second code store.
The existing s-nhx8zw holds GitHub integration scope; these entries add its connector behaviour.
Merging remains subject to s-xy6qte.

No other looks-related decision is replaced or narrowed.
