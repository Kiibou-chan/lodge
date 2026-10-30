---
id: d-fkndvh
kind: decision
title: "lodge is built in layers with one dependency direction"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:23+01:00
changes:
  - {entry: s-dffw9n, action: create}
  - {entry: s-t9zd7a, action: create}
  - {entry: s-q23m04, action: create}
  - {entry: s-nzhyh3, action: create}
  - {entry: s-ctywm6, action: create}
numbers:
  - {value: "2017", handle: "docs/superpowers/specs/2026-10-29-lodge-design.md:241"}
---

lodge is built as a pure core, an app layer of operations and ports, and adapters for git, the command line, the viewer, and the hook, wired in a composition root. Imports run one way, through front doors.

## Reasoning

The author required appropriate software development and design principles from the start, to avoid another long cleanup like the first user's, where enforcement came last after many import cycles and flat folders of over a hundred files.

The package proposals were drafted by an agent in the brainstorm and approved with the design.

The layering follows the dependency rule of clean architecture (Martin 2017).

The rule that `gitstore` is the only package touching git or the record files was amended by the author (LODGE-5): `cli` reads the draft files it is given, `cli` and `viewer` read their own package data, and `hook` reads its input, chosen over routing all of these through `gitstore`.

`core` takes the time and ID entropy as parameters, which is the first user's rule.
