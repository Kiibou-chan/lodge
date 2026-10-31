---
id: s-m4esa0
kind: spec
title: "Entries store the dependencies they require"
rests_on: [s-8f6scf]
---

An entry may list `rests_on: [s-xxxxxx, ...]`, naming only entries it would not hold without.
Adding or changing the list is an entry change made with a decision.
