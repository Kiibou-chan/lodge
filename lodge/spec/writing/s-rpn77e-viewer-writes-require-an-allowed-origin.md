---
id: s-rpn77e
kind: spec
title: "Viewer writes require an allowed origin"
rests_on: [s-704ssg]
---

Every viewer write must carry an `Origin` consisting of `http://` or `https://` followed by an allowed host.
A missing or foreign origin is refused.
