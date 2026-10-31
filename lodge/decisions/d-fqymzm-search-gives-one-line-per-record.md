---
id: d-fqymzm
kind: decision
title: "Search gives one line per record with --brief"
scope: product
decided_by: coordinator
date: 2026-10-31T20:32:36+01:00
changes:
  - {entry: s-3n0ndk, action: edit}
numbers:
  - {value: "20", handle: "lodge search --help, the --limit default"}
  - {value: "1", handle: "s-3n0ndk, the name Level 1"}
---

`lodge search --brief` prints one line per record, its header and title, and the guide tells agents to search broadly with it, then show the records they need.

## Reasoning

In a measured comparison of an agent answering design questions from a store read through lodge against the same knowledge in Markdown files, every lodge run's first round of broad searches printed full Level 1 blocks, 20 per query, and overflowed the agent's inline tool output.
The agents then spent turns reading the overflow back from a file, or cut the output down themselves with `| grep '^s-'`, which keeps the ID line and drops the title.
One line per record gives the agent what it needs to choose what to show, in a fraction of the space.
The default stays Level 1 blocks, so existing callers and the viewer are unchanged.
