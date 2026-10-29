---
id: d-ar0ker
kind: decision
code: LODGE-5
title: "Input and output outside the git store"
scope: process
decided_by: author
date: 2026-10-29T22:17:02+01:00
quote: {text: "A: amend the rule", where: "lodge brainstorm", when: "2026-10-29 14:52"}
---

`gitstore` is the only package that touches git or the record files.
`cli` reads the draft files it is given, `cli` and `viewer` read their own package data, and `hook` reads its input.

## Reasoning

A: amend the rule
