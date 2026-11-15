---
id: s-51ab7j
kind: spec
title: "Cloud identity comes from a checked session ID"
rests_on: [s-pks1qn]
---

From build step 4, every cloud session in an environment presents the same project token, because a network secret belongs to the environment.
The session's identity comes from the session ID lodge gives it in its prompt, checked against the task it starts for, rather than from the shared token.
