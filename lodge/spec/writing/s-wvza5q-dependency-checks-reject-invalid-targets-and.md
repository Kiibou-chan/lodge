---
id: s-wvza5q
kind: spec
title: "Dependency checks reject invalid targets and cycles"
rests_on: [s-j70a0k, s-aw5a1j]
---

Check 2 refuses unresolved `rests_on` IDs and non-entry targets.
Check 8 refuses dependency cycles, since a cycle has no starting point.
Check 6 refuses an entry edited in the change that newly rests on a retired entry.
