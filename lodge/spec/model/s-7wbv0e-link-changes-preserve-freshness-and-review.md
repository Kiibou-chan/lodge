---
id: s-7wbv0e
kind: spec
title: "Link changes preserve freshness and review state"
rests_on: [s-0yzshh, s-01k42c]
---

A decision changing only `rests_on` uses `link`; check 4 permits other alterations only when another decision of the same change lists the entry with `edit` or `create`.
A `link` raises no review flag and does not count as the entry's last change for "changed since", preserving warnings during dependency migration.
