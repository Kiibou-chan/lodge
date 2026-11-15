---
id: s-myvb3j
kind: spec
title: "Cloud sessions start and receive follow-ups through claude"
rests_on: [s-7cseam, s-dazqbj, s-pks1qn]
---

From build step 4, a cloud session starts through `claude --cloud "<brief>"` in a pseudo-terminal; follow-ups use `claude -p "<message>" --cloud <id> --output-format json`.
