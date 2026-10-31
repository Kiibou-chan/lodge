---
id: s-6bc10p
kind: spec
title: "The git adapter reads a checkout or a branch"
---

The storage adapter reads and writes either the current checkout or a named branch kept in its own worktree.
It fetches before reads when the branch is stale, pushes after writes, and retries on a rejected push.
