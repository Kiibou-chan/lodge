---
id: d-sdpcyb
kind: decision
title: "The import checks the store as a change from an empty state, then publishes it as its one owner"
scope: process
decided_by: planner
date: 2026-11-02T19:45:06+01:00
replaces: [d-ag8p8h, d-y42b7b]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "4", handle: "src/lodge/core/check_entries.py:73-84, the unlisted-source check"}
  - {value: "374", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 9"}
  - {value: "0", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 9"}
  - {value: "289", handle: "sed -n 289p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "79", handle: "sed -n 79p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "75", handle: "sed -n 75p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "304", handle: "sed -n 304p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "133", handle: "git show origin/server-core:ts/src/core/check-state.ts | sed -n 133p"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 6"}
---

The importer checks the store as a change from an empty state, with the store's own `.lodge.toml` read at a settings revision defaulting to the store's, then maps the author to the project's one owner and checks the mapped state the same way with the project's settings and owners, refusing there a path that is not UTF-8.
It imports into an empty project only, with one `publish` through the owner's store, IDs and dates as they are, writing no settings.

## Reasoning

d-ag8p8h ran lodge 0.2's state check with the store's settings, but the state check takes no settings (`checkState(s: Snapshot)`, `ts/src/core/check-state.ts:133` on `server-core`), and the unlisted-source problem is check 4 of a change, judged only for decisions new against the published state (`src/lodge/core/check_entries.py:73-84`); both plan reviews found this (B-1, P4-B1), and lodge 0.2's own `lodge check` prints `ok` on the made-up store with its `[import]` sources emptied.
Checked as a change from an empty state, every decision of the store is new, so the store's settings mean what they mean to `lodge add`: lodge 0.2's `check_change` from an empty state gives exactly check 4 for the imported decision with `sources = []`, nothing with the store's own sources, and nothing on this repository's 374 files of records, whose replaced, narrowed, and confirmed decisions raise no check 6, since the replaced status is derived from the empty published state (probe 9 of the plan's `probes.md`).
In lodge 0.2's branch mode the store's branch holds only `lodge/` and `.lodge.toml` sits on the base branch (`src/lodge/gitstore/branch.py:169`, `src/lodge/gitstore/settings.py:33-36`), so the settings need a revision of their own (correctness I-1, practice P4-I9).
The server checks every write as a change (design line 79), and after the import the project's settings judge each later add, so the mapped state is checked with them: a project whose settings do not list the store's sources fails there with check 4, as an add would; the owners are the people (d-vwsnz5), so an agent decision whose role is the owner's name reads as a person's decision without a quote and fails check 3.
A path holding an escaped byte is a name lodge 0.2 reads with `surrogateescape` but the events store refuses (d-pmaw3a), so the import refuses it as a problem with the other server problems rather than as `publish`'s error after both checks passed.
The importer keeps IDs and dates (design line 289), and `add` mints both, `--import` included (probe 6), so it publishes through the compare-and-set `add` uses after its own checks.
An import writes decisions and thread messages in a person's name, which only that person may do (design line 75, d-x6vaw8), so the requester must be the owner the author maps to and the store is that owner's; until build step 7 a project has one person (design line 304), so a project with several owners is refused rather than guessed at.
Cost if wrong: a store whose history a change check refuses, such as a decision dated after the server's clock, cannot move until fixed; a person who wants the store's sources must create the project with them.
