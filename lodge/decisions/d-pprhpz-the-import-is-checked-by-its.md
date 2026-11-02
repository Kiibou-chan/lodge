---
id: d-pprhpz
kind: decision
title: "The import is checked by its own state check, since it publishes through the store"
scope: process
decided_by: planner
date: 2026-11-02T19:09:32+01:00
narrows: [d-fv20kp]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "4", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1', plan 4"}
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
---

The store's `publish` runs no check of its own, so every path that calls it must check first: `app`'s writes run the change check, and plan 4's import, which publishes a lodge 0.2 store's files through the project's store rather than through `add`, runs lodge 0.2's state check on that store and imports into an empty project only.

## Reasoning

d-fv20kp argued that the importer goes through `add`; plan 4 instead publishes the files through the store by the project's one owner, since `add` mints new IDs and dates where the import keeps them (d-y42b7b, recorded on `server-import`).
Plan 4 checks the store as lodge 0.2 checks its published state before it maps anything, and refuses a project that already holds records (d-ag8p8h, recorded on `server-import`), so the import's state is checked as a whole, which is what the change check gives from an empty state.
A test that writes through `publish` directly stands for a hand edit of lodge 0.2, which plan 3's carried command tests need (its RULE-E2E).
Cost if wrong: a later caller of `publish` without a check writes an unchecked state, which reads then flag as failing, as lodge 0.2's reads flag a hand edit.
