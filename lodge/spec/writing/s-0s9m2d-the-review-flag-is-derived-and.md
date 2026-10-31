---
id: s-0s9m2d
kind: spec
title: "The review flag is derived and clears on confirmation"
rests_on: [s-01k42c, s-0yzshh]
---

The review flag is derived and never typed, so it cannot be forgotten.
It shows at Level 1 on the agent decision, on the decision or entry it touched, and in a viewer list of what waits for the author.
It clears when a later author decision names the flagged decision in `confirms` or `replaces`.
`lodge waiting` and the viewer show two groups: waiting for an agent contains open threads whose last message is the author's; waiting for the author contains flagged decisions and open threads whose last message is an agent's.
