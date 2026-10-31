---
id: s-ctywm6
kind: spec
title: "Imports run one way, through front doors"
---

Imports follow the dependency rule of clean architecture (Martin 2017).
`app` imports `core`; `gitstore` imports `app` and `core`; `cli`, `viewer`, and `hook` import `app` and `core`; and `main.py` imports all.
Nothing imports `cli`, `viewer`, `hook`, or `gitstore` except `main.py`, and adapters never import each other.
Each package has one front door, its `__init__.py`, and other packages import only from it.
