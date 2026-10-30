---
id: s-t9zd7a
kind: spec
title: "core is pure"
---

`lodge/core/` is pure: record kinds, parsing and writing the format, levels, the check, write feedback, search ranking, review flags, and rendering the specification.
It reads no clock, no randomness, no environment, no disk, and no network; the time and ID entropy come in as parameters.
