---
id: s-68mfam
kind: spec
title: "Workflow failures follow named back-edges"
rests_on: [s-tprwhs]
---

From build step 5, a workflow is a list of steps with named back-edges rather than a free graph.
Each step names where the task returns when its progression condition fails, such as a review with findings sending it to `fix`.
