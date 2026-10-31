---
id: s-fwas5n
kind: spec
title: "Each checkout viewer write commits its record paths"
rests_on: [s-6bc10p]
---

In checkout mode each viewer confirmation, new thread, reply, or closure commits its new or changed record files alone, by explicit path, without pushing.
Other staged files remain staged, as with `git commit --only`, and the commit uses the checkout's git identity.
The commit message names the operation, such as "Author confirmation from the viewer: d-xxxxxx" or "Thread q-xxxxxx: author reply".
Another worktree or cloud session sees the write only after the branch is pushed or merged.
