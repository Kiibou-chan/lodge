---
id: d-8kq2nk
kind: decision
title: "Checkout-mode state identity: HEAD's tree, git's differences, and a folder-signature cache"
scope: process
decided_by: planner
date: 2026-10-31T22:23:00+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
numbers:
  - {value: "159,716", handle: "find /var/tmp/lodge-bench/s90000/lodge -type f | wc -l"}
  - {value: "176 ms", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "175 to 184 ms", handle: "git -c core.untrackedCache=true status --porcelain -z -uall -- lodge, on a copy of s90000"}
  - {value: "85 ms", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "2,253", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "4.3 ms", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "45 ms", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "12 ms", handle: "uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/walk.py /var/tmp/lodge-bench/s90000"}
  - {value: "0.10 s", handle: "time python -c 'import lodge.main' from a native-disk venv with bytecode compiled"}
  - {value: "2 s", handle: "this decision's rule"}
---

In checkout mode a state's identity is the tree of `lodge/` at `HEAD`, plus the paths `git diff-index --cached HEAD` and `git diff-files` name, each read from disk and hashed, plus the files on disk that `HEAD` lacks, found through a cache of folder signatures (inode, mtime, ctime) under git's racy rule.
`git status` is not used.

## Reasoning

At 159,716 files (`probes/walk.py`): `git status --porcelain=v2 --untracked-files=all --ignored` 176 ms, git's untracked cache no faster (175 to 184 ms), a names-only walk 85 ms, `stat` of the 2,253 folders 4.3 ms, `git diff-files` 45 ms, `git diff-index --cached` 12 ms; with `import lodge.main` at 0.10 s, only the signature cache leaves room under 0.3 s.
A folder's ctime changes whenever an entry is added or removed and cannot be set back by tools, so a matching signature means the same names; a signature newer than the listing minus 2 s is not trusted.
Cost if wrong: a missed new file under `lodge/` would give a stale read; the tests in Task 11 cover creating, deleting, and renaming in a folder within the same second.
