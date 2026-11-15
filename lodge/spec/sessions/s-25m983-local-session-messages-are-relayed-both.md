---
id: s-25m983
kind: spec
title: "Local session messages are relayed both ways"
rests_on: [s-anc255]
---

The runner keeps a local session open as `claude -p --input-format stream-json --output-format stream-json` and relays messages both ways, allowing a mock to be worked on from a phone.
