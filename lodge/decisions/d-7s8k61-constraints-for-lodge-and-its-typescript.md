---
id: d-7s8k61
kind: decision
title: "Constraints for lodge and its TypeScript server"
scope: product
decided_by: coordinator
date: 2026-11-15T04:45:53+01:00
changes:
  - {entry: s-a4jfp1, action: edit}
  - {entry: s-v1sb0j, action: edit}
  - {entry: s-165qfh, action: edit}
  - {entry: s-3xka4c, action: edit}
  - {entry: s-sb9gee, action: create}
  - {entry: s-gcwv38, action: create}
  - {entry: s-5fd1qs, action: create}
  - {entry: s-7cseam, action: create}
  - {entry: s-t8sj11, action: create}
  - {entry: s-51ab7j, action: create}
narrows: [d-zq5sfb, d-jxwj8m]
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

lodge retains its Python environment alongside the TypeScript server environment.
The server design constrains storage, the interface, structure, testing, and cloud access.

## Reasoning

The Constraints section keeps the public-repository boundary already held by s-fk3yzy.
d-b1yjpp settles TypeScript, d-d3js00 settles SQLite behind a storage port, and d-ffk7wy settles Preact with signals.
The design marks dependency-graph enforcement as [my call]; the parser and dependency-cruiser enforce the carried structure rules, rather than trusting imports by convention.
The toolchain additions describe the built gate, with warnings failing under d-f18pz7.
The cloud terminal and shared-secret constraints follow the design's research: the runner needs a terminal, the server needs a reachable public name, and an environment token cannot identify an individual session.
The runner and full interface remain future build steps, as the Build order states.
The design does not assign Tailscale Funnel a separate build step; the entry states it as a deployment requirement.
d-zq5sfb is narrowed only for the claim that all lodge is Python; its public-repository and prose rules remain.
d-jxwj8m is narrowed only where the Python toolchain is presented as the whole environment; the Python rules remain.
