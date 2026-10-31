---
id: s-mc9n8a
kind: spec
title: "Unsafe checkout commits leave the write staged"
rests_on: [s-fwas5n]
---

The viewer writes and stages without committing on the configured base branch, which defaults to `main`, on a detached HEAD, or during a merge, rebase, cherry-pick, or revert, or while a sequence of picks or reverts is stopped.
The page says the write is staged and not committed.
If another process locks git's index, the viewer retries once after a second, then leaves the files staged and reports that.
