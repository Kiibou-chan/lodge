---
id: s-20dnpp
kind: spec
title: "Export writes a dedicated branch safely"
rests_on: [s-f6eaj1]
---

The export writes only a branch holding nothing outside `lodge/`.
For a local target, it refuses a branch checked out in any work tree.
When a remote is named, it does not check work trees and pushes without force.
It builds commits through a temporary index.
