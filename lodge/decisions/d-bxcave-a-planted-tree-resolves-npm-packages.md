---
id: d-bxcave
kind: decision
title: "A planted tree resolves npm packages as the repository does"
scope: process
decided_by: planner
date: 2026-11-02T15:17:31+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-core.md"
numbers:
  - {value: "18.6.0", handle: "grep -n dependency-cruiser docs/superpowers/plans/2026-11-02-lodge-server-core.md (Tech stack)"}
---

The structure tests' planted tree copies `ts/package.json`'s `dependencies` into its own `package.json`, and dependency-cruiser cruises it with `preserveSymlinks` on, so an npm import has the same resolved path and dependency type in a planted tree as in `ts/`.

## Reasoning

Without both, `yaml` imported in a planted tree resolves through the `node_modules` link to its real path outside the tree, with dependency type `npm-no-pkg`, while in an unplanted tree it resolves to `node_modules/yaml/dist/index.js` with type `npm`; with both, the planted tree gives the latter (`plan-fix-2-report.md`, probe of dependency-cruiser 18.6.0; `plan-recheck-1.md`, m2).
The other option, rules that match npm packages by module name alone, would work in both trees too, but leaves the planted tree differing from the repository, so a later rule keyed on a path or a type would again pass one and fail the other.
Cost if wrong: a planted tree with a package outside `dependencies` resolves it as `npm-no-pkg`, which the rule `core-imports` still refuses, since it allows only the two names of `CORE_NPM`.
