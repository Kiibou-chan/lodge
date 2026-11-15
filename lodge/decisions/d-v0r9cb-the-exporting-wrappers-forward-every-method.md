---
id: d-v0r9cb
kind: decision
title: "The exporting wrappers forward every method they do not change through a Proxy"
scope: process
decided_by: planner
date: 2026-11-02T19:45:06+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api.md on origin/server-api at 3e4c29c, Task 4 (Projects gains create's settings, settings, and names)"}
  - {value: "2", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md on origin/server-store at 61f87ad, Task 2 (Projects)"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Task 6"}
  - {value: "8", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import.md, Task 8"}
---

`exportingProjects(projects, written)` gives a `Proxy` over the project list whose `storeFor` wraps the store in a `Proxy` whose `publish` calls `written(project)` after a `PUBLISHED` answer; every other member reaches the inner object with its arguments as given, so a method a later plan adds needs no edit, and `written` is a function rather than the `Exporters` class.

## Reasoning

Plan 3 adds `settings` and `names` to `Projects` and a third parameter to `create` (plan 3 at 3e4c29c, Task 4), after Task 6 writes the wrapper against plan 2's interface; an object listing the methods fails `tsc` at plan 3's merge until Task 8 lands (correctness I-4), and a two-parameter `create` forwarder still type-checks against the three-parameter one and drops the project's settings (practice P4-I5, run with `tsc --strict`).
A `Proxy` forwards what it does not intercept with its arguments, so neither failure can happen and Task 8 edits nothing in `exporting.ts`; waiting for plan 3's Task 4 instead would hold the export lane until plan 2 is merged whole.
A recording function stands in for the exporter in the wrapper's tests, where a stand-in for a class with private members does not type-check (practice P4-M3).
Cost if wrong: a `Proxy` hides a method from `tsc`'s view only if the inner object lacks it, which the inner object's own type prevents; if a reviewer finds it opaque, the wrapper becomes a class listing every method and gains a line at each widening.
