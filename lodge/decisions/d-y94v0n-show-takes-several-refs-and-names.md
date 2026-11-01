---
id: d-y94v0n
kind: decision
title: "Show takes several refs and names siblings and citers"
scope: product
decided_by: coordinator
date: 2026-11-01T01:09:49+01:00
changes:
  - {entry: s-3n0ndk, action: edit}
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

`lodge show REF...` takes several refs and prints them from one read, each record once, with a line naming each ref after the first; for a record with a code it lists the records in that code's family and the records citing the code, one brief line each, capped, with a count of those left out.

## Reasoning

Agents answering design questions through lodge looped `show` over several refs in the shell, paying lodge's start-up and store read once per ref, and a shell separator between records broke two of those loops.
They also searched a code to find its sibling records and the records citing it, which split the code into words and matched hundreds of unrelated records.
One call over several refs reads the store once; the separator line comes from lodge, so no shell loop is needed; siblings and citers come with the record, so no search for the code is needed.
A failing ref is reported in its place and the others still print, with the highest exit code among the failures, so one bad ref does not hide the rest.
One ref prints as before, plus the new sibling and citer lines.
This is the first part of d-3g6ard built; it neither replaces nor narrows it, d-fqymzm, or d-c08bdw, which still hold.
