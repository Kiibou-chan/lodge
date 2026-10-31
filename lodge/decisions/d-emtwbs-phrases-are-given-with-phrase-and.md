---
id: d-emtwbs
kind: decision
title: "Phrases are given with --phrase and match as runs of whole words"
scope: process
decided_by: planner
date: 2026-10-31T22:45:11+01:00
narrows: [d-eby5pb]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

`lodge search --phrase "words"` gives a phrase query, repeatable; a phrase matches a record whose title or statement holds its words as a contiguous run of word tokens (letters or digits, function words kept), compared lower-cased; a multi-word argument without `--phrase` is all its words.
A phrase or a code with no word outside the function words is searched in memory.

## Reasoning

The coordinator's ruling 5 asks for an explicit syntax; an option survives every shell, where quotes inside an argument need two kinds of quoting.
Whole-word runs make a phrase's words a sound candidate filter, which a substring is not (the correctness review's I5: `"ttled poi"`, `"of the"`).
Cost if wrong: one more option.
