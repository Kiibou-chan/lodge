---
id: d-e8pdqe
kind: decision
title: "Search takes several queries, phrases, and codes first, with leaner brief lines"
scope: product
decided_by: coordinator
date: 2026-11-01T01:23:23+01:00
changes:
  - {entry: s-3n0ndk, action: edit}
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

`lodge search` takes several queries in one read, each record printed once across them; `--phrase` gives a phrase that matches as a run of whole words; a query that is a code lists the code's family and the records citing it before word matches; records holding every word rank above records holding some; and brief lines leave out the status current under the default filter, saying so once.

## Reasoning

Agents answering design questions through lodge ran several searches per shell call, each paying lodge's start-up and store read, and printed the same records again under each query.
Searching a code split it into words and matched hundreds of records holding a word of it, while the records the agent wanted were the code's siblings and the records citing it.
A quoted multi-word argument stays all its words, since a shell quote is not a phrase (d-ty4dks); `--phrase` is the explicit syntax (d-emtwbs).
The code rule is d-n9w4by's, the brief-line rule d-p60ka9's; this decision makes them the product's behaviour and edits the reading entry to say so.
Brief lines were the largest share of the text agents brought into context, and the status current on every line carried nothing under the default filter.
This is the second part of d-3g6ard built, after d-y94v0n; it neither replaces nor narrows d-fqymzm, whose one line per record still holds.
