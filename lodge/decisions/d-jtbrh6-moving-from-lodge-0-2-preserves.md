---
id: d-jtbrh6
kind: decision
title: "Moving from lodge 0.2 preserves records and redirects advice"
scope: product
decided_by: coordinator
date: 2026-11-15T04:46:38+01:00
changes:
  - {entry: s-txrm4h, action: create}
  - {entry: s-5sgcxx, action: create}
  - {entry: s-yaz279, action: create}
  - {entry: s-3cagcv, action: create}
numbers:
  - {value: "1", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 1"}
  - {value: "2", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 2"}
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 3"}
  - {value: "4", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 4"}
  - {value: "5", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 5"}
  - {value: "6", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 6"}
  - {value: "7", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md, Build order, item 7"}
  - {value: "300", handle: "ts/tests/structure/, module-size rule"}
  - {value: "0.2", handle: "pyproject.toml, project.version"}
  - {value: "3.12", handle: "pyproject.toml, project.requires-python"}
  - {value: "1.3.14", handle: "ts/package.json, packageManager"}
---

The owner imports a lodge store from git into an empty server project after source and mapped-state checks.
Only author attribution changes, and the hook directs moved projects to the server.

## Reasoning

The Moving from lodge section preserves IDs, dates, codes, and imported provenance so a move does not rewrite knowledge.
d-sdpcyb requires checking changes from an empty state, with the source settings and then the project settings, before publishing through the owner.
d-83kt6y requires writer round trips before mapping; d-hg9qq9 narrows it so a thread changes only its author attribution lines and every other byte stays.
The mapping is the design's [my call], with named-person export settled by d-b61590.
d-va3j7x defines a moved project by its configured server, regardless of local storage mode, so edits to leftover copies do not masquerade as changes on the server.
Only the signed-in person may invoke import, as d-1skjw1 rules, and d-j5s0h0 joins the repository reader and settings reader.
No: d-sdpcyb and d-n9nm8h require the same change checks that these entries specify, and d-va3j7x supplies the moved-project boundary that the hook entry states.
None is replaced or narrowed.
