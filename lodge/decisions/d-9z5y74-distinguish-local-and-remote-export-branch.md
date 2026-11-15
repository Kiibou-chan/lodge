---
id: d-9z5y74
kind: decision
title: "Distinguish local and remote export branch checks"
scope: product
decided_by: coordinator
date: 2026-11-15T05:00:57+01:00
changes:
  - {entry: s-20dnpp, action: edit}
  - {entry: s-b4dtqk, action: edit}
narrows: [d-tnpe08]
numbers:
  - {value: "one commit a minute", handle: "ts/src/app/exporters.ts, EXPORT_INTERVAL_SECONDS = 60; d-sj6hmf, batching and retry interval"}
  - {value: "a minute", handle: "ts/src/app/exporters.ts, EXPORT_INTERVAL_SECONDS = 60, retry sleep"}
---

Export branch safety distinguishes a local target from a remote target.
The batching interval has its implementation handle.

## Reasoning

M2 states the lodge-only branch rule separately from the local-only work-tree refusal in ts/src/git/export.ts.
With a remote named, the exporter does not check work trees; it pushes without force.
The unchanged-tree claim appears only in s-b4dtqk, which is reaffirmed unchanged to supply the missing M1 interval handle.
The design marks batching as [my call]; d-sj6hmf settles retries and startup flushing, and EXPORT_INTERVAL_SECONDS implements the minute.
This narrows d-tnpe08 only for the scope of the work-tree check and its missing interval evidence; its one-way copy and named-person claims remain.
No: d-pv341r, d-sj6hmf, and author d-khew4n remain unchanged.
