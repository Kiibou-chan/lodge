---
id: s-bhew59
kind: spec
title: "A confirmation is a separate author decision"
rests_on: [s-aq3a5k, s-0yzshh]
---

A viewer confirmation writes an author decision with `confirms` naming the displayed decisions.
Its scope is `product` if any confirmed decision has that scope, and `process` otherwise.
Its quote contains the submitted words, `where: "lodge viewer"`, and the local time to the minute.
Its reasoning equals the submitted words.
