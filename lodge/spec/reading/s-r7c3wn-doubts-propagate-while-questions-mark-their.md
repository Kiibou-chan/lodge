---
id: s-r7c3wn
kind: spec
title: "Doubts propagate while questions mark their record"
rests_on: [s-wcv4en]
---

An open doubt shows "in doubt" at level 1 in every read on its record and on entries that depend on it directly or transitively, as "rests on s-xxxxxx, in doubt".
A doubt on a decision marks the entries it created or last changed as "changed by d-xxxxxx, in doubt", and the entries resting on them, directly or further down, as "rests on s-xxxxxx, in doubt".
A question shows "question open"; nothing rests on a question.
