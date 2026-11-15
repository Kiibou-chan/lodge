---
id: d-sk1r7r
kind: decision
title: "The server model preserves records in append-only events"
scope: product
decided_by: coordinator
date: 2026-11-15T04:46:10+01:00
changes:
  - {entry: s-07ar34, action: edit}
  - {entry: s-z1zvb4, action: edit}
  - {entry: s-j8tp0n, action: edit}
  - {entry: s-31atpc, action: create}
  - {entry: s-ava922, action: create}
  - {entry: s-yenn11, action: create}
  - {entry: s-wb086g, action: create}
  - {entry: s-e5rrwm, action: create}
  - {entry: s-fabgyh, action: create}
  - {entry: s-g8m3qv, action: create}
  - {entry: s-tprwhs, action: create}
  - {entry: s-d1dd20, action: create}
  - {entry: s-8v6ek2, action: create}
  - {entry: s-cf0qph, action: create}
  - {entry: s-nfgv2t, action: create}
  - {entry: s-c0bd0b, action: create}
narrows: [d-cg3nn3, d-a3e8kb, d-zq5sfb]
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

The server holds records in append-only events, preserves their meaning, and makes accepted writes current immediately.
People approve decisions drafted in their names; tasks, workflows, sessions, artefacts, and waiting items enter at their named build steps.

## Reasoning

d-8kasej settles the server, d-d3js00 settles the append-only events table, and d-smx3xf settles the path and file bytes carried by record events.
The model preserves the meanings of the first design and the viewer design; immutability concerns decisions and event history, while specification entries retain their existing rewriting semantics.
d-zzfmj2 settles approval through the person, replacing trust in a label for the server.
The design marks named owners, confirmation by the deciding person, author mapping, write-time checking, and one-level task nesting as [my call].
Approval prevents an agent impersonating a person; identity-specific confirmation preserves who has authority to clear review flags.
The built import and export follow d-sdpcyb, d-83kt6y as narrowed by d-hg9qq9, and d-b61590.
Build steps come from the design's Build order, not from the existence of a model definition: task reporting is earlier than workflow execution, code views, and several-person roles.
d-cg3nn3 is narrowed only for no server and Kotlin as a future server candidate; its MCP exclusion for lodge 0.2 remains, and the viewer changes already settled by d-3d4g9j and d-dyrpc6 stand.
d-a3e8kb is narrowed only for files in git as the universal record store; lodge 0.2's files, header format, and checkout settings remain.
d-zq5sfb is also narrowed for git as the universal source of truth; public-repository and prose constraints remain.
