---
id: s-t7wqxn
kind: spec
title: "Local session tokens end with the session and cloud tokens are shared"
rests_on: [s-8v6ek2, s-4w05xp]
---

Each local session gets its own token, scoped to its project and task and revoked when the session ends.
Cloud sessions share their environment's project token.
