---
id: s-e5rrwm
kind: spec
title: "The server checks writes against its current state"
---

The check runs on every record write, and a failing write is refused with the feedback `lodge add` gives.
The server's current state takes the place of the published state of `lodge check --gate`.
