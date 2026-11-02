---
id: d-y42b7b
kind: decision
title: "The import publishes the store's files through the project's store, by its one owner"
scope: process
decided_by: planner
date: 2026-11-02T19:07:50+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "289", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:289"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 6"}
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "79", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:79"}
  - {value: "75", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:75"}
  - {value: "304", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:304"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:302"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at c949ad9, \"Interfaces for plans 3 and 4\""}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at c8773bf, Calls made, item 4"}
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at c8773bf, Calls made, item 4"}
---

The import writes the mapped files, IDs and dates as they are, with one `publish` of the project's `Store`, after lodge 0.2's check of the store as read and the server's check of the mapped state with the project's settings and people; it goes not through `Lodge.add`, writes no settings, and is made by the project's one owner, to whom it maps the author.

## Reasoning

The importer keeps IDs and dates (design line 289), and `add` mints both for a new record, `--import` included (probe 6 of the plan's `probes.md`: lodge 0.2 minted `d-40q44p` for the imported draft), so the import cannot go through `Lodge.add` as plan 2's interfaces suppose (plan 2, "Interfaces for plans 3 and 4"); it publishes through the same compare-and-set port `add` uses, after the check, as plan 2 requires of every write (design line 79).
The server's check runs on the mapped state with the project's people, so the owner's decisions and messages read as a person's (plan 2, Task 10), and with the project's settings, which `lodge init` gives and build step 1 does not change (plan 3, RULE-SETTINGS, Calls made item 4); a store whose own `.lodge.toml` differs so that the check fails is refused with the check's problems.
An import writes decisions in a person's name, which only that person may do (design line 75), so the person importing must be the owner the author maps to; until build step 7 a project has one person (design line 304), so the one owner is the first, and a project with several owners is refused rather than guessed at.
Cost if wrong: a project with two owners before step 7 cannot import until the first owner is recorded; a second import path through `add` would be needed only if IDs were not kept.
