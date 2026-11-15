---
id: s-c0k9hx
kind: spec
title: "Workflow documents are versioned per task kind"
rests_on: [s-tprwhs]
---

From build step 5, a project has one workflow per kind of task, by default `plan` and `task`.
A workflow is a document lodge holds; each change is an event with who changes it and when, preserving process history.
