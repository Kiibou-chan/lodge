---
id: d-svv7gv
kind: decision
title: "The two-week age of a dependency holds for the packages it pulls in, from plan 3's install on"
scope: process
decided_by: planner
date: 2026-11-02T19:42:57+01:00
narrows: [d-4psbdv]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
numbers:
  - {value: "1209600", handle: "14 * 24 * 60 * 60, two weeks in seconds"}
  - {value: "14.0.3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, item 7"}
  - {value: "2.9.1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-7"}
  - {value: "2.11.1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-7"}
  - {value: "2.8.1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-7"}
  - {value: "2.11.0", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md, I-7"}
  - {value: "1.3.14", handle: "docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md, header"}
---

From the third plan's first task, `ts/bunfig.toml` sets `minimumReleaseAge = 1209600` under `[install]`, so `bun install` resolves every package, a dependency's own dependencies included, to a version published at least two weeks earlier.
The task checks each package version new in `ts/bun.lock` against its publication date and lists them in its ledger line.

## Reasoning

d-4psbdv's reason, time for a bad release to be noticed and pulled, holds for a package pulled in as much as for one named in `ts/package.json`.
@simplewebauthn/server 14.0.3 asks for its dependencies with caret ranges, and a plain install resolves `tslib` 2.9.1, published 2026-10-30, and the `@peculiar/asn1-*` packages at 2.11.1, published 2026-10-25; with the setting, Bun 1.3.14 resolves `tslib` 2.8.1 and `@peculiar/asn1-schema` 2.11.0, and both packages then work offline (`docs/superpowers/plans/2026-11-02-lodge-server-api/plan-review-practice.md`, I-7).
The setting lives in the repository, so every later install, a merge's included, keeps to it without anyone remembering the rule.
The packages the first plan locked are not checked here; that is the first plan's lock, and its coordinator's call.
Cost if wrong: a fix needed from a package younger than two weeks waits, or is named in `overrides` by the author's call.
