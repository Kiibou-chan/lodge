---
id: s-gy0nsm
kind: spec
title: "A disposable index speeds reads"
rests_on: [s-j8tp0n]
---

lodge keeps an index in the git common dir, never committed, one file per lodge build, holding parses keyed by path and git blob ID and the states reads have seen.
It never changes what a read prints or what the gate decides: the gate and `add` read the files themselves, and a read with the index switched off, missing, read-only, locked, or corrupt prints the same.
It is safe to delete at any time, and lodge rebuilds it as reads need it.
