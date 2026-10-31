---
id: s-bty9z4
kind: spec
title: "The store owns viewer commits"
rests_on: [s-q23m04, s-nzhyh3]
---

Committing is an operation of the store port, implemented in `gitstore`, the only package that touches git.
In branch mode `add` already commits and pushes, and thread writes do the same.
