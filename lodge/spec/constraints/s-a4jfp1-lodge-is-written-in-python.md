---
id: s-a4jfp1
kind: spec
title: "Python lodge and the TypeScript server"
---

lodge 0.2 is written in Python.
The server, the runner, the interface, and the `lodge` command of the server design are written in TypeScript.
The command ships as a single binary built with `bun build --compile`; from build step 4, the runner ships the same way.
