---
id: d-t2dsd3
kind: decision
title: "A phrase lists its exact runs, then records with every word, then records with some"
scope: product
decided_by: coordinator
date: 2026-11-01T02:01:39+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

A `--phrase` query lists the records holding its words as a contiguous run first, then the records holding every word in another order, then the records holding some of the words, each group by score with ties newest first.

## Reasoning

As built from the plan's wording, a phrase listed its exact runs and then only the records holding some but not all of its words, so a record holding every word in another order was dropped: on lodge's own store, `search --phrase "lines brief"` listed records holding one of the two words and left out d-p60ka9 and d-e8pdqe, which hold both.
The plan meant the phrase's words to still find near matches below the exact ones (d-emtwbs), and a record holding every word is the nearest; d-e8pdqe already ranks records holding every word above records holding some for word queries, and a phrase now keeps that order below its exact runs.
The reading guide's sentence on `--phrase` says the same.
