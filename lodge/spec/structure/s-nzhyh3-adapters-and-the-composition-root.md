---
id: s-nzhyh3
kind: spec
title: "Adapters and the composition root"
---

`lodge/gitstore/` is the Store on files in git, and the only package that touches git or the record files, with these exceptions (LODGE-5): `cli` reads the draft files it is given, `cli` and `viewer` read their own package data, and `hook` reads its input.
`lodge/cli/` is the command line, `lodge/viewer/` the read-only web viewer, and `lodge/hook/` the Claude Code hook command.
`lodge/main.py` is the composition root, which wires the adapters to the app.
