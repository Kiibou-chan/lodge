---
id: d-ag8p8h
kind: decision
title: "The import checks the store as lodge 0.2 does, then maps, into an empty project only"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "0.2", handle: "uv run --frozen --quiet lodge --version"}
  - {value: "79", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:79"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/probes.md, item 3"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1'"}
---

The importer runs lodge 0.2's state check on the store as read, with the settings of the store's own `.lodge.toml`, before it maps the author, and imports nothing when the check finds a problem or the project already holds a record.

## Reasoning

The check runs on every write and a failing write is refused with `lodge add`'s feedback (design line 79), so a store lodge 0.2 itself would refuse is refused before anything is written.
Imported records pass only when `.lodge.toml` lists their source (`tests/e2e/test_add_import.py`, `test_import_from_an_unlisted_source_fails_the_check`), so the check needs the store's own settings, which the reader takes from the same commit.
Checked after the mapping, lodge 0.2's check fails check 3 for every confirmation by a person (probe 3 of the plan's `probes.md`), so the 0.2 check runs on the store as read, and the server's own check runs on the mapped state when the events are written.
A move is done once per project and no project moves during build step 1 (d-2jk0mw), so an empty project is the only target, and merging a store into a project that holds records needs no rule now.
Cost if wrong: a store with a problem lodge 0.2 tolerated in its working tree but not in its published state cannot move until fixed, and importing into a non-empty project later needs a merge rule.
