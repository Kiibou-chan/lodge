---
id: s-vg9y38
kind: spec
title: "Cloud replies appear through session stop reports"
rests_on: [s-anc255]
---

A cloud session receives messages through `claude -p "<message>" --cloud <id>`; replies appear in lodge only as it reports them through a hook at each stop.
Whether that hook can read its transcript is unverified.
