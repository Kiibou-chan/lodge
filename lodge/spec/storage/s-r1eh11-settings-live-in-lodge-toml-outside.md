---
id: s-r1eh11
kind: spec
title: "Settings live in .lodge.toml, outside the data"
---

Settings live in `.lodge.toml` at the root of the working checkout, not in the data.
They cover the store mode and branch, the length guidance, and the hook.
They sit outside the data because in branch mode lodge must know where the data is before it can read it.
