---
id: d-s69cq4
kind: decision
title: "Confirm from the viewer with separate author records and explicit commits"
scope: product
decided_by: coordinator
date: 2026-10-31T03:02:42+01:00
changes:
  - {entry: s-arr325, action: create}
  - {entry: s-cecwv7, action: create}
  - {entry: s-hvsamx, action: create}
  - {entry: s-bhew59, action: create}
  - {entry: s-s4mkaj, action: create}
  - {entry: s-pbt1wj, action: create}
  - {entry: s-gxjwd9, action: create}
  - {entry: s-fwas5n, action: create}
  - {entry: s-mc9n8a, action: create}
  - {entry: s-bty9z4, action: create}
  - {entry: s-j9jc4y, action: create}
  - {entry: s-j5ttw1, action: edit}
  - {entry: s-bdkjte, action: edit}
  - {entry: s-sm2mf7, action: edit}
narrows: [d-mzkt6e]
---

Viewer confirmations are separate author decisions that preserve the confirmed decisions' writers.
Forms bind confirmation to displayed decisions, run the add checks, and redirect after writing.
The store commits each checkout viewer write by explicit path where safe, without pushing.

## Reasoning

The separate confirmation follows d-rnjh2s: reading and confirming cannot transfer authorship.
LODGE-6 (d-8nkamy) still makes a confirmed decision count as hers for the review flag; preserving `decided_by` does not weaken that consequence.
The s-j5ttw1 edit removes the obsolete blanket denial of a confirmation step, while preserving trust in the author label and visible provenance.
This narrows d-mzkt6e only in its entry's blanket denial, not in its review-flag rule or its refusal to require an inaccessible author identity check.
For advisor-marked claims, d-7w5aq0 requires listing every changed entry so the author sees the consequences, binding the write to the displayed IDs to avoid a stale confirmation, choosing scope independent of list order, redirecting to avoid repeated writes, preserving other staged work, using the checkout identity, and skipping commits during merge, rebase, or cherry-pick.
The generated title and statement, per-write checkout commit without pushing, staged fallback on the base branch or detached HEAD, and store-port boundary are coordinator calls.
Leaving a viewer write merely staged during normal checkout work risks unrelated commits or loss; an explicit-path commit isolates it, while the next session push carries it.
A partial commit during an in-progress git operation can fail, and the base branch takes only merges.
The required words and adjacent explanation let the author qualify what confirmation means without changing attribution.
Other related decisions remain current and are not superseded.

s-bdkjte clarifies that dependency freshness compares against the entry's own last change, avoiding a bare warning phrase in ordinary prose.
s-sm2mf7 still holds unchanged after that clarification: its dependency-following reading goal does not depend on the shorter wording.
