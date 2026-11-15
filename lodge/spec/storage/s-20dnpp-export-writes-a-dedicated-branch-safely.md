---
id: s-20dnpp
kind: spec
title: "Export writes a dedicated branch safely"
rests_on: [s-f6eaj1]
---

The export writes only a branch holding nothing outside `lodge/` that no work tree has checked out.
It builds commits through a temporary index, makes no commit when nothing changes, and pushes without force when a remote is named.
