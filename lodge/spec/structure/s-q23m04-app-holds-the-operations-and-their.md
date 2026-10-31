---
id: s-q23m04
kind: spec
title: "app holds the operations and their ports"
---

`lodge/app/` holds the operations (add, read, search, check, and render) and the ports they need.
The ports are Store, which gives the current and the published snapshot and writes, Clock, and IdSource.
